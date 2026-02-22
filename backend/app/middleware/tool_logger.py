import os
from langchain.agents.middleware import wrap_tool_call
from app.utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

@wrap_tool_call
def log_tool_calls(request, handler):
    """Intercept and log every tool call - demonstrates cross-cutting concern."""

    tool_name = request.name if hasattr(request, 'name') else str(request)

    logger.info(f"Tool call #: {tool_name}")
    logger.info(f"Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")

    # Execute the tool call
    result = handler(request)

    # Log the result
    logger.info(f"Tool call #{tool_name} completed")

    return result