from typing import Dict, Any, AsyncGenerator, Tuple

from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_token_and_metadata(chunk: Any) -> Tuple[Any, Any]:
    """从chunk中提取token和metadata"""
    if isinstance(chunk, list):
        token = chunk[0]
        metadata = {} if len(chunk) < 2 else chunk[1]
    else:
        token, metadata = chunk
    return token, metadata


def serialize_metadata(metadata: Any) -> Dict[str, Any]:
    """序列化metadata"""
    try:
        if hasattr(metadata, 'items'):
            return metadata
        elif isinstance(metadata, list):
            logger.info(f"Metadata is list, length: {len(metadata)}")
            return {f'item_{i}': item for i, item in enumerate(metadata)}
        else:
            logger.warning(f"Unsupported metadata type: {type(metadata)}")
            return str(metadata)
    except Exception as e:
        logger.error(f"Error processing metadata: {str(e)}")
        return str(metadata)


async def process_message_chunk(namespace: str, chunk: Any) -> AsyncGenerator[Dict[str, Any], None]:
    """处理消息类型的chunk"""
    try:
        token, metadata = extract_token_and_metadata(chunk)
        content = token.content if hasattr(token, 'content') else str(token)

        if not content:
            logger.debug("Content is empty, skipping")
            return

        metadata = serialize_metadata(metadata)

        yield {
            "type": "token",
            "source": "subagent" if namespace else "main",
            "namespace": namespace,
            "content": content,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"Error processing message chunk: {str(e)}")
        content = str(chunk)
        if content:
            yield {
                "type": "token",
                "source": "subagent" if namespace else "main",
                "namespace": namespace,
                "content": content,
                "metadata": {}
            }


def process_update_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理更新类型的chunk"""
    return {
        "type": "update",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "data": chunk
    }


def process_custom_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理自定义事件类型的chunk"""
    return {
        "type": "custom",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "event": chunk
    }


def process_unknown_chunk(namespace: str, chunk: Any) -> Dict[str, Any]:
    """处理未知类型的chunk"""
    return {
        "type": "unknown",
        "source": "subagent" if namespace else "main",
        "namespace": namespace,
        "data": chunk
    }
