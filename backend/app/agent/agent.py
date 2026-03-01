from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from app.models.models import AgentResponse
# 导入中间件
from app.middleware.logger_middleware import LoggerMiddleware
from app.middleware.memory_middleware import MemoryMiddleware
# 导入技能和工具注册表
from app.skills import skill_registry
from app.tools.registry import ToolRegistry
# 导入自定义日志
from app.utils.logger import get_logger
# 导入配置
from config.settings import settings
import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime
from langgraph.store.sqlite import SqliteStore

logger = get_logger(__name__)

@dataclass
class Context:
    user_id: str
    thread_id: str

class AutonomousAgent:
    def __init__(self):
        """初始化自主决策Agent"""
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.BASE_URL,
            temperature=settings.MODEL_TEMPERATURE,
            timeout=settings.MODEL_TIMEOUT,
            max_retries=settings.MODEL_MAX_RETRIES,
        )

        self.agent = None
        # 初始化SQLite存储作为检查点
        checkpoints_path = "./persistence/checkpoints/checkpoints.db"
        os.makedirs(os.path.dirname(checkpoints_path), exist_ok=True)
        self.checkpoint_saver = SqliteSaver(sqlite3.connect(checkpoints_path, check_same_thread=False))
        logger.info(f"Initialized SQLite checkpoints store at: {checkpoints_path}")
        # 初始化SQLite存储用于持久记忆
        # 确保memory目录存在并初始化SQLite存储
        db_path = "./persistence/memory/memories.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.sqlite_store = SqliteStore(sqlite3.connect(db_path, check_same_thread=False))
        logger.info(f"Initialized SQLite store at: {db_path}")
        
    def _initialize_user_preferences(self):
        """初始化用户偏好数据"""
        try:
            # Setup the store first
            self.sqlite_store.setup()
            
            # Commit any pending transaction from setup
            try:
                self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            # 检查是否已经存在默认用户偏好
            existing = self.sqlite_store.get(
                namespace=('memories', 'preferences'),
                key='settings'
            )
            
            if not existing:
                # 创建默认用户偏好
                default_preferences = {
                    'theme': 'default',
                    'language': 'zh-CN',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.sqlite_store.put(
                    namespace=('memories', 'preferences'),
                    key='settings',
                    value=default_preferences
                )
                
                logger.info("Initialized default user preferences")
            
        except Exception as e:
            logger.error(f"Error initializing user preferences: {e}", exc_info=True)

    def create_backend(self, runtime):
        """创建复合后端，实现持久记忆存储"""
        # 默认后端：使用临时存储（StateBackend）
        default_backend = StateBackend(runtime)
        
        # 记忆存储后端：持久化存储，配置namespace
        memory_backend = StoreBackend(
            runtime,
            namespace=lambda ctx: ("memories",)
        )
        
        # 创建复合后端，路由规则：/memories/ 路径使用持久存储
        # 注意：routes参数应该是字典格式，而不是列表
        return CompositeBackend(
            default=default_backend,
            routes={
                "/memories/": memory_backend,  # 记忆路径指向持久存储
                "/memories/profiles/": memory_backend,  # 用户配置文件
                "/memories/conversations/": memory_backend,  # 对话历史
                "/memories/knowledge/": memory_backend,  # 知识库
                "/memories/preferences/": memory_backend  # 系统偏好
            }
        )

    async def start_up(self):
        """初始化Agent"""
        # 初始化用户偏好数据
        self._initialize_user_preferences()
        
        # 初始化ToolRegistry实例
        self.tool_registry = ToolRegistry()

        await self.tool_registry.load_tools()

        await self.tool_registry.load_mcp_tools()

        # 加载工具
        tools = list(self.tool_registry.tools.values())

        # 获取技能目录（用于Deep Agent技能）
        skills_directory = skill_registry.get_skills_directory()
        
        # 创建中间件列表
        middleware_list = [
            LoggerMiddleware(),
            MemoryMiddleware(self.sqlite_store)
        ]
        
        self.agent = create_deep_agent(
                name="autonomous-agent",
                system_prompt="""
                    You are an intelligent agent with a complete closed-loop decision-making capability base on built-in tools and skills and explicit specified available tools and skills.
                    You strictly follow the logical chain of Think - Plan - Execute - Observe - Reflect - Adjust to accomplish any goal set by the user.
                    Core Workflow:
                    Think: Deeply analyze the user's goal, understand the core demand and success conditions.
                    Plan: Always use write_dotos to break down the goal into atomic, executable steps.
                    Execute: Perform tasks step by step based on the plan.
                    Observe: Collect feedback and results during execution.
                    Reflect: Analyze gaps between actual results and expectations, identify problems if any.
                    Adjust: Optimize the plan and execution strategy based on reflection.
                    Note:
                    - If the goal is completed, set is_completed to True.
                    - If there are any todos, list them in the todos field.
                    - Always maintain this closed-loop logic until the goal is completed.
                """,
                model=self.llm,
                tools=tools,
                skills=[skills_directory],
                response_format=AgentResponse,
                middleware=middleware_list,
                backend=self.create_backend,
                store=self.sqlite_store,
                checkpointer=self.checkpoint_saver,
                context_schema=Context
            )
    
    def run(self, goal: str, session_id: str = None, user_id: str = "user1") -> dict:
        """同步运行Agent(非流式模式)"""
        # 使用session_id作为thread_id，如果没有提供则生成唯一的thread_id
        import uuid
        thread_id = session_id if session_id else str(uuid.uuid4())
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": goal}]},
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            context={"user_id": user_id, "thread_id": thread_id}
        )
    
    async def run_async(self, goal: str, stream_mode: str = "updates", subgraphs: bool = True, session_id: str = None, user_id: str = "user1"):
        """异步运行Agent(流式输出)"""
        try:
            # 使用session_id作为thread_id，如果没有提供则生成唯一的thread_id
            import uuid
            thread_id = session_id if session_id else str(uuid.uuid4())

            # 使用stream方法实现流式输出，支持子图事件
            logger.info(f"Calling agent.stream() with stream_mode: {stream_mode}")
            stream_result = self.agent.stream(
                {"messages": [{"role": "user", "content": goal}]},
                stream_mode=stream_mode,
                subgraphs=subgraphs,
                config={"configurable": {"thread_id": thread_id}},
                context={"user_id": user_id, "thread_id": thread_id}
            )
            
            for namespace, chunk in stream_result:
                logger.debug(f"Got chunk: namespace={namespace}, type={type(chunk)}, value={chunk}")
                
                # 处理不同类型的chunk
                if stream_mode == "messages":
                    # 处理LLM tokens
                    try:
                        print(f"[DEBUG] Processing message chunk")
                        if isinstance(chunk, list):
                            # 如果chunk是列表，取第一个元素作为token
                            print(f"[DEBUG] Chunk is list, length: {len(chunk)}")
                            token = chunk[0]
                            metadata = {} if len(chunk) < 2 else chunk[1]
                            print(f"[DEBUG] Token type: {type(token)}, Metadata type: {type(metadata)}")
                        else:
                            # 否则尝试解包
                            print(f"[DEBUG] Chunk is not list, trying to unpack")
                            token, metadata = chunk
                            print(f"[DEBUG] Token type: {type(token)}, Metadata type: {type(metadata)}")
                        
                        content = token.content if hasattr(token, 'content') else str(token)
                        logger.debug(f"Content: {content}")
                        
                        # 跳过空内容
                        if not content:
                            logger.debug(f"[DEBUG] Content is empty, skipping")
                            continue
                        
                        # 确保metadata是可序列化的
                        try:
                            # 检查metadata是否有items方法
                            if hasattr(metadata, 'items'):
                                pass  # 已经是字典
                            elif isinstance(metadata, list):
                                logger.info(f"Metadata is list, length: {len(metadata)}")
                                # 如果是列表，转换为字典
                                metadata = {f'item_{i}': item for i, item in enumerate(metadata)}
                            else:
                                logger.warning(f"Unsupported metadata type: {type(metadata)}")
                                metadata = str(metadata)
                        except Exception as e:
                            # 处理任何异常，将metadata转换为字符串
                            logger.error(f"Error processing metadata: {str(e)}")
                            metadata = str(metadata)

                        yield {
                            "type": "token",
                            "source": "subagent" if namespace else "main",
                            "namespace": namespace,
                            "content": content,
                            "metadata": metadata
                        }
                    except Exception as e:
                        # 处理解析错误
                        logger.error(f"Error processing message chunk: {str(e)}")
                        # 尝试直接使用chunk作为内容
                        content = str(chunk)
                        if content:
                            yield {
                                "type": "token",
                                "source": "subagent" if namespace else "main",
                                "namespace": namespace,
                                "content": content,
                                "metadata": {}
                            }
                elif stream_mode == "updates":
                    # 处理节点更新
                    yield {
                        "type": "update",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "data": chunk
                    }
                elif stream_mode == "custom":
                    # 处理自定义事件
                    yield {
                        "type": "custom",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "event": chunk
                    }
                else:
                    # 默认处理
                    yield {
                        "type": "unknown",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "data": chunk
                    }
        except Exception as e:
            logger.error(f"Error in run_async: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
    async def invoke(self, goal: str):
        """异步运行Agent(流式输出)- 兼容api.py中的调用"""
        # 直接调用run_async方法
        async for result in self.run_async(goal):
            yield result
    
    def get_conversation_history(self, user_id: str) -> list:
        """Get all conversation threads for a user.
        
        Args:
            user_id: The user ID to get history for
            
        Returns:
            List of conversation threads
        """
        try:
            # Commit any pending transaction
            try:
                self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            stored_data = self.sqlite_store.get(
                namespace=('memories', 'conversations'),
                key=user_id
            )
            
            if stored_data:
                return stored_data.value.get('threads', [])
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}", exc_info=True)
            return []
    
    def get_thread_history(self, user_id: str, thread_id: str) -> dict | None:
        """Get a specific conversation thread for a user.
        
        Args:
            user_id: The user ID
            thread_id: The thread ID to get
            
        Returns:
            Thread data or None if not found
        """
        try:
            # Commit any pending transaction
            try:
                self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            stored_data = self.sqlite_store.get(
                namespace=('memories', 'conversations'),
                key=user_id
            )
            
            if stored_data:
                threads = stored_data.value.get('threads', [])
                for thread in threads:
                    if thread.get('thread_id') == thread_id:
                        return thread
            return None
        except Exception as e:
            logger.error(f"Error getting thread history: {e}", exc_info=True)
            return None
    
    def delete_thread(self, user_id: str, thread_id: str) -> bool:
        """Delete a specific conversation thread for a user.
        
        Args:
            user_id: The user ID
            thread_id: The thread ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Commit any pending transaction
            try:
                self.sqlite_store.conn.commit()
            except Exception:
                pass
            
            stored_data = self.sqlite_store.get(
                namespace=('memories', 'conversations'),
                key=user_id
            )
            
            if stored_data:
                threads = stored_data.value.get('threads', [])
                # Filter out the thread to delete
                new_threads = [t for t in threads if t.get('thread_id') != thread_id]
                
                if len(new_threads) != len(threads):
                    stored_data.value['threads'] = new_threads
                    self.sqlite_store.put(
                        namespace=('memories', 'conversations'),
                        key=user_id,
                        value=stored_data.value
                    )
                    self.sqlite_store.conn.commit()
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting thread: {e}", exc_info=True)
            return False