from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
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
                middleware=[LoggerMiddleware()]
            )
    
    def run(self, goal: str) -> dict:
        """同步运行Agent（非流式模式）"""
        return self.agent.invoke({"messages": [{"role": "user", "content": goal}]})
    
    async def run_async(self, goal: str, stream_mode: str = "updates", subgraphs: bool = True):
        """异步运行Agent（流式输出）"""
        try:
            # 使用stream方法实现流式输出，支持子图事件
            for namespace, chunk in self.agent.stream(
                {"messages": [{"role": "user", "content": goal}]},
                stream_mode=stream_mode,
                subgraphs=subgraphs
            ):
                # 处理不同类型的chunk
                if stream_mode == "messages":
                    # 处理LLM tokens
                    token, metadata = chunk
                    content = token.content if hasattr(token, 'content') else str(token)
                    
                    # 跳过空内容
                    if not content:
                        continue
                    
                    yield {
                        "type": "token",
                        "source": "subagent" if namespace else "main",
                        "namespace": namespace,
                        "content": content,
                        "metadata": metadata
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
            print(f"[DEBUG] Error in run_async: {str(e)}")
            # 如果流式输出失败，回退到同步模式
            result = self.agent.invoke({"messages": [{"role": "user", "content": goal}]})
            yield {
                "type": "fallback",
                "content": result
            }
    
    async def invoke(self, goal: str):
        """异步运行Agent（流式输出）- 兼容api.py中的调用"""
        # 直接调用run_async方法
        async for result in self.run_async(goal):
            yield result