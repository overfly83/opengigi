import axios from 'axios'
import { ChunkCacheManager } from './chunkCacheManager'
import { MessageType, normalizeMessageType } from './messageTypes'

export class StreamHandler {
  constructor(app) {
    this.app = app
    this.eventSource = null
    this.chunkCacheManager = new ChunkCacheManager(app)
    this.jsonBuffer = ''
  }

  startStreamingMode() {
    this.app.addLog(MessageType.SYSTEM, '开始执行自主决策Agent（流式模式）')
    this.app.addLog(MessageType.SYSTEM, `目标: ${this.app.goal}`)
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
        
        // 根据消息类型统一处理
        const messageType = normalizeMessageType(data.type)
        
        switch (messageType) {
          case MessageType.MESSAGE_DELTA:
            this.handleMessageDelta(data)
            break
          case MessageType.MESSAGE_COMPLETE:
            this.handleMessageComplete(data)
            break
          case MessageType.TOOL_CALL:
            this.handleToolCall(data)
            break
          case MessageType.TOOL_RESULT:
            this.handleToolResult(data)
            break
          case MessageType.ERROR:
            this.handleError(data)
            break
          default:
            // 处理其他消息类型
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
      this.app.addLog(MessageType.ERROR, '流式连接失败，请重试')
    }
  }

  handleStreamDone() {
    this.eventSource.close()
    this.app.isRunning = false
    this.app.agentStatus = null // 清除状态

    // 处理缓冲区中剩余的内容
    if (this.jsonBuffer.length > 0) {
      // 直接添加剩余内容作为系统类型消息
      this.addMessage(MessageType.SYSTEM, this.jsonBuffer, 'done', 'done')
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
    // 根据统一的消息类型处理
    const messageType = normalizeMessageType(data.type)
    
    switch (messageType) {
      case MessageType.AI:
        this._handleAiMessage(data)
        break
      case MessageType.TOOL_CALL:
        this._handleToolCallMessage(data)
        break
      case MessageType.TOOL_RESULT:
        this._handleToolResultMessage(data)
        break
      case MessageType.STREAMING:
        this._handleStreamingMessage(data)
        break
      case MessageType.SYSTEM:
        this._handleSystemMessage(data)
        break
      case MessageType.ERROR:
        this._handleErrorMessage(data)
        break
      default:
        this._handleDefaultMessage(data)
    }
  }

  _handleAiMessage(data) {
    if (!data.content) return

    let processedContent = this.app.processContentForTodos(data.content)
    if (!processedContent) return

    if (data.content.includes('Updated todo list to ')) {
      this.chunkCacheManager.initialize(this.app.todos)
    }

    this.addMessage(MessageType.AI, processedContent, data.source, data.namespace)
  }

  _handleToolCallMessage(data) {
    if (!data.content) return

    this.addMessage(MessageType.TOOL_CALL, `调用工具: ${data.content}`, data.source, data.namespace)
  }

  _handleToolResultMessage(data) {
    if (!data.content) return

    this.addMessage(MessageType.TOOL_RESULT, `工具结果: ${data.content}`, data.source, data.namespace, data.tool_name)
  }

  _handleStreamingMessage(data) {
    // 处理流式消息
    if (data.data && data.data.model && data.data.model.structured_response) {
      const structuredResponse = data.data.model.structured_response
      if (structuredResponse.result) {
        this.addMessage(MessageType.AI, `主Agent (${data.namespace}): ${structuredResponse.result}`, data.source, data.namespace)
      }
    }

    if (data.data && data.data.model && data.data.model.messages) {
      data.data.model.messages.forEach(message => {
        if (message.content) {
          if (message.content.includes('Returning structured response:')) {
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
                this.addMessage(MessageType.TOOL_RESULT, `${resultStr}`, data.source, data.namespace)
                return
              }
            }
            this.addMessage(MessageType.TOOL_RESULT, `${message.content}`, data.source, data.namespace)
          } else {
            this.addMessage(MessageType.AI, `${message.content}`, data.source, data.namespace)
          }
        }
      })
    }

    if (data.data && data.data.tools && data.data.tools.messages) {
      data.data.tools.messages.forEach(message => {
        if (message.content) {
          this.addMessage(MessageType.TOOL_RESULT, `工具 (${data.namespace}): ${message.content}`, data.source, data.namespace)
        }
      })
    }
  }

  _handleSystemMessage(data) {
    if (!data.content) return

    this.addMessage(MessageType.SYSTEM, `系统: ${data.content}`, data.source, data.namespace)
  }

  _handleErrorMessage(data) {
    if (!data.content) return

    this.addMessage(MessageType.ERROR, `错误: ${data.content}`, data.source, data.namespace)
  }

  _handleDefaultMessage(data) {
    if (!data.content) return

    this.addMessage(MessageType.SYSTEM, data.content, data.source, data.namespace)
  }
  
  // 添加消息的辅助方法
  addMessage(type, content, source, namespace, toolName = null) {
    this.jsonBuffer += content
    // 直接使用指定的类型，不需要再解析
    // 处理换行符，确保\n被转换为\n
    const processedContent = content.replace(/\\n/g, '\n')
    const logItem = {
      type: type,
      content: processedContent,
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false })
    }
    // 添加tool_name字段（如果有）
    if (toolName) {
      logItem.tool_name = toolName
    }
    // 使用app的addLog方法添加消息
    this.app.processLogs.push(logItem)
    this.app.$nextTick(() => {
      this.app.scrollToBottom()
    })
    this.app.currentStream = {
      source: source,
      namespace: namespace,
      content: processedContent
    }
    this.jsonBuffer = ''
  }

  stop() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
  }

  // 处理结构化SSE事件
  handleMessageDelta(data) {
    if (data.content) {
      let processedContent = this.app.processContentForTodos(data.content)
      if (!processedContent) return

      // 直接添加消息，使用AI类型
      this.addMessage(MessageType.AI, processedContent, 'main', [])
    }
  }

  handleMessageComplete(data) {
    if (data.content) {
      // 处理最终消息内容
      this.app.addLog(MessageType.SYSTEM, `最终结果: ${data.content}`)
    }
  }

  handleToolCall(data) {
    if (data.tool_calls) {
      // 处理工具调用
      const toolCalls = Array.isArray(data.tool_calls) ? data.tool_calls : [data.tool_calls]
      toolCalls.forEach(toolCall => {
        const toolName = toolCall.name || toolCall.function || 'unknown'
        const argumentsStr = JSON.stringify(toolCall.args || toolCall.arguments || {})
        this.addMessage(MessageType.TOOL_CALL, `调用工具: ${toolName} ${argumentsStr}`, 'main', [])
      })
    } else if (data.content) {
      // 兼容旧格式
      this.addMessage(MessageType.TOOL_CALL, `调用工具: ${data.content}`, 'main', [])
    }
  }

  handleToolResult(data) {
    if (data.tool_result) {
      const toolResult = data.tool_result
      const toolName = toolResult.name || 'tool'
      const content = toolResult.content || ''
      this.addMessage(MessageType.TOOL_RESULT, `工具结果: ${content}`, 'main', [], toolName)
    } else if (data.content) {
      // 兼容旧格式
      this.addMessage(MessageType.TOOL_RESULT, `工具结果: ${data.content}`, 'main', [], data.tool_name)
    }
  }

  handleError(data) {
    const errorMessage = data.error || data.message || '未知错误'
    this.addMessage(MessageType.ERROR, `错误: ${errorMessage}`, 'main', [])
    this.eventSource.close()
    this.app.isRunning = false
    this.app.agentStatus = null
  }
}

