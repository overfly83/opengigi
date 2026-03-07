from typing import Dict, Any, AsyncGenerator
import json
from app.utils.logger import get_logger
from app.agent.message_processor import get_message_processor
from app.agent.message_types import MessageType

logger = get_logger(__name__)


def ensure_serializable(obj):
    """递归处理对象，确保可以被JSON序列化"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, dict):
        return {k: ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # 处理对象实例
        try:
            return ensure_serializable(obj.__dict__)
        except Exception:
            # 如果无法序列化__dict__，尝试转换为字符串
            return str(obj)
    elif hasattr(obj, 'dict'):
        # 处理Pydantic模型
        try:
            return ensure_serializable(obj.dict())
        except Exception:
            return str(obj)
    elif hasattr(obj, 'asdict'):
        # 处理dataclass
        try:
            return ensure_serializable(obj.asdict())
        except Exception:
            return str(obj)
    else:
        # 如果是其他不可序列化类型，转换为字符串
        return str(obj)


async def process_message_chunk(namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
    """处理消息类型的chunk"""
    processor = get_message_processor("messages")
    async for result in processor.process(namespace, chunk):
        yield result


async def process_update_chunk_async(namespace: str, chunk: Any) -> Dict[str, Any]:
    """异步处理更新类型的chunk"""
    processor = get_message_processor("updates")
    results = []
    async for result in processor.process(namespace, chunk):
        results.append(result)
    return results[0] if results else {}


def process_update_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理更新类型的chunk"""
    # 直接处理，不使用异步生成器
    if chunk and isinstance(chunk, dict):
        if 'tool_calls' in chunk:
            return {
                "type": "tool_call",
                "source": "subagent" if namespace else "main",
                "namespace": namespace,
                "content": str(chunk['tool_calls']),
                "data": chunk
            }
        elif 'tool_result' in chunk:
            return {
                "type": "tool_result",
                "source": "subagent" if namespace else "main",
                "namespace": namespace,
                "content": str(chunk['tool_result']),
                "data": chunk
            }
    return {
        "type": "streaming",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "data": chunk
    }


def process_custom_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理自定义事件类型的chunk"""
    return {
        "type": "system",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "content": str(chunk),
        "event": chunk
    }


def process_unknown_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理未知类型的chunk"""
    return {
        "type": "error",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "content": str(chunk),
        "data": chunk
    }


async def process_async_generator(generator: AsyncGenerator[Dict[str, Any], None]) -> list:
    """处理异步生成器，返回结果列表"""
    results = []
    async for item in generator:
        results.append(item)
    return results


# 记录SSE事件的辅助函数
def log_sse_event(event_type, event_data):
    """记录SSE事件并返回格式化的事件字符串"""
    logger.debug(f"[SSE→Client] type={event_type} | {json.dumps(event_data)[:200]}...")
    return f"data: {json.dumps(event_data)}\n\n"


def create_error_event(error: Exception) -> str:
    """创建错误事件"""
    error_data = {
        'error': str(error),
        'message': 'An error occurred during streaming'
    }
    return log_sse_event(MessageType.ERROR.value, error_data)


def create_message_delta_event(message_id: str, content: str, accumulated_content: str) -> str:
    """创建消息增量事件"""
    delta_data = {
        'id': message_id,
        'content': content,
        'accumulated_content': accumulated_content
    }
    return log_sse_event(MessageType.MESSAGE_DELTA.value, delta_data)


def create_message_complete_event(content: str, chunk_count: int) -> str:
    """创建消息完成事件"""
    complete_data = {
        'content': content,
        'chunk_count': chunk_count
    }
    return log_sse_event(MessageType.MESSAGE_COMPLETE.value, complete_data)
