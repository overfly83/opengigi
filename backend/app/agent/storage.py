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


async def get_thread_history(sqlite_store: AsyncSqliteStore, user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
    """获取用户的特定对话线程"""
    try:
        await commit_transaction(sqlite_store)
        stored_data = await sqlite_store.aget(
            namespace=CONVERSATIONS_NAMESPACE,
            key=f"{user_id}:{thread_id}"
        )
        return stored_data.value if stored_data else None
    except Exception as e:
        logger.error(f"Error getting thread history: {e}", exc_info=True)
        return None


async def save_thread_history(sqlite_store: AsyncSqliteStore, user_id: str, thread: Dict[str, Any]) -> None:
    """保存用户的特定对话线程"""
    try:
        thread_id = thread.get('thread_id')
        if not thread_id:
            logger.error("Thread ID is required to save thread history")
            return
        
        await sqlite_store.aput(
            namespace=CONVERSATIONS_NAMESPACE,
            key=f"{user_id}:{thread_id}",
            value=thread
        )
        await commit_transaction(sqlite_store)
        logger.debug(f"Saved thread {thread_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving thread history: {e}", exc_info=True)


async def delete_thread(sqlite_store: AsyncSqliteStore, user_id: str, thread_id: str) -> bool:
    """删除用户的特定对话线程"""
    try:
        # 注意：AsyncSqliteStore 没有直接的删除方法，我们可以通过保存空值来模拟删除
        await sqlite_store.aput(
            namespace=CONVERSATIONS_NAMESPACE,
            key=f"{user_id}:{thread_id}",
            value=None
        )
        
        # 从索引中移除线程ID
        index_key = f"{user_id}:index"
        stored_index = await sqlite_store.aget(
            namespace=CONVERSATIONS_NAMESPACE,
            key=index_key
        )
        
        if stored_index and stored_index.value:
            thread_ids = stored_index.value
            if thread_id in thread_ids:
                thread_ids.remove(thread_id)
                await sqlite_store.aput(
                    namespace=CONVERSATIONS_NAMESPACE,
                    key=index_key,
                    value=thread_ids
                )
        
        await commit_transaction(sqlite_store)
        return True
    except Exception as e:
        logger.error(f"Error deleting thread: {e}", exc_info=True)
        return False


async def get_conversation_history(sqlite_store: AsyncSqliteStore, user_id: str) -> List[Dict[str, Any]]:
    """获取用户的所有对话线程（对外接口）"""
    try:
        # 注意：由于 AsyncSqliteStore 没有提供按前缀列出键的方法，
        # 我们需要维护一个索引来跟踪用户的所有线程
        # 先尝试从旧格式迁移数据
        await migrate_from_old_format(sqlite_store, user_id)
        
        # 获取用户的线程索引
        index_key = f"{user_id}:index"
        await commit_transaction(sqlite_store)
        stored_index = await sqlite_store.aget(
            namespace=CONVERSATIONS_NAMESPACE,
            key=index_key
        )
        
        thread_ids = stored_index.value if stored_index else []
        threads = []
        
        # 获取每个线程的详细信息
        for thread_id in thread_ids:
            thread = await get_thread_history(sqlite_store, user_id, thread_id)
            if thread:
                threads.append(thread)
        
        # 按更新时间排序（最新的在前）
        threads.sort(key=lambda x: x.get('updated_at', x.get('date', '')), reverse=True)
        
        return threads
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        return []


async def migrate_from_old_format(sqlite_store: AsyncSqliteStore, user_id: str) -> None:
    """从旧格式迁移数据到新格式"""
    try:
        # 检查是否存在旧格式数据
        old_data = await sqlite_store.aget(
            namespace=CONVERSATIONS_NAMESPACE,
            key=user_id
        )
        
        if old_data and old_data.value and 'threads' in old_data.value:
            threads = old_data.value['threads']
            if threads:
                # 迁移每个线程
                thread_ids = []
                for thread in threads:
                    thread_id = thread.get('thread_id')
                    if thread_id:
                        await save_thread_history(sqlite_store, user_id, thread)
                        thread_ids.append(thread_id)
                
                # 保存线程索引
                if thread_ids:
                    await sqlite_store.aput(
                        namespace=CONVERSATIONS_NAMESPACE,
                        key=f"{user_id}:index",
                        value=thread_ids
                    )
                    await commit_transaction(sqlite_store)
                
                # 移除旧格式数据
                await sqlite_store.aput(
                    namespace=CONVERSATIONS_NAMESPACE,
                    key=user_id,
                    value=None
                )
                await commit_transaction(sqlite_store)
                
                logger.info(f"Migrated {len(threads)} threads from old format for user {user_id}")
    except Exception as e:
        logger.error(f"Error migrating from old format: {e}", exc_info=True)


async def add_thread_to_index(sqlite_store: AsyncSqliteStore, user_id: str, thread_id: str) -> None:
    """将线程添加到用户的线程索引中"""
    try:
        index_key = f"{user_id}:index"
        stored_index = await sqlite_store.aget(
            namespace=CONVERSATIONS_NAMESPACE,
            key=index_key
        )
        
        thread_ids = stored_index.value if stored_index else []
        if thread_id not in thread_ids:
            thread_ids.append(thread_id)
            await sqlite_store.aput(
                namespace=CONVERSATIONS_NAMESPACE,
                key=index_key,
                value=thread_ids
            )
            await commit_transaction(sqlite_store)
    except Exception as e:
        logger.error(f"Error adding thread to index: {e}", exc_info=True)
