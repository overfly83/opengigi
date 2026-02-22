<template>
  <div class="app">
    <header class="header">
      <h1>自主决策Agent</h1>
      <p>基于deepagents框架的智能助手</p>
    </header>
    
    <main class="main">
      <section class="input-section">
        <h2>设置目标</h2>
        <textarea 
          v-model="goal" 
          placeholder="请输入您的目标，例如：为周末制定一个详细的旅行计划，包括景点、交通和住宿"
          rows="4"
          :disabled="isRunning"
        ></textarea>
        
        <div class="mode-selector">
          <h3>交互模式</h3>
          <div class="radio-group">
            <label>
              <input 
                type="radio" 
                v-model="mode" 
                value="streaming" 
                :disabled="isRunning"
              >
              流式模式 (实时显示)
            </label>
            <label>
              <input 
                type="radio" 
                v-model="mode" 
                value="non-streaming" 
                :disabled="isRunning"
              >
              非流式模式 (完整显示)
            </label>
          </div>
        </div>
        
        <button 
          class="start-btn" 
          @click="startAgent" 
          :disabled="isRunning || !goal.trim()"
        >
          {{ isRunning ? '执行中...' : '开始执行' }}
        </button>
      </section>
      
      <section class="output-section">
        <h2>执行过程</h2>
        <div class="process-container" v-if="isRunning || processLogs.length > 0">
          <div 
            v-for="(log, index) in processLogs" 
            :key="index" 
            class="log-item"
            :class="log.type"
          >
            <span class="log-time">{{ log.time }}</span>
            <span class="log-content">{{ log.content }}</span>
          </div>
          <div class="loading" v-if="isRunning">
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
          </div>
        </div>
        <div class="empty-state" v-else>
          执行结果将显示在这里
        </div>
      </section>
      
      <section class="result-section" v-if="result">
        <h2>执行结果</h2>
        <div class="result-container">
          <div class="result-item">
            <strong>阶段:</strong>
            <p>{{ result.phase }}</p>
          </div>
          <div class="result-item">
            <strong>结果:</strong>
            <p>{{ result.result }}</p>
          </div>
          <div class="result-item">
            <strong>完成状态:</strong>
            <p :class="result.is_completed ? 'completed' : 'pending'">
              {{ result.is_completed ? '完成' : '未完成' }}
            </p>
          </div>
          <div class="result-item" v-if="result.todos && result.todos.length > 0">
            <strong>待办事项:</strong>
            <ul>
              <li v-for="(todo, index) in result.todos" :key="index">
                <span :class="todo.status">{{ todo.content }}</span>
                <span class="todo-status">({{ todo.status }})</span>
              </li>
            </ul>
          </div>
          <div class="result-item" v-else-if="result.todos">
            <strong>待办事项:</strong>
            <p>无待办事项</p>
          </div>
        </div>
      </section>
    </main>
    
    <footer class="footer">
      <p>© 2026 自主决策Agent - 基于deepagents框架</p>
    </footer>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      goal: '',
      mode: 'streaming',
      isRunning: false,
      processLogs: [],
      result: null,
      eventSource: null,
      currentStream: null // 用于存储当前流式会话的信息
    }
  },
  methods: {
    startAgent() {
      if (!this.goal.trim()) return
      
      // 重置状态
      this.processLogs = []
      this.result = null
      this.isRunning = true
      this.currentStream = null
      
      if (this.mode === 'streaming') {
        this.startStreamingMode()
      } else {
        this.startNonStreamingMode()
      }
    },
    
    startStreamingMode() {
      // 流式模式：使用Server-Sent Events
      this.addLog('info', '开始执行自主决策Agent（流式模式）')
      this.addLog('info', `目标: ${this.goal}`)
      
      // 连接到后端的SSE端点
      this.eventSource = new EventSource(`http://localhost:8000/run-agent-stream?goal=${encodeURIComponent(this.goal)}&stream_mode=messages`)
      
      this.eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          this.eventSource.close()
          this.isRunning = false
          return
        }
        
        try {
          const data = JSON.parse(event.data)
          
          // 处理不同类型的流式数据
          if (data.type === 'token') {
            // 处理LLM tokens
            if (!data.content) return // 跳过空内容
            
            const source = data.source === 'main' ? '主Agent' : '子Agent'
            const namespace = typeof data.namespace === 'string' ? ` (${data.namespace})` : 
                           Array.isArray(data.namespace) && data.namespace.length > 0 ? ` (${data.namespace.join(', ')})` : ''
            
            // 检查是否是当前会话的连续内容
            if (this.currentStream && this.currentStream.source === source && this.currentStream.namespace === namespace) {
              // 更新当前会话的内容
              this.currentStream.content += data.content
              
              // 更新最后一条日志
              const lastLogIndex = this.processLogs.length - 1
              if (lastLogIndex >= 0 && this.processLogs[lastLogIndex].type === 'streaming') {
                this.processLogs[lastLogIndex].content = `${source}${namespace}: ${this.currentStream.content}`
              }
            } else {
              // 开始新的会话
              this.currentStream = {
                source: source,
                namespace: namespace,
                content: data.content
              }
              
              // 添加新的流式日志
              this.processLogs.push({
                time: this.getCurrentTime(),
                type: 'streaming',
                content: `${source}${namespace}: ${data.content}`
              })
            }
          } else if (data.type === 'update') {
            // 处理节点更新
            const source = data.source === 'main' ? '主Agent' : '子Agent'
            const namespace = typeof data.namespace === 'string' ? ` (${data.namespace})` : 
                           Array.isArray(data.namespace) && data.namespace.length > 0 ? ` (${data.namespace.join(', ')})` : ''
            
            // 格式化更新数据
            if (typeof data.data === 'object' && data.data !== null) {
              Object.entries(data.data).forEach(([nodeName, nodeData]) => {
                if (nodeName === 'tools') {
                  // 处理工具调用结果
                  if (nodeData.messages) {
                    nodeData.messages.forEach(msg => {
                      if (msg.type === 'tool') {
                        this.addLog('success', `子Agent完成: ${msg.name}`)
                        this.addLog('info', `  结果: ${msg.content}`)
                      }
                    })
                  }
                } else {
                  this.addLog('info', `${source}${namespace}: 步骤: ${nodeName}`)
                }
              })
            }
          } else if (data.type === 'custom') {
            // 处理自定义事件
            const source = data.source === 'main' ? '主Agent' : '子Agent'
            const namespace = typeof data.namespace === 'string' ? ` (${data.namespace})` : 
                           Array.isArray(data.namespace) && data.namespace.length > 0 ? ` (${data.namespace.join(', ')})` : ''
            this.addLog('info', `${source}${namespace}: 自定义事件: ${JSON.stringify(data.event)}`)
          } else if (data.type === 'fallback') {
            // 处理回退结果
            this.result = data.content
          } else {
            // 默认处理
            this.addLog('info', JSON.stringify(data))
          }
        } catch (error) {
          console.error('解析SSE数据失败:', error)
          console.error('原始数据:', event.data)
        }
      }
      
      this.eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error)
        this.eventSource.close()
        this.isRunning = false
        this.addLog('error', '流式连接失败，请重试')
      }
    },
    
    startNonStreamingMode() {
      // 非流式模式：使用普通HTTP请求
      this.addLog('info', '开始执行自主决策Agent（非流式模式）')
      this.addLog('info', `目标: ${this.goal}`)
      this.addLog('info', '正在执行，请稍候...')
      
      // 调用后端的非流式API
      axios.post('http://localhost:8000/run-agent', {
        goal: this.goal,
        mode: 'non-streaming'
      })
      .then(response => {
        if (response.data.success) {
          const resultData = response.data.data
          
          this.addLog('info', `=== ${resultData.phase} 阶段 ===`)
          this.addLog('info', `结果: ${resultData.result}`)
          
          if (resultData.is_completed) {
            this.addLog('success', '\n=== 目标完成 ===')
          } else {
            this.addLog('info', '\n=== 目标进行中 ===')
          }
          
          if (resultData.todos && resultData.todos.length > 0) {
            this.addLog('info', '\n=== 待办事项 ===')
            resultData.todos.forEach(todo => {
              this.addLog(todo.status, `  ${todo.content} (${todo.status})`)
            })
          }
          
          this.result = resultData
        } else {
          this.addLog('error', '执行失败: ' + response.data.message)
        }
        this.isRunning = false
      })
      .catch(error => {
        console.error('API请求失败:', error)
        this.addLog('error', '执行失败，请重试')
        this.isRunning = false
      })
    },
    
    simulateStreamingOutput() {
      // 模拟流式输出
      const steps = [
        { type: 'info', content: '=== 思考阶段 ===' },
        { type: 'info', content: '分析目标: ' + this.goal },
        { type: 'info', content: '思考结果: 正在分析目标的核心诉求和达成条件...' },
        { type: 'info', content: '\n=== 计划阶段 ===' },
        { type: 'info', content: '为目标制定计划: ' + this.goal },
        { type: 'info', content: '生成的计划: 步骤1: 分析目标需求, 步骤2: 制定详细计划, 步骤3: 执行计划, 步骤4: 观察结果, 步骤5: 反思调整' },
        { type: 'info', content: '\n=== 执行阶段 ===' },
        { type: 'info', content: '执行步骤 1: 分析目标需求' },
        { type: 'info', content: '执行结果: 已完成目标需求分析...' },
        { type: 'info', content: '执行步骤 2: 制定详细计划' },
        { type: 'info', content: '执行结果: 已制定详细计划...' },
        { type: 'info', content: '执行步骤 3: 执行计划' },
        { type: 'info', content: '执行结果: 已执行计划中的各项任务...' },
        { type: 'info', content: '执行步骤 4: 观察结果' },
        { type: 'info', content: '执行结果: 已观察并记录执行结果...' },
        { type: 'info', content: '执行步骤 5: 反思调整' },
        { type: 'info', content: '执行结果: 已完成反思和调整...' },
        { type: 'info', content: '\n=== 观察阶段 ===' },
        { type: 'info', content: '观察步骤 1 的执行结果' },
        { type: 'info', content: '观察结果: 执行成功，达到预期目标...' },
        { type: 'info', content: '\n=== 反思阶段 ===' },
        { type: 'info', content: '反思目标执行过程: ' + this.goal },
        { type: 'info', content: '反思结果: 执行过程顺利，所有步骤都已完成...' },
        { type: 'success', content: '\n=== 目标完成 ===' }
      ]
      
      let index = 0
      const interval = setInterval(() => {
        if (index < steps.length) {
          this.addLog(steps[index].type, steps[index].content)
          index++
        } else {
          clearInterval(interval)
          this.isRunning = false
          this.result = {
          phase: 'reflect',
          result: '执行过程顺利，所有步骤都已完成',
          is_completed: true,
          todos: []
        }
        }
      }, 500)
    },
    
    simulateNonStreamingOutput() {
      // 模拟非流式输出
      this.addLog('info', '正在执行，请稍候...')
      
      setTimeout(() => {
        this.processLogs = [
          { time: this.getCurrentTime(), type: 'info', content: '开始执行自主决策Agent（非流式模式）' },
          { time: this.getCurrentTime(), type: 'info', content: `目标: ${this.goal}` },
          { time: this.getCurrentTime(), type: 'info', content: '=== 思考阶段 ===' },
          { time: this.getCurrentTime(), type: 'info', content: '分析目标: ' + this.goal },
          { time: this.getCurrentTime(), type: 'info', content: '思考结果: 已完成目标分析' },
          { time: this.getCurrentTime(), type: 'info', content: '\n=== 计划阶段 ===' },
          { time: this.getCurrentTime(), type: 'info', content: '为目标制定计划: ' + this.goal },
          { time: this.getCurrentTime(), type: 'info', content: '生成的计划: 步骤1: 分析目标需求, 步骤2: 制定详细计划, 步骤3: 执行计划, 步骤4: 观察结果, 步骤5: 反思调整' },
          { time: this.getCurrentTime(), type: 'info', content: '\n=== 执行阶段 ===' },
          { time: this.getCurrentTime(), type: 'info', content: '执行步骤 1-5: 已完成所有步骤' },
          { time: this.getCurrentTime(), type: 'info', content: '\n=== 观察阶段 ===' },
          { time: this.getCurrentTime(), type: 'info', content: '观察结果: 所有步骤执行成功' },
          { time: this.getCurrentTime(), type: 'info', content: '\n=== 反思阶段 ===' },
          { time: this.getCurrentTime(), type: 'info', content: '反思结果: 执行过程顺利，达到预期目标' },
          { time: this.getCurrentTime(), type: 'success', content: '\n=== 目标完成 ===' }
        ]
        
        this.isRunning = false
        this.result = {
          phase: 'reflect',
          result: '执行过程顺利，达到预期目标',
          is_completed: true,
          todos: []
        }
      }, 3000)
    },
    
    addLog(type, content) {
      this.processLogs.push({
        time: this.getCurrentTime(),
        type,
        content
      })
      
      // 自动滚动到底部
      setTimeout(() => {
        const container = document.querySelector('.process-container')
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 100)
    },
    
    getCurrentTime() {
      const now = new Date()
      return now.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background-color: #4a90e2;
  color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.main {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.input-section {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.input-section h2 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
}

.input-section textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 20px;
  font-family: Arial, sans-serif;
}

.mode-selector {
  margin-bottom: 20px;
}

.mode-selector h3 {
  font-size: 1.2rem;
  margin-bottom: 10px;
  color: #555;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.start-btn {
  background-color: #4a90e2;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.start-btn:hover:not(:disabled) {
  background-color: #357abd;
}

.start-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.output-section {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.output-section h2 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
}

.process-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
  max-height: 500px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 0.9rem;
  line-height: 1.5;
}

.log-item {
  margin-bottom: 10px;
  padding: 5px 0;
}

.log-time {
  color: #888;
  margin-right: 10px;
  font-size: 0.8rem;
}

.log-content {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-item.info .log-content {
  color: #333;
}

.log-item.success .log-content {
  color: #27ae60;
  font-weight: bold;
}

.log-item.error .log-content {
  color: #e74c3c;
  font-weight: bold;
}

.log-item.streaming .log-content {
  color: #3498db;
  animation: typing 0.5s ease;
}

@keyframes typing {
  from { opacity: 0.5; }
  to { opacity: 1; }
}

.loading {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background-color: #4a90e2;
  border-radius: 50%;
  animation: pulse 1.5s infinite ease-in-out;
}

.loading-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

.empty-state {
  background-color: #f9f9f9;
  padding: 40px;
  border-radius: 4px;
  text-align: center;
  color: #888;
  font-style: italic;
}

.result-section {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-section h2 {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
}

.result-container {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
}

.result-item {
  margin-bottom: 20px;
}

.result-item strong {
  display: block;
  margin-bottom: 5px;
  color: #555;
}

.result-item ul {
  margin-left: 20px;
}

.result-item li {
  margin-bottom: 5px;
}

.result-item .completed {
  color: #27ae60;
  font-weight: bold;
}

.result-item .pending {
  color: #f39c12;
  font-weight: bold;
}

.result-item .todo-status {
  margin-left: 10px;
  font-size: 0.8rem;
  color: #888;
}

.result-item .success {
  color: #27ae60;
  font-weight: bold;
}

.result-item .fail {
  color: #e74c3c;
  font-weight: bold;
}

.footer {
  text-align: center;
  margin-top: 40px;
  padding: 20px;
  background-color: #f5f5f5;
  color: #888;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .app {
    padding: 10px;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .main {
    gap: 20px;
  }
  
  .input-section,
  .output-section,
  .result-section {
    padding: 20px;
  }
  
  .radio-group {
    flex-direction: column;
    gap: 10px;
  }
}
</style>