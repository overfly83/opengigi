from typing import Dict, Any, AsyncGenerator, Callable
from abc import ABC, abstractmethod
from app.agent.message_types import MessageType, Message, create_message
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MessageProcessor(ABC):
    """消息处理器抽象基类"""
    
    @abstractmethod
    async def process(self, namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
        """处理消息"""
        pass


class MessageChunkProcessor(MessageProcessor):
    """消息类型的chunk处理器"""
    
    async def process(self, namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            # 提取token和metadata
            if isinstance(chunk, list):
                token = chunk[0]
                metadata = {} if len(chunk) < 2 else chunk[1]
            else:
                token, metadata = chunk
            
            content = token.content if hasattr(token, 'content') else str(token)
            
            if not content:
                logger.debug("Content is empty, skipping")
                return
            
            # 序列化metadata
            if hasattr(metadata, 'items'):
                serial_metadata = metadata
            elif isinstance(metadata, list):
                logger.info(f"Metadata is list, length: {len(metadata)}")
                serial_metadata = {f'item_{i}': item for i, item in enumerate(metadata)}
            else:
                logger.warning(f"Unsupported metadata type: {type(metadata)}")
                serial_metadata = str(metadata)
            
            message = create_message(
                MessageType.AI.value,
                content=content,
                source="subagent" if namespace else "main",
                namespace=namespace,
                metadata=serial_metadata
            )
            
            yield message.__dict__
            
        except Exception as e:
            logger.error(f"Error processing message chunk: {str(e)}")
            content = str(chunk)
            if content:
                error_message = create_message(
                    MessageType.ERROR.value,
                    content=content,
                    source="subagent" if namespace else "main",
                    namespace=namespace,
                    metadata={},
                    error=str(e)
                )
                yield error_message.__dict__


class UpdateChunkProcessor(MessageProcessor):
    """更新类型的chunk处理器"""
    
    async def process(self, namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
        # 检查是否包含工具调用
        if chunk and isinstance(chunk, dict):
            if 'tool_calls' in chunk:
                tool_call_message = create_message(
                    MessageType.TOOL_CALL.value,
                    content=str(chunk['tool_calls']),
                    source="subagent" if namespace else "main",
                    namespace=namespace,
                    tool_args=chunk['tool_calls']
                )
                yield tool_call_message.__dict__
            elif 'tool_result' in chunk:
                tool_result_message = create_message(
                    MessageType.TOOL_RESULT.value,
                    content=str(chunk['tool_result']),
                    source="subagent" if namespace else "main",
                    namespace=namespace,
                    tool_result=chunk['tool_result']
                )
                yield tool_result_message.__dict__
            else:
                streaming_message = create_message(
                    MessageType.STREAMING.value,
                    content=str(chunk),
                    source="subagent" if namespace else "main",
                    namespace=namespace,
                    data=chunk
                )
                yield streaming_message.__dict__
        else:
            streaming_message = create_message(
                MessageType.STREAMING.value,
                content=str(chunk),
                source="subagent" if namespace else "main",
                namespace=namespace,
                data=chunk
            )
            yield streaming_message.__dict__


class CustomChunkProcessor(MessageProcessor):
    """自定义事件类型的chunk处理器"""
    
    async def process(self, namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
        system_message = create_message(
            MessageType.SYSTEM.value,
            content=str(chunk),
            source="subagent" if namespace else "main",
            namespace=namespace
        )
        yield system_message.__dict__


class UnknownChunkProcessor(MessageProcessor):
    """未知类型的chunk处理器"""
    
    async def process(self, namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
        error_message = create_message(
            MessageType.ERROR.value,
            content=str(chunk),
            source="subagent" if namespace else "main",
            namespace=namespace,
            data=chunk
        )
        yield error_message.__dict__


class MessageProcessorFactory:
    """消息处理器工厂"""
    
    def __init__(self):
        self._processors = {
            "messages": MessageChunkProcessor(),
            "updates": UpdateChunkProcessor(),
            "custom": CustomChunkProcessor(),
            "unknown": UnknownChunkProcessor()
        }
    
    def get_processor(self, stream_mode: str) -> MessageProcessor:
        """根据流模式获取处理器"""
        return self._processors.get(stream_mode, self._processors["unknown"])


# 创建全局消息处理器工厂实例
message_processor_factory = MessageProcessorFactory()


def get_message_processor(stream_mode: str) -> MessageProcessor:
    """获取消息处理器"""
    return message_processor_factory.get_processor(stream_mode)
