<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-gradient-to-r from-primary to-secondary shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-center md:text-left mb-4 md:mb-0">
            <h1 class="text-2xl md:text-3xl font-bold text-white mb-2">
              自主决策Agent
            </h1>
            <p class="text-white text-opacity-90">
              基于deepagents框架的智能助手
            </p>
          </div>
          <div class="flex items-center space-x-2">
            <button class="btn bg-white text-primary hover:bg-gray-100">
              <i class="fas fa-question-circle mr-1"></i>
              帮助
            </button>
            <button class="btn bg-white text-primary hover:bg-gray-100">
              <i class="fas fa-cog mr-1"></i>
              设置
            </button>
          </div>
        </div>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
      <div class="flex flex-col lg:flex-row gap-4" id="main-container">
        <!-- Left Sidebar with Resize Handle -->
        <div class="lg:w-1/4 space-y-6 resizeable-sidebar" ref="sidebarRef" :style="{ width: sidebarWidth + 'px' }">
          <!-- Todo List Component -->
          <div class="card shadow-lg">
            <TodoList :todos="todos" />
          </div>
          
          <!-- Memory Component -->
          <div class="card shadow-lg">
            <MemoryComponent />
          </div>
          
          <!-- Resize Handle -->
          <div class="resize-handle right-handle" @mousedown="startResize('sidebar', $event)"></div>
        </div>
        
        <!-- Right Content -->
        <div class="lg:flex-1 space-y-6 flex-1" :style="{ width: 'calc(100% - ' + (sidebarWidth + 16) + 'px)' }">
          <!-- Input Section -->
          <div class="card shadow-lg">
            <h2 class="text-xl font-semibold mb-6 flex items-center">
              <i class="fas fa-bullseye mr-2 text-primary"></i>
              设置目标
            </h2>
            
            <textarea 
              v-model="goal" 
              placeholder="请输入您的目标，例如：为周末制定一个详细的旅行计划，包括景点、交通和住宿"
              rows="4"
              :disabled="isRunning"
              class="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary transition-all duration-300"
            ></textarea>
            
            <div class="mt-6 mb-8">
              <h3 class="text-md font-medium text-gray-700 mb-3">交互模式</h3>
              <div class="flex flex-col sm:flex-row gap-4">
                <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer transition-all duration-300 hover:border-primary"
                       :class="{ 'border-primary bg-primary bg-opacity-5': mode === 'streaming' }">
                  <input 
                    type="radio" 
                    v-model="mode" 
                    value="streaming" 
                    :disabled="isRunning"
                    class="mr-3 accent-primary"
                  >
                  <div>
                    <div class="font-medium">流式模式</div>
                    <div class="text-sm text-gray-500">实时显示执行过程</div>
                  </div>
                </label>
                <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer transition-all duration-300 hover:border-primary"
                       :class="{ 'border-primary bg-primary bg-opacity-5': mode === 'non-streaming' }">
                  <input 
                    type="radio" 
                    v-model="mode" 
                    value="non-streaming" 
                    :disabled="isRunning"
                    class="mr-3 accent-primary"
                  >
                  <div>
                    <div class="font-medium">非流式模式</div>
                    <div class="text-sm text-gray-500">完整显示执行结果</div>
                  </div>
                </label>
              </div>
            </div>
            
            <button 
              class="btn btn-primary w-full py-3 text-lg font-medium"
              @click="startAgent" 
              :disabled="isRunning || !goal.trim()"
            >
              <template v-if="isRunning">
                <i class="fas fa-spinner fa-spin mr-2"></i>
                执行中...
              </template>
              <template v-else>
                <i class="fas fa-play mr-2"></i>
                开始执行
              </template>
            </button>
          </div>
          
          <!-- Output Section -->
          <div class="card shadow-lg">
            <h2 class="text-xl font-semibold mb-6 flex items-center">
              <i class="fas fa-stream mr-2 text-primary"></i>
              执行过程
            </h2>
            
            <div v-if="isRunning || processLogs.length > 0" class="relative">
              <div class="process-container max-h-96 overflow-y-auto p-4 bg-gray-50 rounded-lg">
                <div 
                  v-for="(log, index) in processLogs" 
                  :key="index" 
                  class="log-item"
                  :class="'log-item-' + log.type"
                >
                  <div class="flex items-start">
                    <span class="text-xs text-gray-500 mr-3 mt-1 whitespace-nowrap">{{ log.time }}</span>
                    <span class="flex-1 text-sm">{{ log.content }}</span>
                  </div>
                </div>
                
                <div class="loading flex items-center mt-4" v-if="isRunning">
                  <span class="loading-dot w-2 h-2 bg-primary rounded-full mr-1"></span>
                  <span class="loading-dot w-2 h-2 bg-primary rounded-full mr-1"></span>
                  <span class="loading-dot w-2 h-2 bg-primary rounded-full"></span>
                  <span class="ml-2 text-sm text-gray-500">执行中...</span>
                </div>
              </div>
              
              <!-- Scroll to bottom button -->
              <button 
                v-if="processLogs.length > 10"
                class="absolute bottom-4 right-4 bg-white p-2 rounded-full shadow-md text-gray-600 hover:text-primary transition-colors duration-300"
                @click="scrollToBottom"
              >
                <i class="fas fa-arrow-down"></i>
              </button>
            </div>
            
            <div v-else class="empty-state p-8 bg-gray-50 rounded-lg flex flex-col items-center justify-center">
              <i class="fas fa-terminal text-3xl text-gray-300 mb-3"></i>
              <p class="text-gray-500">执行结果将显示在这里</p>
            </div>
          </div>
          
          <!-- Result Section -->
          <div class="card shadow-lg" v-if="result">
            <h2 class="text-xl font-semibold mb-6 flex items-center">
              <i class="fas fa-flag-checkered mr-2 text-primary"></i>
              执行结果
            </h2>
            
            <div class="result-container space-y-4">
              <div class="p-4 bg-gray-50 rounded-lg">
                <div class="font-medium text-gray-700 mb-2">阶段:</div>
                <div class="text-lg">{{ result.phase }}</div>
              </div>
              
              <div class="p-4 bg-gray-50 rounded-lg">
                <div class="font-medium text-gray-700 mb-2">结果:</div>
                <div class="text-lg whitespace-pre-wrap">{{ result.result }}</div>
              </div>
              
              <div class="p-4 bg-gray-50 rounded-lg">
                <div class="font-medium text-gray-700 mb-2">完成状态:</div>
                <div 
                  class="text-lg font-medium" 
                  :class="result.is_completed ? 'text-success' : 'text-warning'"
                >
                  {{ result.is_completed ? '完成' : '未完成' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p>© 2026 自主决策Agent - 基于deepagents框架</p>
          </div>
          <div class="flex space-x-4">
            <a href="#" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-github text-xl"></i>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-twitter text-xl"></i>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-linkedin text-xl"></i>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios'
import TodoList from './components/TodoList.vue'
import MemoryComponent from './components/MemoryComponent.vue'

export default {
  name: 'App',
  components: {
    TodoList,
    MemoryComponent
  },
  data() {
    return {
      goal: '',
      mode: 'streaming',
      isRunning: false,
      processLogs: [],
      result: null,
      eventSource: null,
      currentStream: null, // 用于存储当前流式会话的信息
      todos: [], // 用于存储todo列表
      sidebarWidth: 320, // 默认侧边栏宽度
      isResizing: false,
      resizeType: null,
      startX: 0
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
      this.todos = [] // 重置todos数组
      
      if (this.mode === 'streaming') {
        this.startStreamingMode()
      } else {
        this.startNonStreamingMode()
      }
    },
    
    scrollToBottom() {
      const container = document.querySelector('.process-container')
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    processContentForTodos(content) {
      // Check if content contains todo update
      if (content.includes('Updated todo list to ')) {
        // Extract the todo list part
        const startIdx = content.indexOf('Updated todo list to ') + 'Updated todo list to '.length;
        // Find the end of the todo list (matching closing bracket)
        let bracketCount = 0;
        let endIdx = startIdx;
        for (let i = startIdx; i < content.length; i++) {
          if (content[i] === '[') {
            bracketCount++;
          } else if (content[i] === ']') {
            bracketCount--;
            if (bracketCount === 0) {
              endIdx = i + 1;
              break;
            }
          }
        }
        // Extract the todo list string
        const todoListStr = content.substring(startIdx, endIdx);
        // Try to parse the todo list
        try {
          // Replace single quotes with double quotes to make it valid JSON
          const validJsonStr = todoListStr.replace(/'/g, '"');
          const todos = JSON.parse(validJsonStr);
          // Update the todos array
          this.todos = todos;
          // Return the remaining content
          return content.substring(endIdx).trim();
        } catch (error) {
          console.error('Failed to parse todo list:', error);
          // If parsing fails, return the original content
          return content;
        }
      }
      // If no todo update, return original content
      return content;
    },

    updateTodoListOnCompletion() {
      // Check if there are any todos
      if (!this.todos || this.todos.length === 0) {
        return;
      }
      
      // Find the last in-progress step
      let lastInProgressIndex = -1;
      for (let i = this.todos.length - 1; i >= 0; i--) {
        if (this.todos[i].status === 'in_progress') {
          lastInProgressIndex = i;
          break;
        }
      }
      
      // If there's an in-progress step
      if (lastInProgressIndex !== -1) {
        // Create a copy of the todos array to modify
        const updatedTodos = [...this.todos];
        
        // Mark the last in-progress step as completed
        updatedTodos[lastInProgressIndex].status = 'completed';
        
        // If it's not the last step, mark subsequent steps as skipped
        if (lastInProgressIndex < updatedTodos.length - 1) {
          for (let i = lastInProgressIndex + 1; i < updatedTodos.length; i++) {
            updatedTodos[i].status = 'skipped';
          }
        }
        
        // Update the todos array
        this.todos = updatedTodos;
      }
    },

    // Resize-related methods
    startResize(type, event) {
      this.isResizing = true;
      this.resizeType = type;
      this.startX = event.clientX;
      
      // Add event listeners for mouse move and mouse up
      document.addEventListener('mousemove', this.resize);
      document.addEventListener('mouseup', this.stopResize);
      
      // Prevent default behavior
      event.preventDefault();
    },

    resize(event) {
      if (!this.isResizing) return;
      
      const deltaX = event.clientX - this.startX;
      
      if (this.resizeType === 'sidebar') {
        // Calculate new width with minimum and maximum constraints
        let newWidth = this.sidebarWidth + deltaX;
        
        // Minimum width: 200px
        newWidth = Math.max(200, newWidth);
        
        // Maximum width: 50% of container
        const containerWidth = document.getElementById('main-container').offsetWidth;
        newWidth = Math.min(containerWidth * 0.5, newWidth);
        
        this.sidebarWidth = newWidth;
        this.startX = event.clientX;
      }
    },

    stopResize() {
      this.isResizing = false;
      this.resizeType = null;
      
      // Remove event listeners
      document.removeEventListener('mousemove', this.resize);
      document.removeEventListener('mouseup', this.stopResize);
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
            
            // Update todo list on completion
            this.updateTodoListOnCompletion();
            
            // 处理完成后，从日志中提取最终结果
            let finalResult = ''
            for (let i = this.processLogs.length - 1; i >= 0; i--) {
                const log = this.processLogs[i]
                if (log.content && log.content.startsWith('主Agent (()): ')) {
                    finalResult = log.content.replace('主Agent (()): ', '')
                    break;
                }
            }
            
            // 设置结果对象
            if (finalResult) {
                this.result = {
                    phase: 'reflect',
                    result: finalResult,
                    is_completed: true,
                    todos: this.todos
                }
            }
            
            return
        }
        
        try {
            const data = JSON.parse(event.data)
            
            // 处理不同类型的流式数据
            if (data.type === 'token') {
                // 处理LLM tokens
                if (!data.content) return // 跳过空内容
                
                // Process content to extract todos
                let processedContent = this.processContentForTodos(data.content);
                if (!processedContent) return; // Skip if all content was todo update
                
                const source = data.source === 'main' ? '主Agent' : '子Agent'
                const namespace = typeof data.namespace === 'string' ? ` (${data.namespace})` : 
                               Array.isArray(data.namespace) && data.namespace.length > 0 ? ` (${data.namespace.join(', ')})` : ''
                
                // 检查是否是当前会话的连续内容
                if (this.currentStream && this.currentStream.source === source && this.currentStream.namespace === namespace) {
                    // 更新当前会话的内容
                    this.currentStream.content += processedContent
                    
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
                        content: processedContent
                    }
                    
                    // 添加新的流式日志
                    this.processLogs.push({
                        time: this.getCurrentTime(),
                        type: 'streaming',
                        content: `${source}${namespace}: ${this.currentStream.content}`
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
            } else if (data.type === 'final_status') {
                // 处理最终状态更新
                this.todos = data.todos || []
                
                // 更新结果对象
                this.result = {
                    phase: 'reflect',
                    result: data.content || '执行完成',
                    is_completed: data.is_completed,
                    todos: this.todos
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
                
                // 检查是否是新的消息格式
                if (resultData.messages && Array.isArray(resultData.messages)) {
                    // 显示所有消息
                    let finalAiMessage = null
                    
                    for (const message of resultData.messages) {
                        if (message.type === 'human') {
                            // 人类消息
                            this.addLog('info', `用户: ${message.content}`)
                        } else if (message.type === 'ai') {
                            // AI消息
                            if (message.tool_calls && message.tool_calls.length > 0) {
                                // 工具调用
                                this.addLog('info', `主Agent (()): ${message.content || '正在调用工具...'}`)
                                for (const toolCall of message.tool_calls) {
                                    if (toolCall.function) {
                                        const funcName = toolCall.function.name
                                        let args = {}
                                        try {
                                            args = JSON.parse(toolCall.function.arguments)
                                            // 检查是否有todos
                                            if (args.todos) {
                                                this.todos = args.todos
                                            }
                                        } catch (e) {
                                            args = toolCall.function.arguments
                                        }
                                        this.addLog('info', `  调用工具: ${funcName} ${JSON.stringify(args)}`)
                                    }
                                }
                            } else {
                                // 普通回复
                                this.addLog('info', `主Agent (()): ${message.content}`)
                                finalAiMessage = message
                            }
                        } else if (message.type === 'tool') {
                            // 工具结果
                            this.addLog('info', `工具 ${message.name}: ${message.content}`)
                        }
                    }
                    
                    // 显示结果
                    this.addLog('info', `=== reflect 阶段 ===`)
                    this.addLog('info', `结果: ${finalAiMessage ? finalAiMessage.content : '执行完成'}`)
                    this.addLog('success', '\n=== 目标完成 ===')
                    
                    // 构建结果对象
                    this.result = {
                        phase: 'reflect',
                        result: finalAiMessage ? finalAiMessage.content : '执行完成',
                        is_completed: true,
                        todos: this.todos
                    }
                } else {
                    // 旧格式处理
                    this.addLog('info', `=== ${resultData.phase} 阶段 ===`)
                    this.addLog('info', `结果: ${resultData.result}`)
                    
                    if (resultData.is_completed) {
                        this.addLog('success', '\n=== 目标完成 ===')
                    } else {
                        this.addLog('info', '\n=== 目标进行中 ===')
                    }
                    
                    if (resultData.todos && resultData.todos.length > 0) {
                        this.todos = resultData.todos
                        this.addLog('info', '\n=== 待办事项 ===')
                        resultData.todos.forEach(todo => {
                            this.addLog(todo.status, `  ${todo.content} (${todo.status})`)
                        })
                    }
                    
                    this.result = resultData
                }
            } else {
                this.addLog('error', '执行失败: ' + response.data.message)
            }
            // Update todo list on completion
            this.updateTodoListOnCompletion();
            
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

/* Resize handle styles */
.resizeable-sidebar {
  position: relative;
  min-width: 200px;
  max-width: 50%;
}

.resize-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: col-resize;
  transition: all 0.2s ease;
  z-index: 10;
}

.right-handle {
  right: -3px;
}

.resize-handle:hover {
  background-color: rgba(74, 144, 226, 0.3);
}

.resize-handle:active {
  background-color: rgba(74, 144, 226, 0.6);
}

/* Custom cursor during resize */
body.resize-active {
  cursor: col-resize;
  user-select: none;
}
</style>