import axios from 'axios'
import { ChunkCacheManager } from './chunkCacheManager'

export class StreamHandler {
  constructor(app) {
    this.app = app
    this.eventSource = null
    this.chunkCacheManager = new ChunkCacheManager(app)
    this.jsonBuffer = ''
  }

  startStreamingMode() {
    this.app.addLog('info', '开始执行自主决策Agent（流式模式）')
    this.app.addLog('info', `目标: ${this.app.goal}`)
    this.app.agentStatus = '执行中...' // 设置执行状态

    let url = `http://localhost:8000/run-agent-stream?goal=${encodeURIComponent(this.app.goal)}&stream_mode=updates`
    if (this.app.sessionUuid) {
      url += `&session_id=${encodeURIComponent(this.app.sessionUuid)}`
    }
    if (this.app.userId) {
      url += `&user_id=${encodeURIComponent(this.app.userId)}`
    }
    this.eventSource = new EventSource(url)

    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.handleStreamDone()
        return
      }

      try {
        const data = JSON.parse(event.data)
        
        // Check for new structured event types
        if (data.type === 'message_delta') {
          this.handleMessageDelta(data)
        } else if (data.type === 'message_complete') {
          this.handleMessageComplete(data)
        } else if (data.type === 'tool_call') {
          this.handleToolCall(data)
        } else if (data.type === 'tool_result') {
          this.handleToolResult(data)
        } else if (data.type === 'error') {
          this.handleError(data)
        } else {
          // Fallback to original handling for backward compatibility
          this.handleStreamData(data)
        }
      } catch (error) {
        console.error('解析流数据失败:', error)
      }
    }

    this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      this.eventSource.close()
      this.app.isRunning = false
      this.app.agentStatus = null // 清除状态
      this.app.addLog('error', '流式连接失败，请重试')
    }
  }

  handleStreamDone() {
    this.eventSource.close()
    this.app.isRunning = false
    this.app.agentStatus = null // 清除状态

    // 处理缓冲区中剩余的内容
    if (this.jsonBuffer.length > 0) {
      // 直接添加剩余内容作为info类型消息
      this.addMessage('info', this.jsonBuffer, 'done', 'done')
    }

    this.app.updateTodoListOnCompletion()

    const finalResult = this.extractFinalResult()
    
    if (finalResult) {
      this.app.result = {
        phase: 'reflect',
        result: finalResult.replace(/\n/g, '\n'),
        is_completed: true,
        todos: this.app.todos
      }
    }

    // 保存执行历史
    this.app.saveHistory()
  }

  extractFinalResult() {
    let finalResult = ''
    for (let i = this.app.processLogs.length - 1; i >= 0; i--) {
      const log = this.app.processLogs[i]
      if (log.content) {
        // 匹配主Agent的消息，支持不同的命名空间格式
        const mainAgentMatch = log.content.match(/^主Agent \((.*?)\): /)
        if (mainAgentMatch) {
          let content = log.content.replace(/^主Agent \((.*?)\): /, '')
          
          // 检查是否是结构化响应
          if (content.includes('Returning structured response:')) {
            // 提取结果部分，忽略技术术语
            const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length
            let structuredContent = content.substring(structuredStart).trim()
            
            // 尝试解析结构化内容
            try {
              // 提取result值
              const resultMatch = structuredContent.match(/result='([^']+)'/)
              if (resultMatch && resultMatch[1]) {
                finalResult = resultMatch[1]
                break
              }
              // 尝试另一种格式，如result="..."
              const resultMatchDoubleQuote = structuredContent.match(/result="([^"]+)"/)
              if (resultMatchDoubleQuote && resultMatchDoubleQuote[1]) {
                finalResult = resultMatchDoubleQuote[1]
                break
              }
            } catch (e) {
              // 解析失败，使用整个内容
              finalResult = content
              break
            }
          } else {
            // 非结构化响应，直接使用内容
            finalResult = content
            break
          }
        }
      }
    }
    return finalResult
  }

  handleStreamData(data) {
    if (data.type === 'token') {
      this._handleTokenData(data)
    } else if (data.type === 'update') {
      this._handleUpdateData(data)
    }
  }

  _handleTokenData(data) {
    if (!data.content) return

    let processedContent = this.app.processContentForTodos(data.content)
    if (!processedContent) return

    if (data.content.includes('Updated todo list to ')) {
      this.chunkCacheManager.initialize(this.app.todos)
    }

    // 直接添加消息，使用info类型
    this.addMessage('info', processedContent, data.source, data.namespace)
  }

  _handleUpdateData(data) {
    // 处理结构化响应
    this._handleStructuredResponse(data)
    
    // 处理model中的消息
    this._handleModelMessages(data)
    
    // 处理tools中的消息
    this._handleToolsMessages(data)
  }

  _handleStructuredResponse(data) {
    if (data.data && data.data.model && data.data.model.structured_response) {
      const structuredResponse = data.data.model.structured_response
      if (structuredResponse.result) {
        // 只显示结果内容，忽略技术术语
        this.addMessage('ai', `主Agent (${data.namespace}): ${structuredResponse.result}`, data.source, data.namespace)
      }
    }
  }

  _handleModelMessages(data) {
    if (data.data && data.data.model && data.data.model.messages) {
      data.data.model.messages.forEach(message => {
        this._handleMessage(message, data)
      })
    }
  }

  _handleToolsMessages(data) {
    if (data.data && data.data.tools && data.data.tools.messages) {
      data.data.tools.messages.forEach(message => {
        if (message.content) {
          this.addMessage('tool_result', `工具 (${data.namespace}): ${message.content}`, data.source, data.namespace)
        }
      })
    }
  }

  _handleMessage(message, data) {
    const namespace = data.namespace
    
    // 处理带内容的消息
    if (message.content) {
      if (message.content.includes('Returning structured response:')) {
        // 提取结果部分，忽略技术术语
        const structuredStart = message.content.indexOf('Returning structured response:') + 'Returning structured response:'.length
        let structuredContent = message.content.substring(structuredStart).trim()
        
        if (structuredContent.includes('result=')) {
          const resultStart = structuredContent.indexOf('result=') + 'result='.length
          let resultEnd = structuredContent.indexOf(' is_simple_and_unrelevant=')
          if (resultEnd === -1) {
            resultEnd = structuredContent.indexOf(' is_completed=')
          }
          if (resultEnd !== -1) {
            let resultStr = structuredContent.substring(resultStart, resultEnd).trim()
            if (resultStr.startsWith('\'')) {
              resultStr = resultStr.substring(1)
            }
            if (resultStr.endsWith('\'')) {
              resultStr = resultStr.substring(0, resultStr.length - 1)
            }
            // 只显示结果内容
            this.addMessage('ai', `${resultStr}`, data.source, namespace)
            return
          }
        }
        // 如果没有找到结果部分，使用原始内容
        this.addMessage('ai', `${message.content}`, data.source, namespace)
      } else if (message.type === 'tool') {
        // 处理工具消息
        this.addMessage('tool_result', `${message.content}`, data.source, namespace)
      } else {
        // 其他消息类型
        this.addMessage('info', `${message.content}`, data.source, namespace)
      }
    }
    
    // 处理工具调用消息（即使没有content）
    if (message.tool_calls && message.tool_calls.length > 0) {
      message.tool_calls.forEach(toolCall => {
        this.addMessage('tool_call', `${JSON.stringify(toolCall.args)}`, data.source, namespace)
      })
    }
  }
  
  // 添加消息的辅助方法
  addMessage(type, content, source, namespace) {
    this.jsonBuffer += content
    // 直接使用指定的类型，不需要再解析
    this.app.addLog(type, content)
    this.app.currentStream = {
      source: source,
      namespace: namespace,
      content: content
    }
    this.jsonBuffer = ''
  }



  stop() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
  }

  // New handler methods for structured SSE events
  handleMessageDelta(data) {
    if (data.content) {
      let processedContent = this.app.processContentForTodos(data.content)
      if (!processedContent) return

      // 直接添加消息，使用info类型
      this.addMessage('info', processedContent, 'main', [])
    }
  }

  handleMessageComplete(data) {
    if (data.content) {
      // 处理最终消息内容
      this.app.addLog('info', `最终结果: ${data.content}`)
    }
  }

  handleToolCall(data) {
    if (data.tool_call) {
      const toolCall = data.tool_call
      const toolName = toolCall.name || 'unknown'
      const argumentsStr = JSON.stringify(toolCall.arguments || {})
      // Add tool call with wrench icon
      this.app.addLog('tool_call', `调用工具: ${toolName} ${argumentsStr}`)
    }
  }

  handleToolResult(data) {
    if (data.tool_result) {
      const toolResult = data.tool_result
      const toolName = toolResult.name || 'tool'
      const content = toolResult.content || ''
      // Add tool result with toolbox icon
      this.app.addLog('tool_result', `工具结果: ${toolName} ${content}`)
    }
  }

  handleError(data) {
    const errorMessage = data.message || '未知错误'
    this.app.addLog('error', `错误: ${errorMessage}`)
    this.eventSource.close()
    this.app.isRunning = false
    this.app.agentStatus = null
  }
}
