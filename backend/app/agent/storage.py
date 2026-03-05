import os
import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Dict, Any, Optional

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite.aio import AsyncSqliteStore

from app.agent.constants import (
    CHECKPOINTS_PATH,
    MEMORIES_PATH,
    CONVERSATIONS_NAMESPACE,
    PREFERENCES_NAMESPACE
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def commit_transaction(sqlite_store: AsyncSqliteStore) -> None:
    """提交未完成的事务"""
    try:
        await sqlite_store.conn.commit()
    except Exception:
        pass


async def initialize_checkpoint_saver() -> AsyncSqliteSaver:
    """初始化检查点保存器"""
    os.makedirs(os.path.dirname(CHECKPOINTS_PATH), exist_ok=True)
    conn = await aiosqlite.connect(CHECKPOINTS_PATH, check_same_thread=False)
    saver = AsyncSqliteSaver(conn)
    logger.info(f"Initialized SQLite checkpoints store at: {CHECKPOINTS_PATH}")
    return saver


async def initialize_sqlite_store() -> AsyncSqliteStore:
    """初始化SQLite存储"""
    os.makedirs(os.path.dirname(MEMORIES_PATH), exist_ok=True)
    conn = await aiosqlite.connect(MEMORIES_PATH, check_same_thread=False)
    store = AsyncSqliteStore(conn)
    await store.setup()
    logger.info(f"Initialized SQLite store at: {MEMORIES_PATH}")
    return store


async def initialize_user_preferences(sqlite_store: AsyncSqliteStore) -> None:
    """初始化用户偏好数据"""
    try:
        existing = await sqlite_store.aget(
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

            await sqlite_store.aput(
                namespace=PREFERENCES_NAMESPACE,
                key='settings',
                value=default_preferences
            )

            logger.info("Initialized default user preferences")

    except Exception as e:
        logger.error(f"Error initializing user preferences: {e}", exc_info=True)


async def get_user_conversations(sqlite_store: AsyncSqliteStore, user_id: str) -> List[Dict[str, Any]]:
    """获取用户的所有对话线程"""
    await commit_transaction(sqlite_store)
    stored_data = await sqlite_store.aget(
        namespace=CONVERSATIONS_NAMESPACE,
        key=user_id
    )
    return stored_data.value.get('threads', []) if stored_data else []


async def save_user_conversations(sqlite_store: AsyncSqliteStore, user_id: str, threads: List[Dict[str, Any]]) -> None:
    """保存用户的对话线程"""
    await sqlite_store.aput(
        namespace=CONVERSATIONS_NAMESPACE,
        key=user_id,
        value={'threads': threads}
    )
    await commit_transaction(sqlite_store)


async def get_conversation_history(sqlite_store: AsyncSqliteStore, user_id: str) -> List[Dict[str, Any]]:
    """获取用户的所有对话线程（对外接口）"""
    try:
        return await get_user_conversations(sqlite_store, user_id)
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        return []


async def get_thread_history(sqlite_store: AsyncSqliteStore, user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
    """获取用户的特定对话线程"""
    try:
        threads = await get_user_conversations(sqlite_store, user_id)
        for thread in threads:
            if thread.get('thread_id') == thread_id:
                return thread
        return None
    except Exception as e:
        logger.error(f"Error getting thread history: {e}", exc_info=True)
        return None


async def delete_thread(sqlite_store: AsyncSqliteStore, user_id: str, thread_id: str) -> bool:
    """删除用户的特定对话线程"""
    try:
        threads = await get_user_conversations(sqlite_store, user_id)
        new_threads = [t for t in threads if t.get('thread_id') != thread_id]

        if len(new_threads) != len(threads):
            await save_user_conversations(sqlite_store, user_id, new_threads)
            return True

        return False
    except Exception as e:
        logger.error(f"Error deleting thread: {e}", exc_info=True)
        return False
