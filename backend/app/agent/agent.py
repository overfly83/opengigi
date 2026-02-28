from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from app.models.models import AgentResponse
# 导入中间件
from app.middleware.logger_middleware import LoggerMiddleware
# 导入技能和工具注册表
from app.skills import skill_registry
from app.tools.registry import ToolRegistry
# 导入自定义日志
from app.utils.logger import get_logger
# 导入配置
from config.settings import settings

logger = get_logger(__name__)


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
        # 初始化内存存储作为检查点
        self.checkpoint_saver = InMemorySaver()

    def create_backend(self, runtime):
        """创建复合后端，实现持久记忆存储"""
        # 默认后端：使用临时存储（StateBackend）
        default_backend = StateBackend(runtime)
        
        # 记忆存储后端：使用基于LangGraph store的StoreBackend
        memory_backend = StoreBackend(runtime)
        
        # 创建复合后端，路由规则：/memories/ 路径使用持久存储
        # 注意：routes参数应该是字典格式，而不是列表
        return CompositeBackend(
            default=default_backend,
            routes={
                "/memories/": memory_backend  # 记忆路径指向持久存储
            }
        )

    async def start_up(self):
        """初始化Agent"""
        # 初始化ToolRegistry实例
        self.tool_registry = ToolRegistry()

        await self.tool_registry.load_tools()

        await self.tool_registry.load_mcp_tools()

        # 加载工具
        tools = list(self.tool_registry.tools.values())

        # 获取技能目录（用于Deep Agent技能）
        skills_directory = skill_registry.get_skills_directory()
        
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
                middleware=[LoggerMiddleware()],
                backend=self.create_backend,
                checkpointer=self.checkpoint_saver
            )
    
    def run(self, goal: str, session_id: str = None, user_id: str = "user1") -> dict:
        """同步运行Agent（非流式模式）"""
        # 使用session_id作为thread_id，如果没有提供则生成唯一的thread_id
        import uuid
        thread_id = session_id if session_id else str(uuid.uuid4())
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": goal}]},
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}}
        )
    
    async def run_async(self, goal: str, stream_mode: str = "updates", subgraphs: bool = True, session_id: str = None, user_id: str = "user1"):
        """异步运行Agent（流式输出）"""
        try:
            # 使用session_id作为thread_id，如果没有提供则生成唯一的thread_id
            import uuid
            thread_id = session_id if session_id else str(uuid.uuid4())
            print(f"[DEBUG] Starting run_async with thread_id: {thread_id}, user_id: {user_id}")
            
            # 使用stream方法实现流式输出，支持子图事件
            print(f"[DEBUG] Calling agent.stream() with stream_mode: {stream_mode}")
            stream_result = self.agent.stream(
                {"messages": [{"role": "user", "content": goal}]},
                stream_mode=stream_mode,
                subgraphs=subgraphs,
                config={"configurable": {"thread_id": thread_id, "user_id": user_id}}
            )
            print(f"[DEBUG] Got stream result: {type(stream_result)}")
            
            print(f"[DEBUG] Starting to iterate over stream")
            for namespace, chunk in stream_result:
                print(f"[DEBUG] Got chunk: namespace={namespace}, type={type(chunk)}, value={chunk}")
                
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
                        
                        print(f"[DEBUG] Getting content from token")
                        content = token.content if hasattr(token, 'content') else str(token)
                        print(f"[DEBUG] Content: {content}")
                        
                        # 跳过空内容
                        if not content:
                            print(f"[DEBUG] Content is empty, skipping")
                            continue
                        
                        # 确保metadata是可序列化的
                        print(f"[DEBUG] Processing metadata")
                        try:
                            # 检查metadata是否有items方法
                            if hasattr(metadata, 'items'):
                                print(f"[DEBUG] Metadata has items method")
                                pass  # 已经是字典
                            elif isinstance(metadata, list):
                                print(f"[DEBUG] Metadata is list, converting to dict")
                                # 如果是列表，转换为字典
                                metadata = {f'item_{i}': item for i, item in enumerate(metadata)}
                            else:
                                print(f"[DEBUG] Metadata is other type, converting to string")
                                # 其他情况，转换为字符串
                                metadata = str(metadata)
                        except Exception as e:
                            # 处理任何异常，将metadata转换为字符串
                            print(f"[DEBUG] Error processing metadata: {str(e)}")
                            metadata = str(metadata)
                        
                        print(f"[DEBUG] Yielding token result")
                        yield {
                            "type": "token",
                            "source": "subagent" if namespace else "main",
                            "namespace": namespace,
                            "content": content,
                            "metadata": metadata
                        }
                    except Exception as e:
                        # 处理解析错误
                        print(f"[DEBUG] Error processing message chunk: {str(e)}")
                        # 尝试直接使用chunk作为内容
                        content = str(chunk)
                        if content:
                            print(f"[DEBUG] Yielding error token result")
                            yield {
                                "type": "token",
                                "source": "subagent" if namespace else "main",
                                "namespace": namespace,
                                "content": content,
                                "metadata": {}
                            }
                elif stream_mode == "updates":
                    # 处理节点更新
                    print(f"[DEBUG] Yielding update result")
                    yield {
                        "type": "update",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "data": chunk
                    }
                elif stream_mode == "custom":
                    # 处理自定义事件
                    print(f"[DEBUG] Yielding custom result")
                    yield {
                        "type": "custom",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "event": chunk
                    }
                else:
                    # 默认处理
                    print(f"[DEBUG] Yielding unknown result")
                    yield {
                        "type": "unknown",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "data": chunk
                    }
        except Exception as e:
            print(f"[DEBUG] Error in run_async: {str(e)}")
            import traceback
            traceback.print_exc()
            # 如果流式输出失败，回退到同步模式
            import uuid
            thread_id = session_id if session_id else str(uuid.uuid4())
            print(f"[DEBUG] Falling back to sync mode with thread_id: {thread_id}, user_id: {user_id}")
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": goal}]},
                config={"configurable": {"thread_id": thread_id, "user_id": user_id}}
            )
            print(f"[DEBUG] Got fallback result: {type(result)}")
            yield {
                "type": "fallback",
                "content": result
            }
    
    async def invoke(self, goal: str):
        """异步运行Agent（流式输出）- 兼容api.py中的调用"""
        # 直接调用run_async方法
        async for result in self.run_async(goal):
            yield result