import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore

from app.agent.constants import (
    CHECKPOINTS_PATH,
    MEMORIES_PATH,
    CONVERSATIONS_NAMESPACE,
    PREFERENCES_NAMESPACE
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def commit_transaction(sqlite_store: SqliteStore) -> None:
    """提交未完成的事务"""
    try:
        sqlite_store.conn.commit()
    except Exception:
        pass


def initialize_checkpoint_saver() -> SqliteSaver:
    """初始化检查点保存器"""
    os.makedirs(os.path.dirname(CHECKPOINTS_PATH), exist_ok=True)
    saver = SqliteSaver(sqlite3.connect(CHECKPOINTS_PATH, check_same_thread=False))
    logger.info(f"Initialized SQLite checkpoints store at: {CHECKPOINTS_PATH}")
    return saver


def initialize_sqlite_store() -> SqliteStore:
    """初始化SQLite存储"""
    os.makedirs(os.path.dirname(MEMORIES_PATH), exist_ok=True)
    store = SqliteStore(sqlite3.connect(MEMORIES_PATH, check_same_thread=False))
    logger.info(f"Initialized SQLite store at: {MEMORIES_PATH}")
    return store


def initialize_user_preferences(sqlite_store: SqliteStore) -> None:
    """初始化用户偏好数据"""
    try:
        sqlite_store.setup()
        commit_transaction(sqlite_store)

        existing = sqlite_store.get(
            namespace=PREFERENCES_NAMESPACE,
            key='settings'
        )

        if not existing:
            default_preferences = {
                'theme': 'default',
                'language': 'zh-CN',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            sqlite_store.put(
                namespace=PREFERENCES_NAMESPACE,
                key='settings',
                value=default_preferences
            )

            logger.info("Initialized default user preferences")

    except Exception as e:
        logger.error(f"Error initializing user preferences: {e}", exc_info=True)


def get_user_conversations(sqlite_store: SqliteStore, user_id: str) -> List[Dict[str, Any]]:
    """获取用户的所有对话线程"""
    commit_transaction(sqlite_store)
    stored_data = sqlite_store.get(
        namespace=CONVERSATIONS_NAMESPACE,
        key=user_id
    )
    return stored_data.value.get('threads', []) if stored_data else []


def save_user_conversations(sqlite_store: SqliteStore, user_id: str, threads: List[Dict[str, Any]]) -> None:
    """保存用户的对话线程"""
    sqlite_store.put(
        namespace=CONVERSATIONS_NAMESPACE,
        key=user_id,
        value={'threads': threads}
    )
    sqlite_store.conn.commit()


def get_conversation_history(sqlite_store: SqliteStore, user_id: str) -> List[Dict[str, Any]]:
    """获取用户的所有对话线程（对外接口）"""
    try:
        return get_user_conversations(sqlite_store, user_id)
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        return []


def get_thread_history(sqlite_store: SqliteStore, user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
    """获取用户的特定对话线程"""
    try:
        threads = get_user_conversations(sqlite_store, user_id)
        for thread in threads:
            if thread.get('thread_id') == thread_id:
                return thread
        return None
    except Exception as e:
        logger.error(f"Error getting thread history: {e}", exc_info=True)
        return None


def delete_thread(sqlite_store: SqliteStore, user_id: str, thread_id: str) -> bool:
    """删除用户的特定对话线程"""
    try:
        threads = get_user_conversations(sqlite_store, user_id)
        new_threads = [t for t in threads if t.get('thread_id') != thread_id]

        if len(new_threads) != len(threads):
            save_user_conversations(sqlite_store, user_id, new_threads)
            return True

        return False
    except Exception as e:
        logger.error(f"Error deleting thread: {e}", exc_info=True)
        return False
