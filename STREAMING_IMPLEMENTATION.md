# Streaming and Non-Streaming Implementation

## Overview
This implementation follows the LangChain Deep Agents streaming documentation to provide both streaming and non-streaming modes for agent execution.

## Key Features

### 1. Non-Streaming Mode
- Uses `agent.run(goal)` to execute the agent synchronously
- Returns the complete result once execution is finished
- Suitable for simple tasks where real-time updates are not needed

### 2. Streaming Mode
- Uses `agent.stream()` with subgraph support to enable real-time updates
- Supports three stream modes:
  - `messages`: Stream individual LLM tokens from main agent and subagents
  - `updates`: Track subagent progress as each step completes
  - `custom`: Emit user-defined signals from inside subagent nodes
- Provides namespace information to identify which agent produced each event

## Implementation Details

### Agent Class (backend/app/agent/agent.py)

#### Non-Streaming Mode
```python
def run(self, goal: str) -> dict:
    """同步运行Agent（非流式模式）"""
    return self.agent.run(goal)
```

#### Streaming Mode
```python
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
                yield {
                    "type": "token",
                    "source": "subagent" if namespace else "main",
                    "namespace": namespace,
                    "content": token.content if hasattr(token, 'content') else str(token),
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
        # 如果流式输出失败，回退到同步模式
        result = self.agent.run(goal)
        yield {
            "type": "fallback",
            "content": result
        }
```

### API Endpoints (backend/app/api/api.py)

#### Non-Streaming Endpoint
```python
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
```

#### Streaming Endpoint
```python
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
```

## Usage Examples

### Non-Streaming Mode
```bash
curl -X POST http://localhost:8000/run-agent \
  -H "Content-Type: application/json" \
  -d '{"goal": "Research quantum computing advances", "mode": "non-streaming"}'
```

### Streaming Mode (Updates)
```bash
curl -N http://localhost:8000/run-agent-stream?goal=Research+quantum+computing+advances&stream_mode=updates
```

### Streaming Mode (Messages)
```bash
curl -N http://localhost:8000/run-agent-stream?goal=Research+quantum+computing+advances&stream_mode=messages
```

## Key Concepts

### Namespaces
- Empty namespace: Main agent events
- `("tools:abc123",)`: Subagent spawned by main agent's task tool call abc123
- `("tools:abc123", "model_request:def456")`: Model request node inside a subagent

### Stream Modes
1. **messages**: Stream individual LLM tokens from all agents
2. **updates**: Track subagent progress as each step completes
3. **custom**: Emit user-defined signals from inside subagent nodes

### Subgraph Streaming
- Enabled by setting `subgraphs=True` in the stream method
- Allows tracking of subagent execution in real-time
- Provides visibility into tool calls and results from within subagent execution

## Error Handling
- If streaming fails, the implementation falls back to non-streaming mode
- Detailed error messages are returned in both modes
- Proper JSON serialization is ensured for all output formats

## Future Enhancements
- Add support for combining multiple stream modes
- Implement custom event emission from tools
- Add WebSocket support for bidirectional communication
- Enhance frontend visualization of streaming events