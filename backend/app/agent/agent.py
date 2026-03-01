import uuid
import traceback
from dataclasses import dataclass
from typing import Dict, Any, Optional, AsyncGenerator

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI

from app.models.models import AgentResponse
from app.middleware.logger_middleware import LoggerMiddleware
from app.middleware.memory_middleware import MemoryMiddleware
from app.skills import skill_registry
from app.tools.registry import ToolRegistry
from app.utils.logger import get_logger
from app.config.settings import settings
from app.agent import storage
from app.agent import stream_processor

logger = get_logger(__name__)


@dataclass
class Context:
    user_id: str
    thread_id: str


class AutonomousAgent:
    def __init__(self):
        """初始化自主决策Agent"""
        self.llm = self._initialize_llm()
        self.agent = None
        self.checkpoint_saver = storage.initialize_checkpoint_saver()
        self.sqlite_store = storage.initialize_sqlite_store()
        self.tool_registry = None

    def _initialize_llm(self) -> ChatOpenAI:
        """初始化LLM模型"""
        return ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.BASE_URL,
            temperature=settings.MODEL_TEMPERATURE,
            timeout=settings.MODEL_TIMEOUT,
            max_retries=settings.MODEL_MAX_RETRIES,
        )

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
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
        """

    def _get_thread_id(self, session_id: Optional[str]) -> str:
        """获取或生成thread_id"""
        return session_id if session_id else str(uuid.uuid4())

    def create_backend(self, runtime):
        """创建复合后端，实现持久记忆存储"""
        default_backend = StateBackend(runtime)
        memory_backend = StoreBackend(
            runtime,
            namespace=lambda ctx: ("memories",)
        )

        return CompositeBackend(
            default=default_backend,
            routes={
                "/memories/": memory_backend,
                "/memories/profiles/": memory_backend,
                "/memories/conversations/": memory_backend,
                "/memories/knowledge/": memory_backend,
                "/memories/preferences/": memory_backend
            }
        )

    async def start_up(self) -> None:
        """初始化Agent"""
        storage.initialize_user_preferences(self.sqlite_store)

        self.tool_registry = ToolRegistry()
        await self.tool_registry.load_tools()
        await self.tool_registry.load_mcp_tools()

        tools = list(self.tool_registry.tools.values())
        skills_directory = skill_registry.get_skills_directory()

        middleware_list = [
            LoggerMiddleware(),
            MemoryMiddleware(self.sqlite_store)
        ]

        self.agent = create_deep_agent(
            name="autonomous-agent",
            system_prompt=self._get_system_prompt(),
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

    def run(self, goal: str, session_id: Optional[str] = None, user_id: str = "user1") -> Dict[str, Any]:
        """同步运行Agent(非流式模式)"""
        thread_id = self._get_thread_id(session_id)
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": goal}]},
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            context={"user_id": user_id, "thread_id": thread_id}
        )

    async def run_async(
        self,
        goal: str,
        stream_mode: str = "updates",
        subgraphs: bool = True,
        session_id: Optional[str] = None,
        user_id: str = "user1"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """异步运行Agent(流式输出)"""
        try:
            thread_id = self._get_thread_id(session_id)

            logger.info(f"Calling agent.stream() with stream_mode: {stream_mode}")
            stream_result = self.agent.stream(
                {"messages": [{"role": "user", "content": goal}]},
                stream_mode=stream_mode,
                subgraphs=subgraphs,
                config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
                context={"user_id": user_id, "thread_id": thread_id}
            )

            for namespace, chunk in stream_result:
                logger.debug(f"Got chunk: namespace={namespace}, type={type(chunk)}, value={chunk}")

                if stream_mode == "messages":
                    async for result in stream_processor.process_message_chunk(namespace, chunk):
                        yield result
                elif stream_mode == "updates":
                    yield stream_processor.process_update_chunk(namespace, chunk)
                elif stream_mode == "custom":
                    yield stream_processor.process_custom_chunk(namespace, chunk)
                else:
                    yield stream_processor.process_unknown_chunk(namespace, chunk)

        except Exception as e:
            logger.error(f"Error in run_async: {str(e)}")
            traceback.print_exc()
            raise

    async def invoke(self, goal: str) -> AsyncGenerator[Dict[str, Any], None]:
        """异步运行Agent(流式输出)- 兼容api.py中的调用"""
        async for result in self.run_async(goal):
            yield result

    def get_conversation_history(self, user_id: str):
        """获取用户的所有对话线程"""
        return storage.get_conversation_history(self.sqlite_store, user_id)

    def get_thread_history(self, user_id: str, thread_id: str):
        """获取用户的特定对话线程"""
        return storage.get_thread_history(self.sqlite_store, user_id, thread_id)

    def delete_thread(self, user_id: str, thread_id: str) -> bool:
        """删除用户的特定对话线程"""
        return storage.delete_thread(self.sqlite_store, user_id, thread_id)
