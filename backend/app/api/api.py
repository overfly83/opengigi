from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import json
from app.agent.agent import AutonomousAgent
import asyncio
from pydantic import BaseModel
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

# 递归处理对象，确保可以被JSON序列化
def ensure_serializable(obj):
    """递归处理对象，确保可以被JSON序列化"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, list):
        return [ensure_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: ensure_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        # 如果是对象，转换为字典
        result_dict = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                # 只包含非私有属性
                result_dict[key] = ensure_serializable(value)
        return result_dict
    elif hasattr(obj, 'content'):
        # 处理LangChain的消息对象
        return {
            'type': obj.type if hasattr(obj, 'type') else 'unknown',
            'content': obj.content if hasattr(obj, 'content') else str(obj),
            'name': obj.name if hasattr(obj, 'name') else None
        }
    else:
        # 如果是其他不可序列化类型，转换为字符串
        return str(obj)

# 真正的流式输出生成器
async def generate_streaming_output(goal: str, stream_mode: str = "updates"):
    """生成流式输出"""
    try:
        # 直接使用agent的异步run方法，实时获取结果
        async for result in agent.run_async(goal, stream_mode=stream_mode):
            # 确保result可以被JSON序列化
            result = ensure_serializable(result)
            # 流式输出每个步骤
            yield f"data: {json.dumps(result)}\n\n"
            await asyncio.sleep(0.1)  # 小延迟，确保前端能实时显示
        
        # 输出完成标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        # 输出错误信息
        yield f"data: {json.dumps({"type": "error", "content": f"执行过程中出错: {str(e)}"})}\n\n"
        yield "data: [DONE]\n\n"
        raise

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    """运行Agent（非流式模式）"""
    try:
        # 执行Agent
        state = agent.run(request.goal)
        
        return {
            "success": True,
            "data": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/run-agent-stream")
async def run_agent_stream(goal: str, stream_mode: str = "updates"):
    """运行Agent（流式模式）"""
    try:
        return StreamingResponse(
            generate_streaming_output(goal, stream_mode=stream_mode),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "自主决策Agent API",
        "endpoints": {
            "/run-agent": "运行Agent（非流式模式）",
            "/run-agent-stream": "运行Agent（流式模式）"
        }
    }

# 移除直接运行的代码，使用uvicorn命令启动应用
# 例如：uvicorn api:app --host 0.0.0.0 --port 8000 --reload
