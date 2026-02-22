from pydantic import BaseModel
from typing import List, Optional, Literal

class Todo(BaseModel):
    """待办事项模型"""
    content: str
    status: Literal["pending", "success", "fail"]

class AgentResponse(BaseModel):
    """Agent响应模型"""
    phase: Literal["think", "plan", "execute", "observe", "reflect", "adjust"]
    result: str
    is_simple_and_unrelevant: Optional[bool] = None
    is_completed: Optional[bool] = None
    todos: Optional[List[Todo]] = None