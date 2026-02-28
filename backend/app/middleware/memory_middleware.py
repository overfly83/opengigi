import json
from typing import Any, Dict
from datetime import datetime
from langchain.agents.middleware import AgentMiddleware
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
        logger.info("MemoryMiddleware initialized with SqliteStore")
    
    def _get_user_id(self, runtime: Runtime) -> str:
        """Get user_id from runtime config."""
        try:
            if hasattr(runtime, 'context'):
                user_id = runtime.context.user_id or 'user1'
                return user_id
        except Exception:
            logger.error("Error getting user_id from runtime context")
            return 'user1'
    
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
    
    def _save_conversation_history(self, messages: list, runtime: Runtime):
        """Save conversation history to memory store."""
        try:
            user_id = self._get_user_id(runtime)
            date_str = datetime.now().strftime('%Y-%m-%d')
            key = f"{date_str}_{user_id}"
            
            # Serialize messages
            serialized_messages = [self._serialize_message(msg) for msg in messages]
            
            # Prepare conversation data
            conversation_data = {
                'user_id': user_id,
                'date': date_str,
                'messages': serialized_messages,
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to SqliteStore
            self.sqlite_store.put(
                namespace=('memories', 'conversations'),
                key=key,
                value=conversation_data
            )
            
            logger.info(f"Saved conversation history: {key}")
            logger.debug(f"Conversation data: {json.dumps(conversation_data, ensure_ascii=False)}")
            
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
                self._save_conversation_history(messages, runtime)
            
        except Exception as e:
            logger.error(f"Error in MemoryMiddleware.after_model: {e}", exc_info=True)
        
        return None
