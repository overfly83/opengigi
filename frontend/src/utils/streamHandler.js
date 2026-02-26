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

    this.eventSource = new EventSource(`http://localhost:8000/run-agent-stream?goal=${encodeURIComponent(this.app.goal)}&stream_mode=messages`)

    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.handleStreamDone()
        return
      }

      try {
        const data = JSON.parse(event.data)
        this.handleStreamData(data)
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
      this.processJsonBuffer('done', 'done')
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
      if (log.content && log.content.startsWith('主Agent (()): ')) {
        let content = log.content.replace('主Agent (()): ', '')
        
        if (content.includes('Returning structured response:')) {
          const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length
          let structuredContent = content.substring(structuredStart).trim()
          
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
              finalResult = resultStr
              break
            }
          }
        } else {
          finalResult = content
          break
        }
      }
    }
    return finalResult
  }

  handleStreamData(data) {
    if (data.type === 'token') {
      if (!data.content) return

      let processedContent = this.app.processContentForTodos(data.content)
      if (!processedContent) return

      if (data.content.includes('Updated todo list to ')) {
        this.chunkCacheManager.initialize(this.app.todos)
      }

      // 处理 JSON 对象的边界检测
      this.jsonBuffer += processedContent
      this.processJsonBuffer(data.source, data.namespace)
    }
  }

  processJsonBuffer(source, namespace) {
    let buffer = this.jsonBuffer
    let startIndex = buffer.indexOf('{')
    
    // 处理非 JSON 内容（如最终答案和计算步骤）
    if (startIndex === -1 && buffer.length > 0) {
      // 检测任务索引
      const detectedTaskIndex = this.chunkCacheManager.detectTaskFromChunk(buffer)
      
      if (detectedTaskIndex !== -1 && detectedTaskIndex !== this.chunkCacheManager.cache.currentTaskIndex) {
        this.chunkCacheManager.flushCachedChunks(this.chunkCacheManager.cache.currentTaskIndex)
        this.chunkCacheManager.cache.currentTaskIndex = detectedTaskIndex
      } else {
        this.chunkCacheManager.cacheChunk(buffer)
      }
      
      // 为非 JSON 内容创建一个新的流
      this.app.addLog('streaming', buffer)
      this.app.currentStream = {
        source: source,
        namespace: namespace,
        content: buffer
      }
      
      // 清空缓冲区
      this.jsonBuffer = ''
      return
    }
    
    while (startIndex !== -1) {
      let bracketCount = 1
      let endIndex = startIndex + 1
      
      // 寻找匹配的闭合括号
      while (endIndex < buffer.length && bracketCount > 0) {
        if (buffer[endIndex] === '{') {
          bracketCount++
        } else if (buffer[endIndex] === '}') {
          bracketCount--
        }
        endIndex++
      }
      
      // 如果找到完整的 JSON 对象
      if (bracketCount === 0) {
        const jsonObject = buffer.substring(startIndex, endIndex)
        
        // 检测任务索引
        const detectedTaskIndex = this.chunkCacheManager.detectTaskFromChunk(jsonObject)
        
        if (detectedTaskIndex !== -1 && detectedTaskIndex !== this.chunkCacheManager.cache.currentTaskIndex) {
          this.chunkCacheManager.flushCachedChunks(this.chunkCacheManager.cache.currentTaskIndex)
          this.chunkCacheManager.cache.currentTaskIndex = detectedTaskIndex
        } else {
          this.chunkCacheManager.cacheChunk(jsonObject)
        }
        
        // 为每个 JSON 对象创建一个新的流
        this.app.addLog('streaming', jsonObject)
        this.app.currentStream = {
          source: source,
          namespace: namespace,
          content: jsonObject
        }
        
        // 移除已处理的 JSON 对象
        buffer = buffer.substring(endIndex)
        startIndex = buffer.indexOf('{')
      } else {
        // 未找到完整的 JSON 对象，等待更多数据
        break
      }
    }
    
    // 更新缓冲区
    this.jsonBuffer = buffer
  }

  stop() {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
  }
}
