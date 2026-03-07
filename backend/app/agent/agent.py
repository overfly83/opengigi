import uuid
import traceback
import json
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
        self.checkpoint_saver = None
        self.sqlite_store = None
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
        self.checkpoint_saver = await storage.initialize_checkpoint_saver()
        self.sqlite_store = await storage.initialize_sqlite_store()
        
        await storage.initialize_user_preferences(self.sqlite_store)
        # load tools
        self.tool_registry = ToolRegistry()
        await self.tool_registry.load_tools()
        await self.tool_registry.load_mcp_tools()
        tools = self.tool_registry.list_tools()
        # load skills
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
            store= self.sqlite_store,
            checkpointer= self.checkpoint_saver,
            context_schema=Context
        )
    
    async def shutdown(self) -> None:
        """关闭Agent并清理资源"""
        logger.info("Shutting down agent resources...")
        # 清理SQLite连接
        if hasattr(self, 'sqlite_store') and self.sqlite_store:
            try:
                # 关闭检查点保存器连接
                if hasattr(self.checkpoint_saver, 'conn') and self.checkpoint_saver.conn:
                    await self.checkpoint_saver.conn.close()
                # 关闭SQLite存储连接
                if hasattr(self.sqlite_store, 'conn') and self.sqlite_store.conn:
                    await self.sqlite_store.conn.close()
                logger.info("SQLite connections are closed.")
            except Exception as e:
                logger.error(f"Error closing SQLite connections: {e}")


    def run(self, goal: str, session_id: Optional[str] = None, user_id: str = "user1") -> Dict[str, Any]:
        """同步运行Agent(非流式模式)"""
        import asyncio
        return asyncio.run(self.arun(goal, session_id, user_id))

    async def arun(self, goal: str, session_id: Optional[str] = None, user_id: str = "user1") -> Dict[str, Any]:
        """异步运行Agent(非流式模式)"""
        thread_id = self._get_thread_id(session_id)
        return await self.agent.ainvoke(
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
    ) -> AsyncGenerator[str, None]:
        """异步运行Agent(流式输出)"""
        try:
            thread_id = self._get_thread_id(session_id)

            logger.info(f"Calling agent.astream() with stream_mode: {stream_mode}")
            stream_result = self.agent.astream(
                {"messages": [{"role": "user", "content": goal}]},
                stream_mode=stream_mode,
                subgraphs=subgraphs,
                config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
                context={"user_id": user_id, "thread_id": thread_id}
            )

            # 跟踪已发送的消息ID
            sent_message_ids = set()
            accumulated_content = ""
            chunk_count = 0

            async for namespace, chunk in stream_result:
                chunk_count += 1
                logger.debug(f"Got chunk: namespace={namespace}, type={type(chunk)}, value={chunk}")

                # 处理不同类型的chunk
                if stream_mode == "messages":
                    async for result in stream_processor.process_message_chunk(namespace, chunk):
                        # 确保result可以被JSON序列化
                        result = stream_processor.ensure_serializable(result)
                        
                        # 1. 保持原有格式输出（向后兼容）
                        yield f"data: {json.dumps(result)}\n\n"
                        
                        # 2. 处理新的结构化事件格式
                        if isinstance(result, dict):
                            # 处理ai类型的结果（消息内容）
                            if result.get('type') == 'ai' and result.get('content'):
                                content = result['content']
                                msg_id = str(id(result))  # 生成消息ID
                                
                                # 跳过已发送的消息
                                if msg_id in sent_message_ids:
                                    logger.debug(f"[Stream] Skipping duplicate message id={msg_id}")
                                    continue
                                
                                # 累积内容
                                accumulated_content += content
                                
                                # 发送message_delta事件
                                yield stream_processor.create_message_delta_event(
                                    msg_id,
                                    content,
                                    accumulated_content
                                )
                                
                                # 标记为已发送
                                sent_message_ids.add(msg_id)
                elif stream_mode == "updates":
                    result = stream_processor.process_update_chunk(namespace, chunk)
                    # 确保result可以被JSON序列化
                    result = stream_processor.ensure_serializable(result)
                    
                    # 保持原有格式输出（向后兼容）
                    yield f"data: {json.dumps(result)}\n\n"
                elif stream_mode == "custom":
                    result = stream_processor.process_custom_chunk(namespace, chunk)
                    # 确保result可以被JSON序列化
                    result = stream_processor.ensure_serializable(result)
                    
                    # 保持原有格式输出（向后兼容）
                    yield f"data: {json.dumps(result)}\n\n"
                else:
                    result = stream_processor.process_unknown_chunk(namespace, chunk)
                    # 确保result可以被JSON序列化
                    result = stream_processor.ensure_serializable(result)
                    
                    # 保持原有格式输出（向后兼容）
                    yield f"data: {json.dumps(result)}\n\n"

            # 3. 流结束时发送message_complete事件
            if accumulated_content:
                yield stream_processor.create_message_complete_event(
                    accumulated_content,
                    chunk_count
                )
            
            # 4. 发送完成标记
            logger.debug(f"[SSE→Client] [DONE] - Stream completed, total chunks: {chunk_count}")
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in run_async: {str(e)}")
            traceback.print_exc()
            
            # 发送错误事件
            yield stream_processor.create_error_event(e)
            # 发送完成标记
            logger.debug(f"[SSE→Client] [DONE] - Stream completed with error")
            yield "data: [DONE]\n\n"
            raise

    async def invoke(self, goal: str) -> AsyncGenerator[Dict[str, Any], None]:
        """异步运行Agent(流式输出)- 兼容api.py中的调用"""
        # 注意：此方法已过时，建议直接使用run_async获取SSE格式的输出
        # 为了向后兼容，这里仍然返回字典格式
        async for sse_message in self.run_async(goal):
            # 解析SSE消息，提取数据部分
            if sse_message.startswith('data: '):
                data_part = sse_message[6:].strip()
                if data_part != '[DONE]':
                    try:
                        data = json.loads(data_part)
                        yield data
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse SSE message: {data_part}")

    async def get_conversation_history(self, user_id: str):
        """获取用户的所有对话线程"""
        return await storage.get_conversation_history(self.sqlite_store, user_id)

    async def get_thread_history(self, user_id: str, thread_id: str):
        """获取用户的特定对话线程"""
        return await storage.get_thread_history(self.sqlite_store, user_id, thread_id)

    async def delete_thread(self, user_id: str, thread_id: str) -> bool:
        """删除用户的特定对话线程"""
        return await storage.delete_thread(self.sqlite_store, user_id, thread_id)
