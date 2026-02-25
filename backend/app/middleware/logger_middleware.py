from typing import Any, Dict, Callable
from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.middleware.todo import PlanningState
from langchain.agents.middleware import AgentState
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from app.utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

class LoggerMiddleware(AgentMiddleware):
    """Combined logger middleware that logs tool calls, todo lists, and agent messages."""

    def wrap_tool_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Log tool calls before and after execution.

        Args:
            request: Tool call request to execute.
            handler: Callback that executes the tool call and returns the response.

        Returns:
            The tool call response.
        """
        # Log tool call details
        logger.debug(f"============*** Start Tool Call ***============")
        
        # Check if there are todos in the tool call arguments
        if hasattr(request, 'tool_call') and 'args' in request.tool_call:
            args = request.tool_call['args']
            tool_name = request.tool_call['name']
            logger.debug(f"Tool name: {tool_name} | Arguments: {args if args else 'N/A'}")
        else:
            tool_name = request.tool_call['name'] if hasattr(request, 'tool_call') else str(request)
            logger.debug(f"Tool name: {tool_name}  >>>>>  Arguments: N/A")

        # Execute the tool call
        result = handler(request)

        if result and hasattr(result, 'update'):
            self._log_todos(result.update['todos'])
        # Log the result
        logger.debug(f"Result: {result if result else 'No result'}")
        logger.debug("============*** End Tool Call ***=============")

        return result
    

    def before_model(
        self, state: PlanningState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Log information before model execution.

        Args:
            state: The current agent state before model execution.
            runtime: The LangGraph runtime instance.

        Returns:
            None to allow normal execution.
        """
        pass

    def wrap_model_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Log model calls before and after execution.

        Args:
            request: Model request to execute.
            handler: Callback that executes the model request and returns the response.

        Returns:
            The model call response.
        """
        logger.debug("=========*** wrap_model_call ***============")
        
        logger.debug(f"Number of messages in request: {len(request.messages or [])}")
        
        # Execute the model call
        logger.debug("Executing model call...")
        response = handler(request)

        # Log response information
        logger.debug("Model call completed")
        if hasattr(response, 'result'):
            result = getattr(response, 'result', '')
            if result:
                truncated_result = result[:200] + "..." if len(result) > 200 else result
                logger.debug(f"Response result: {truncated_result}")
        elif hasattr(response, 'messages'):
            logger.debug(f"Number of messages in response: {len(response.messages)}")
        
        logger.debug("=========*** wrap_model_call End ***============")
        return response

    def after_model(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Log the todo list and agent messages after model execution.

        Args:
            state: The current agent state containing messages and todos.
            runtime: The LangGraph runtime instance.

        Returns:
            None to allow normal execution.
        """
        logger.debug("==========*** after_model Execution ***==========")
        logger.debug("==========*** after_model Execution End ***==========")
        return None

    def _log_todos(self, todos):
        """Log todo list with enhanced formatting.

        Args:
            todos: List of todo items to log.
        """
        if not todos:
            return
        
        # Log the todos
        logger.debug("====== Todo List ======")
        for i, todo in enumerate(todos, 1):
            # Use different log levels based on todo status for better visibility
            status = todo['status']
            content = todo['content']
            
            if status == "completed":
                logger.info(f"{i}. ✅ [COMPLETED] {content}")
            elif status == "in_progress":
                logger.info(f"{i}. 🔄 [IN PROGRESS] {content}")
            else:  # pending
                logger.info(f"{i}. ⏳ [PENDING] {content}")
        logger.debug("====== Todo List End ======")
