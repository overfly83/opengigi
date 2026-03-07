import json
from typing import Any, Dict, Callable
from datetime import datetime
from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.middleware import AgentState
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.store.sqlite.aio import AsyncSqliteStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryMiddleware(AgentMiddleware):
    """Middleware that automatically saves conversation history to memory."""
    
    def __init__(self, sqlite_store: AsyncSqliteStore):
        super().__init__()
        self.sqlite_store = sqlite_store
        self.current_user_id = 'user1'
        self.current_thread_id = ''
        logger.info("MemoryMiddleware initialized with AsyncSqliteStore")
    
    def _capture_config(self, obj: Any, source: str = "unknown"):
        """Try to capture user_id and thread_id from runtime.context only."""
        try:
            # Only get from runtime.context (as specified by user)
            if hasattr(obj, 'context'):
                context = obj.context
                if hasattr(context, 'user_id') and hasattr(context, 'thread_id'):
                    user_id = context.user_id
                    thread_id = context.thread_id
                    if user_id or thread_id:
                        self.current_user_id = user_id
                        self.current_thread_id = thread_id
                        logger.debug(f"Captured from {source} (context) - user_id: {self.current_user_id}, thread_id: {self.current_thread_id}")
                        return
            
        except Exception as e:
            logger.debug(f"Error capturing config from {source}: {e}")
    
    def wrap_model_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Wrap model call to capture user_id and thread_id from request."""
        # Execute the model call
        return handler(request)

    async def awrap_model_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Wrap model call to capture user_id and thread_id from request (async)."""
        # Execute the model call
        return await handler(request)
    
    def wrap_tool_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Wrap tool call to capture user_id and thread_id from request."""
        # Execute the tool call
        return handler(request)

    async def awrap_tool_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Wrap tool call to capture user_id and thread_id from request (async)."""
        # Execute the tool call
        return await handler(request)
    
    def before_model(
        self, state: Any, runtime: Runtime
    ) -> Any | None:
        """Before model execution - capture config from runtime."""
        self._capture_config(runtime, "before_model")
        return None

    async def abefore_model(
        self, state: Any, runtime: Runtime
    ) -> Any | None:
        """Before model execution - capture config from runtime (async)."""
        self._capture_config(runtime, "abefore_model")
        return None
    
    def _serialize_message(self, message: Any) -> dict:
        """Serialize a message to a dictionary."""
        if isinstance(message, HumanMessage):
            return {
                'type': 'human',
                'content': message.content,
                'timestamp': datetime.now().isoformat()
            }
        elif isinstance(message, AIMessage):
            # Use message.content instead of content_blocks to avoid [object Object] in frontend
            content = message.content if hasattr(message, 'content') and message.content else str(message.content_blocks)
            return {
                'type': 'ai',
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
        elif isinstance(message, ToolMessage):
            return {
                'type': 'tool',
                'content': message.content,
                'tool_name': message.name,
                'timestamp': datetime.now().isoformat()
            }
        return {
            'type': 'unknown',
            'content': str(message),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _save_conversation_history(self, messages: list):
        """Save conversation history to memory store with thread_id support."""
        try:
            user_id = self.current_user_id
            thread_id = self.current_thread_id
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            if not thread_id:
                logger.debug(f"No thread_id available, skipping save")
                return
            
            # Serialize messages
            serialized_messages = [self._serialize_message(msg) for msg in messages]
            
            # Commit any pending transaction
            try:
                await self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            # Import storage functions
            from app.agent import storage
            
            # Get existing thread
            existing_thread = await storage.get_thread_history(self.sqlite_store, user_id, thread_id)
            
            if existing_thread:
                # Update existing thread
                existing_thread['date'] = date_str
                existing_thread['messages'] = serialized_messages
                existing_thread['updated_at'] = datetime.now().isoformat()
                await storage.save_thread_history(self.sqlite_store, user_id, existing_thread)
            else:
                # Create new thread
                new_thread = {
                    'thread_id': thread_id,
                    'date': date_str,
                    'messages': serialized_messages,
                    'updated_at': datetime.now().isoformat()
                }
                await storage.save_thread_history(self.sqlite_store, user_id, new_thread)
                await storage.add_thread_to_index(self.sqlite_store, user_id, thread_id)
            logger.info(f"Saved conversation history for user: {user_id}, thread: {thread_id}")
            logger.debug(f"Conversation saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}", exc_info=True)
    
    def after_model(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Save conversation history after model execution (sync).
        
        Args:
            state: The current agent state containing messages and todos.
            runtime: The LangGraph runtime instance.
            
        Returns:
            None to allow normal execution.
        """
        # For sync version, we can't use async operations
        return None

    async def aafter_model(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Save conversation history after model execution (async).
        
        Args:
            state: The current agent state containing messages and todos.
            runtime: The LangGraph runtime instance.
            
        Returns:
            None to allow normal execution.
        """
        try:
            logger.debug("MemoryMiddleware: aafter_model called")
            
            # Get messages from state if it exists
            messages = state.get('messages', []) if 'messages' in state else []
            if messages:
                logger.debug(f"Saving conversation history with {len(messages)} messages")
                await self._save_conversation_history(messages)
            
        except Exception as e:
            logger.error(f"Error in MemoryMiddleware.aafter_model: {e}", exc_info=True)
        
        return None

    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Before agent execution - capture config from runtime."""
        self._capture_config(runtime, "before_agent")
        return None

    async def abefore_agent(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Before agent execution - capture config from runtime (async)."""
        self._capture_config(runtime, "abefore_agent")
        return None

    def after_agent(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """After agent execution."""
        return None

    async def aafter_agent(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """After agent execution (async)."""
        return None
