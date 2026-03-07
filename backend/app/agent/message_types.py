from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class MessageType(Enum):
    """消息类型枚举"""
    # 基础消息类型
    HUMAN = "human"  # 人类消息
    AI = "ai"        # AI消息
    TOOL_CALL = "tool_call"  # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    SYSTEM = "system"  # 系统消息
    ERROR = "error"    # 错误消息
    STREAMING = "streaming"  # 流式消息
    MESSAGE_DELTA = "message_delta"  # 消息增量
    MESSAGE_COMPLETE = "message_complete"  # 消息完成
    DONE = "done"      # 完成标记


class StreamMode(Enum):
    """流式模式枚举"""
    MESSAGES = "messages"  # 消息模式
    UPDATES = "updates"    # 更新模式
    CUSTOM = "custom"      # 自定义模式


@dataclass
class Message:
    """基础消息结构"""
    type: str
    content: str
    source: Optional[str] = None
    namespace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@dataclass
class ToolCallMessage(Message):
    """工具调用消息"""
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None


@dataclass
class ToolResultMessage(Message):
    """工具结果消息"""
    tool_name: Optional[str] = None
    tool_result: Optional[Any] = None


@dataclass
class StreamingMessage(Message):
    """流式消息"""
    data: Optional[Any] = None


@dataclass
class ErrorMessage(Message):
    """错误消息"""
    error: Optional[str] = None
    error_code: Optional[int] = None


@dataclass
class MessageDelta(Message):
    """消息增量"""
    message_id: Optional[str] = None
    accumulated_content: Optional[str] = None


@dataclass
class MessageComplete(Message):
    """消息完成"""
    chunk_count: Optional[int] = None


# 消息类型映射
MESSAGE_TYPE_MAP = {
    MessageType.HUMAN.value: Message,
    MessageType.AI.value: Message,
    MessageType.TOOL_CALL.value: ToolCallMessage,
    MessageType.TOOL_RESULT.value: ToolResultMessage,
    MessageType.SYSTEM.value: Message,
    MessageType.ERROR.value: ErrorMessage,
    MessageType.STREAMING.value: StreamingMessage,
    MessageType.MESSAGE_DELTA.value: MessageDelta,
    MessageType.MESSAGE_COMPLETE.value: MessageComplete,
}


def get_message_class(message_type: str):
    """根据消息类型获取对应的消息类"""
    return MESSAGE_TYPE_MAP.get(message_type, Message)


def create_message(message_type: str, **kwargs) -> Message:
    """创建消息实例"""
    message_class = get_message_class(message_type)
    return message_class(type=message_type, **kwargs)
