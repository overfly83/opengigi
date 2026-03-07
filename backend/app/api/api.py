from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import json
from app.agent.agent import AutonomousAgent
import asyncio
from pydantic import BaseModel
from typing import Optional
# 导入自定义日志
from app.utils.logger import get_logger


logger = get_logger(__name__)

# 创建全局Agent实例
agent = AutonomousAgent()

# 定义生命周期事件处理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("Starting up...")
    # 异步加载 MCP 工具
    try:
        await agent.start_up()
        logger.info("Agent started up successfully")
    except Exception as e:
        logger.error(f"Failed to start up agent: {e}")
        raise e
    yield
    # 关闭时执行
    logger.info("Shutting down...")
    try:
        await agent.shutdown()
        logger.info("Agent shutdown successfully")
    except Exception as e:
        logger.error(f"Error during agent shutdown: {e}")

app = FastAPI(lifespan=lifespan)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class AgentRequest(BaseModel):
    goal: str
    mode: str  # streaming 或 non-streaming


class StreamRequest(BaseModel):
    goal: str
    stream_mode: str = "updates"
    session_id: Optional[str] = None
    user_id: str = "user1"


@app.post("/run-agent")
async def run_agent(request: AgentRequest, session_id: str = None, user_id: str = "user1"):
    """运行Agent（非流式模式）"""
    try:
        # 执行Agent
        state = agent.run(request.goal, session_id=session_id, user_id=user_id)
        
        return {
            "success": True,
            "data": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run-agent-stream")
async def run_agent_stream(goal: str, stream_mode: str = "updates", session_id: str = None, user_id: str = "user1"):
    """运行Agent（流式模式）"""
    try:
        return StreamingResponse(
            agent.run_async(goal, stream_mode=stream_mode, session_id=session_id, user_id=user_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_conversation_history(user_id: str):
    """Get all conversation history for a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        List of conversation threads
    """
    try:
        history = await agent.get_conversation_history(user_id)
        return {
            "success": True,
            "data": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{user_id}/{thread_id}")
async def get_thread_history(user_id: str, thread_id: str):
    """Get a specific conversation thread for a user.
    
    Args:
        user_id: The user ID
        thread_id: The thread ID
        
    Returns:
        Thread data
    """
    try:
        thread = await agent.get_thread_history(user_id, thread_id)
        if thread:
            return {
                "success": True,
                "data": thread
            }
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history/{user_id}/{thread_id}")
async def delete_thread(user_id: str, thread_id: str):
    """Delete a specific conversation thread for a user.
    
    Args:
        user_id: The user ID
        thread_id: The thread ID to delete
        
    Returns:
        Success message
    """
    try:
        success = await agent.delete_thread(user_id, thread_id)
        if success:
            return {
                "success": True,
                "message": "Thread deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "自主决策Agent API - 第十二次更新",
        "endpoints": {
            "/run-agent": "运行Agent(非流式模式)",
            "/run-agent-stream": "运行Agent(流式模式)",
            "/history/{user_id}": "获取用户的历史对话列表",
            "/history/{user_id}/{thread_id}": "获取特定对话线程的详细内容"
        }
    }

# 移除直接运行的代码，使用uvicorn命令启动应用
# 例如：uvicorn api:app --host 0.0.0.0 --port 8000 --reload
