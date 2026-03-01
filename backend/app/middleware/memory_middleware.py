import json
from typing import Any, Dict, List, Callable
from datetime import datetime
from langchain.agents.middleware.types import AgentMiddleware
from langchain.agents.middleware import AgentState
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.store.sqlite import SqliteStore
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryMiddleware(AgentMiddleware):
    """Middleware that automatically saves conversation history to memory."""
    
    def __init__(self, sqlite_store: SqliteStore):
        super().__init__()
        self.sqlite_store = sqlite_store
        self.current_user_id = 'user1'
        self.current_thread_id = ''
        logger.info("MemoryMiddleware initialized with SqliteStore")
    
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
    
    def wrap_tool_call(
        self, request: Any, handler: Callable[[Any], Any]
    ) -> Any:
        """Wrap tool call to capture user_id and thread_id from request."""
        # Execute the tool call
        return handler(request)
    
    def before_model(
        self, state: Any, runtime: Runtime
    ) -> Any | None:
        """Before model execution - capture config from runtime."""
        self._capture_config(runtime, "before_model")
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
            return {
                'type': 'ai',
                'content': message.content,
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
    
    def _save_conversation_history(self, messages: list):
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
                self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            # Get existing user data
            existing_data = self.sqlite_store.get(
                namespace=('memories', 'conversations'),
                key=user_id
            )
            
            if existing_data:
                user_data = existing_data.value
                threads = user_data.get('threads', [])
            else:
                user_data = {
                    'user_id': user_id,
                    'threads': []
                }
                threads = []
            
            # Find or create thread
            thread_found = False
            for thread in threads:
                if thread.get('thread_id') == thread_id:
                    # Update existing thread
                    thread['date'] = date_str
                    thread['messages'] = serialized_messages
                    thread['updated_at'] = datetime.now().isoformat()
                    thread_found = True
                    break
            
            if not thread_found and thread_id:
                # Create new thread
                new_thread = {
                    'thread_id': thread_id,
                    'date': date_str,
                    'messages': serialized_messages,
                    'updated_at': datetime.now().isoformat()
                }
                threads.append(new_thread)
                user_data['threads'] = threads
            
            # Save to SqliteStore
            self.sqlite_store.put(
                namespace=('memories', 'conversations'),
                key=user_id,
                value=user_data
            )
            
            logger.info(f"Saved conversation history for user: {user_id}, thread: {thread_id}")
            logger.debug(f"Conversation data: {json.dumps(user_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}", exc_info=True)
    
    def after_model(
        self, state: AgentState, runtime: Runtime
    ) -> Dict[str, Any] | None:
        """Save conversation history after model execution.
        
        Args:
            state: The current agent state containing messages and todos.
            runtime: The LangGraph runtime instance.
            
        Returns:
            None to allow normal execution.
        """
        try:
            logger.debug("MemoryMiddleware: after_model called")
            
            # Get messages from state if it exists
            messages = state.get('messages', []) if 'messages' in state else []
            if messages:
                logger.debug(f"Saving conversation history with {len(messages)} messages")
                self._save_conversation_history(messages)
            
        except Exception as e:
            logger.error(f"Error in MemoryMiddleware.after_model: {e}", exc_info=True)
        
        return None
