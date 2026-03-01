<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg">
      <div class="container mx-auto px-4 py-3">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="flex items-center mb-2 md:mb-0">
            <div class="w-8 h-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center mr-2">
              <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div>
              <h1 class="text-lg font-bold text-white">GiGi</h1>
              <p class="text-[9px] text-white text-opacity-80">Based on deepagents framework</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <div v-if="agentStatus" class="flex items-center bg-white bg-opacity-20 px-2 py-0.5 rounded-full">
              <div class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse mr-1.5"></div>
              <span class="text-white text-xs">{{ agentStatus }}</span>
            </div>
            <div class="flex items-center bg-white bg-opacity-20 px-2 py-0.5 rounded-full relative" :title="'Session UUID: ' + sessionUuid">
              <span class="text-white text-xs truncate max-w-[120px]">Session: {{ sessionUuid.slice(0, 8) }}...</span>
            </div>
            <div class="flex items-center bg-white bg-opacity-20 px-2 py-0.5 rounded-full">
              <span class="text-white text-xs">User: </span>
              <input 
                v-model="userId" 
                class="bg-transparent border-none text-white text-xs focus:outline-none w-20" 
                placeholder="user1"
              >
            </div>
            <button class="btn bg-white text-blue-600 hover:bg-gray-100 text-xs px-2 py-1" @click="showHelp = true">
              <i class="fas fa-question-circle mr-1"></i>
              Help
            </button>
            <button class="btn bg-white text-blue-600 hover:bg-gray-100 text-xs px-2 py-1" @click="showHistory = true">
              <i class="fas fa-history mr-1"></i>
              History
            </button>
            <button class="btn bg-white text-blue-600 hover:bg-gray-100 text-xs px-2 py-1" @click="showSettings = true">
              <i class="fas fa-cog mr-1"></i>
              Settings
            </button>
          </div>
        </div>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6 flex-1 flex flex-col overflow-hidden">
      <div class="flex flex-col lg:flex-row gap-4 flex-1 h-full overflow-hidden">
        <!-- Left Sidebar with Resize Handle -->
        <div class="lg:w-1/4 resizeable-sidebar flex flex-col gap-4 overflow-hidden h-full" ref="sidebarRef" :style="{ width: sidebarWidth + 'px' }">
          <!-- Todo List Component -->
          <div class="card shadow-lg overflow-auto" style="flex: 0 1 auto; min-height: 120px; max-height: 40%;">
            <TodoList :todos="todos" />
          </div>
          
          <!-- Memory Component -->
          <div class="card shadow-lg overflow-auto" style="flex: 1 0 60%; min-height: 400px;">
            <MemoryComponent 
            :userId="userId" 
            :currentSessionUuid="sessionUuid"
            @load-thread="handleLoadThread"
            @thread-deleted="handleThreadDeleted"
          />
            <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <button 
                @click="startNewConversation"
                class="w-full btn bg-blue-600 text-white hover:bg-blue-700 text-xs py-2 flex items-center justify-center"
              >
                <i class="fas fa-plus mr-1"></i>
                New Conversation
              </button>
            </div>
          </div>
          
          <!-- Resize Handle -->
          <!-- <div class="resize-handle right-handle" @mousedown="startResize('sidebar', $event)"></div> -->
        </div>
        
        <!-- Right Content -->
        <div class="lg:flex-1 space-y-4 flex-1 flex flex-col overflow-hidden" :style="{ width: 'calc(100% - ' + (sidebarWidth + 16) + 'px)' }">
          <!-- Input Section -->
          <div class="card shadow-lg">
            <h2 class="text-base font-semibold mb-3 flex items-center">
              <i class="fas fa-bullseye mr-2 text-blue-600"></i>
              Set Goal
            </h2>
            
            <textarea 
              v-model="goal" 
              placeholder="Enter your goal, e.g., Create a detailed weekend travel plan including attractions, transportation, and accommodation"
              rows="2"
              :disabled="isRunning"
              class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600 transition-all duration-300 text-sm"
            ></textarea>
            
            <div class="mt-2 mb-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div class="flex space-x-2">
                <label class="flex items-center justify-center p-2 border border-gray-300 rounded-md cursor-pointer transition-all duration-300 hover:border-blue-600" 
                       :class="{ 'border-blue-600 bg-blue-50': mode === 'streaming' }"
                       title="Streaming mode - Display execution process in real-time">
                  <input 
                    type="radio" 
                    v-model="mode" 
                    value="streaming" 
                    :disabled="isRunning"
                    class="hidden"
                  >
                  <i class="fas fa-water text-sm text-gray-600" :class="{ 'text-blue-600': mode === 'streaming' }"></i>
                </label>
                <label class="flex items-center justify-center p-2 border border-gray-300 rounded-md cursor-pointer transition-all duration-300 hover:border-blue-600" 
                       :class="{ 'border-blue-600 bg-blue-50': mode === 'non-streaming' }"
                       title="Non-streaming mode - Display complete execution result">
                  <input 
                    type="radio" 
                    v-model="mode" 
                    value="non-streaming" 
                    :disabled="isRunning"
                    class="hidden"
                  >
                  <i class="fas fa-bolt text-sm text-gray-600" :class="{ 'text-blue-600': mode === 'non-streaming' }"></i>
                </label>
              </div>
              
              <div class="flex items-center space-x-2 flex-1 sm:flex-none">
          <button 
            class="btn btn-primary py-2 px-4 text-sm font-medium"
            :disabled="isRunning || !goal.trim()"
            @click="startAgent"
          >
            <i class="fas fa-play mr-1 text-sm"></i>
            {{ isRunning ? 'Running...' : 'Start Execution' }}
          </button>
        </div>
            </div>
          </div>

          <!-- Result Section -->
          <div class="card shadow-lg" v-if="result">
            <h2 class="text-base font-semibold mb-3 flex items-center">
              <i class="fas fa-flag-checkered mr-2 text-blue-600"></i>
              Execution Result
            </h2>
            
            <div class="p-3 bg-gray-50 rounded-lg">
              <div class="whitespace-pre-wrap text-sm leading-relaxed">{{ formattedResult }}</div>
            </div>
          </div>

          <!-- Process Section -->
          <div class="card shadow-lg flex-1 flex flex-col min-h-0">
            <h2 class="text-base font-semibold mb-3 flex items-center">
              <i class="fas fa-stream mr-2 text-blue-600"></i>
              Execution Process
            </h2>
            
            <!-- Progress Bar -->
            <div v-if="isRunning" class="mb-3">
              <div class="flex justify-between text-xs mb-1">
                <span>Progress</span>
                <span>{{ Math.round(progress) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out" 
                  :style="{ width: progress + '%' }"
                ></div>
              </div>
            </div>
            
            <div class="process-container overflow-y-auto p-3 bg-gray-50 rounded-lg" ref="processContainer" style="height: calc(100% - 32px); min-height: 400px;">
              <div v-for="(log, index) in processLogs" :key="index" 
                   :class="['p-2 mb-1 rounded-lg', log.type === 'info' ? 'bg-blue-50' : 
                           log.type === 'success' ? 'bg-green-50' : 
                           log.type === 'error' ? 'bg-red-50' : 
                           log.type === 'streaming' ? 'bg-gray-100' : '']">
                <div class="flex items-start">
                  <i class="fas fa-info-circle mt-1 mr-2 text-blue-500" v-if="log.type === 'info' "></i>
                  <i class="fas fa-check-circle mt-1 mr-2 text-green-500" v-else-if="log.type === 'success'"></i>
                  <i class="fas fa-times-circle mt-1 mr-2 text-red-500" v-else-if="log.type === 'error'"></i>
                  <i class="fas fa-play-circle mt-1 mr-2 text-gray-500" v-else-if="log.type === 'streaming' "></i>
                  <div class="flex-1">
                    <div class="text-xs text-gray-500 mb-1">{{ log.timestamp }}</div>
                    <div class="text-xs whitespace-pre-wrap">{{ log.content }}</div>
                  </div>
                </div>
              </div>
              <div v-if="processLogs.length === 0" class="flex flex-col items-center justify-center h-full text-gray-500">
                <i class="fas fa-clipboard-list text-xl mb-2"></i>
                <p class="text-xs">No execution logs</p>
              </div>
              <div v-if="isRunning" class="flex justify-center items-center py-3">
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gradient-to-r from-blue-800 to-indigo-900 text-white py-3 mt-4">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-center md:text-left mb-2 md:mb-0">
            <p class="text-xs">© 2026 Autonomous Decision Agent - Based on deepagents framework</p>
          </div>
          <div class="flex space-x-3">
            <a href="https://github.com/overfly83/opengigi" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-github text-sm"></i>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-twitter text-sm"></i>
            </a>
            <a href="#" class="text-gray-300 hover:text-white transition-colors duration-300">
              <i class="fab fa-linkedin text-sm"></i>
            </a>
          </div>
        </div>
      </div>
    </footer>

    <!-- Settings Dialog -->
    <SettingsDialog 
      v-model:visible="showSettings"
      v-model:settings="settings"
      @update:sidebarWidth="updateSidebarWidth"
      @save="handleSettingsSave"
    />
    
    <!-- Help Dialog -->
    <HelpDialog v-model:visible="showHelp" />
    
    <!-- History Dialog -->
    <div v-if="showHistory" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Execution History</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="showHistory = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div v-if="history.length > 0" class="space-y-4">
          <div 
            v-for="(item, index) in history" 
            :key="index"
            class="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
          >
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-medium text-sm">{{ item.goal }}</h4>
              <span class="text-xs text-gray-500">{{ item.timestamp }}</span>
            </div>
            <div class="text-xs text-gray-600 mb-2">
              <span class="font-medium">Mode:</span> {{ item.mode === 'streaming' ? 'Streaming' : 'Non-Streaming' }}
            </div>
            <div class="text-xs text-gray-600 mb-2">
              <span class="font-medium">Tasks:</span> {{ item.todos.length }}
            </div>
            <div class="text-xs text-gray-600">
              <span class="font-medium">Status:</span> {{ item.status }}
            </div>
            <div class="mt-2">
              <button 
                class="text-xs text-blue-600 hover:underline"
                @click="loadHistoryItem(item)"
              >
                Load Details
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-500">
          <i class="fas fa-history text-2xl mb-2"></i>
          <p class="text-sm">No execution history</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import TodoList from './components/TodoList.vue'
import MemoryComponent from './components/MemoryComponent.vue'
import SettingsDialog from './components/SettingsDialog.vue'
import HelpDialog from './components/HelpDialog.vue'
import { StreamHandler } from './utils/streamHandler'
import { ResultProcessor } from './utils/resultProcessor'

export default {
  name: 'App',
  components: {
    TodoList,
    MemoryComponent,
    SettingsDialog,
    HelpDialog
  },
  mounted() {
    // 生成sessionUuid
    this.sessionUuid = this.generateUuid()
    // 加载设置和历史记录
    this.loadSettings()
    this.loadHistory()
  },
  data() {
    return {
      goal: '',
      mode: 'streaming',
      sessionUuid: '',
      userId: 'user1',
      isRunning: false,
      processLogs: [],
      result: null,
      todos: [],
      sidebarWidth: 320,
      isResizing: false,
      resizeType: null,
      startX: 0,
      currentStream: null,
      chunkCacheManager: null,
      agentStatus: null, // Agent 状态
      showSettings: false,
      settings: {
        theme: 'light',
        fontSize: 'normal',
        sidebarWidth: 320
      },
      progress: 0, // 执行进度
      showHistory: false, // 显示历史记录对话框
      showHelp: false, // 显示帮助对话框
      history: [] // 执行历史记录
    }
  },
  computed: {
    formattedResult() {
      if (!this.result || !this.result.result) return ''
      return this.result.result.replace(/\\n/g, '\n')
    }
  },
  methods: {
    startAgent() {
      if (!this.goal.trim()) return
      
      this.processLogs = []
      this.result = null
      this.isRunning = true
      this.currentStream = null
      this.todos = []
      this.agentStatus = '执行中...' // 设置执行状态
      this.progress = 0 // 重置进度
      
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
    
    addLog(type, content) {
      const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false })
      this.processLogs.push({ type, content, timestamp })
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    processContentForTodos(content) {
      if (content.includes('Returning structured response:')) {
        const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length
        let structuredContent = content.substring(structuredStart).trim()
        
        try {
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
              return resultStr.replace(/\\n/g, '\n')
            }
          }
        } catch (e) {
          console.error('Failed to parse structured response:', e)
        }
        
        return structuredContent
      }
      
      if (content.includes('Updated todo list to ')) {
        const startIdx = content.indexOf('Updated todo list to ') + 'Updated todo list to '.length
        let bracketCount = 0
        let endIdx = startIdx
        for (let i = startIdx; i < content.length; i++) {
          if (content[i] === '[') {
            bracketCount++
          } else if (content[i] === ']') {
            bracketCount--
            if (bracketCount === 0) {
              endIdx = i + 1
              break
            }
          }
        }
        const todoListStr = content.substring(startIdx, endIdx)
        try {
          const validJsonStr = todoListStr.replace(/'/g, '"')
          const todos = JSON.parse(validJsonStr)
          this.todos = todos
          // 更新进度
          if (todos.length > 0) {
            const completedCount = todos.filter(todo => todo.status === 'completed').length
            this.progress = (completedCount / todos.length) * 100
          }
        } catch (error) {
          console.error('Failed to parse todo list:', error)
        }
        
        // 返回剩余的内容，而不是空字符串
        const remainingContent = content.substring(endIdx).trim()
        return remainingContent
      }
      
      const lines = content.split('\n')
      const filteredLines = lines.filter(line => {
        if (/^\s*\d+\s*\./.test(line)) {
          return false
        }
        if (line.trim().startsWith('`') && line.trim().endsWith('`')) {
          return false
        }
        if (!line.trim()) {
          return false
        }
        return true
      })
      
      const filteredContent = filteredLines.join('\n').trim()
      return filteredContent
    },

    updateTodoListOnCompletion() {
      if (!this.todos || this.todos.length === 0) {
        return
      }
      
      let lastInProgressIndex = -1
      for (let i = this.todos.length - 1; i >= 0; i--) {
        if (this.todos[i].status === 'in_progress') {
          lastInProgressIndex = i
          break
        }
      }
      
      if (lastInProgressIndex !== -1) {
          const updatedTodos = [...this.todos]
          updatedTodos[lastInProgressIndex].status = 'completed'
          
          if (lastInProgressIndex < updatedTodos.length - 1) {
            for (let i = lastInProgressIndex + 1; i < updatedTodos.length; i++) {
              updatedTodos[i].status = 'skipped'
            }
          }
          
          this.todos = updatedTodos
          // 更新进度
          const completedCount = updatedTodos.filter(todo => todo.status === 'completed').length
          this.progress = (completedCount / updatedTodos.length) * 100
        }
    },

    startResize(type, event) {
      this.isResizing = true
      this.resizeType = type
      this.startX = event.clientX
      
      document.addEventListener('mousemove', this.resize)
      document.addEventListener('mouseup', this.stopResize)
      
      event.preventDefault()
    },

    resize(event) {
      if (!this.isResizing) return
      
      const deltaX = event.clientX - this.startX
      
      if (this.resizeType === 'sidebar') {
        let newWidth = this.sidebarWidth + deltaX
        newWidth = Math.max(200, newWidth)
        
        const containerWidth = document.getElementById('main-container').offsetWidth
        newWidth = Math.min(containerWidth * 0.5, newWidth)
        
        this.sidebarWidth = newWidth
        this.startX = event.clientX
      }
    },

    stopResize() {
      this.isResizing = false
      this.resizeType = null
      document.removeEventListener('mousemove', this.resize)
      document.removeEventListener('mouseup', this.stopResize)
    },

    startStreamingMode() {
      const streamHandler = new StreamHandler(this)
      streamHandler.startStreamingMode()
    },

    startNonStreamingMode() {
      this.addLog('info', '开始执行自主决策Agent（非流式模式）')
      this.addLog('info', `目标: ${this.goal}`)
      this.addLog('info', '正在执行，请稍候...')
      this.agentStatus = '执行中...' // 设置执行状态
      
      axios.post('http://localhost:8000/run-agent', {
        goal: this.goal,
        mode: 'non-streaming'
      }, {
        params: {
          session_id: this.sessionUuid,
          user_id: this.userId
        }
      })
      .then(response => {
        if (response.data.success) {
          const resultProcessor = new ResultProcessor(this)
          resultProcessor.processNonStreamingResult(response)
          
          this.updateTodoListOnCompletion()
          this.isRunning = false
          this.agentStatus = null // 清除状态
          this.saveHistory() // 保存执行历史
        } else {
          this.addLog('error', '执行失败: ' + response.data.message)
          this.isRunning = false
          this.agentStatus = null // 清除状态
          this.saveHistory() // 保存执行历史
        }
      })
      .catch(error => {
        console.error('API请求失败:', error)
        this.addLog('error', '执行失败，请重试')
        this.isRunning = false
        this.agentStatus = null // 清除状态
        this.saveHistory() // 保存执行历史
      })
    },

    processContentForTodos(content) {
      if (content.includes('Returning structured response:')) {
        const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length
        let structuredContent = content.substring(structuredStart).trim()
        
        try {
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
              return resultStr.replace(/\\n/g, '\n')
            }
          }
        } catch (e) {
          console.error('Failed to parse structured response:', e)
        }
        
        return structuredContent
      }
      
      if (content.includes('Updated todo list to ')) {
        const startIdx = content.indexOf('Updated todo list to ') + 'Updated todo list to '.length
        let bracketCount = 0
        let endIdx = startIdx
        for (let i = startIdx; i < content.length; i++) {
          if (content[i] === '[') {
            bracketCount++
          } else if (content[i] === ']') {
            bracketCount--
            if (bracketCount === 0) {
              endIdx = i + 1
              break
            }
          }
        }
        const todoListStr = content.substring(startIdx, endIdx)
        try {
          const validJsonStr = todoListStr.replace(/'/g, '"')
          const todos = JSON.parse(validJsonStr)
          this.todos = todos
          // 更新进度
          if (todos.length > 0) {
            const completedCount = todos.filter(todo => todo.status === 'completed').length
            this.progress = (completedCount / todos.length) * 100
          }
        } catch (error) {
          console.error('Failed to parse todo list:', error)
        }
        
        const remainingContent = content.substring(endIdx).trim()
        return remainingContent
      }
      
      const lines = content.split('\n')
      const filteredLines = lines.filter(line => {
        if (/^\s*\d+\s*\./.test(line)) {
          return false
        }
        if (line.trim().startsWith('`') && line.trim().endsWith('`')) {
          return false
        }
        if (!line.trim()) {
          return false
        }
        return true
      })
      
      const filteredContent = filteredLines.join('\n').trim()
      return filteredContent
    },

    updateSidebarWidth(width) {
      this.sidebarWidth = width
    },
    handleSettingsSave(settings) {
      // 处理设置保存事件
      this.sidebarWidth = settings.sidebarWidth
    },
    loadSettings() {
      // 从本地存储加载设置
      const savedSettings = localStorage.getItem('appSettings')
      if (savedSettings) {
        this.settings = { ...this.settings, ...JSON.parse(savedSettings) }
        this.sidebarWidth = this.settings.sidebarWidth
        // 应用主题
        if (this.settings.theme === 'dark') {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
        // 应用字体大小
        document.documentElement.classList.remove('text-sm', 'text-base', 'text-lg')
        switch (this.settings.fontSize) {
          case 'small':
            document.documentElement.classList.add('text-sm')
            break
          case 'large':
            document.documentElement.classList.add('text-lg')
            break
          default:
            document.documentElement.classList.add('text-base')
        }
      }
    },
    saveHistory() {
      // 保存历史记录到本地存储
      const historyItem = {
        id: Date.now(),
        goal: this.goal,
        mode: this.mode,
        todos: [...this.todos],
        result: this.result,
        timestamp: new Date().toLocaleString(),
        status: this.todos.length > 0 ? 
          this.todos.every(todo => todo.status === 'completed') ? 'Completed' : 'Partial' : 'No Tasks'
      }
      
      // 从本地存储加载现有历史记录
      const existingHistory = localStorage.getItem('appHistory')
      let history = existingHistory ? JSON.parse(existingHistory) : []
      
      // 添加新的历史记录项
      history.unshift(historyItem)
      
      // 限制历史记录数量为最近10条
      if (history.length > 10) {
        history = history.slice(0, 10)
      }
      
      // 保存到本地存储
      localStorage.setItem('appHistory', JSON.stringify(history))
      
      // 更新当前历史记录列表
      this.history = history
    },
    loadHistory() {
      // 从本地存储加载历史记录
      const savedHistory = localStorage.getItem('appHistory')
      if (savedHistory) {
        this.history = JSON.parse(savedHistory)
      }
    },
    loadHistoryItem(item) {
      // 加载历史记录项到当前界面
      this.goal = item.goal
      this.mode = item.mode
      this.todos = [...item.todos]
      this.result = item.result
      this.showHistory = false
    },
    generateUuid() {
      // 生成唯一的UUID
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    },
    
    startNewConversation() {
      // 开始新对话
      this.sessionUuid = this.generateUuid()
      this.goal = ''
      this.processLogs = []
      this.result = null
      this.todos = []
      this.agentStatus = null
      this.progress = 0
    },
    
    handleLoadThread(thread) {
      // 加载历史对话
      this.sessionUuid = thread.thread_id
      
      // 清空当前状态
      this.goal = ''
      this.processLogs = []
      this.result = null
      this.todos = []
      this.agentStatus = null
      this.progress = 0
      
      // 显示历史对话消息
      this.addLog('info', `Loaded conversation from ${thread.date}`)
      
      // 添加历史消息到 processLogs
      thread.messages.forEach(msg => {
        let type = 'info'
        let content = ''
        
        if (msg.type === 'human') {
          type = 'info'
          content = `User: ${msg.content}`
        } else if (msg.type === 'ai') {
          type = 'success'
          content = `AI: ${msg.content || '(empty response)'}`
        } else if (msg.type === 'tool') {
          type = 'streaming'
          content = `Tool [${msg.tool_name}]: ${msg.content.substring(0, 200)}${msg.content.length > 200 ? '...' : ''}`
        }
        
        if (content) {
          const timestamp = new Date(msg.timestamp).toLocaleTimeString('zh-CN', { hour12: false })
          this.processLogs.push({ type, content, timestamp })
        }
      })
      
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    handleThreadDeleted(deletedThreadId) {
      // If the deleted thread was the active one, start a new conversation
      if (deletedThreadId === this.sessionUuid) {
        this.startNewConversation()
      }
    }
  }
}
</script>

<style scoped>
.process-container {
  max-height: 800px;
  overflow-y: auto;
}

.resize-handle {
  width: 8px;
  cursor: col-resize;
  background-color: #cbd5e1;
  transition: background-color 0.3s;
}

.resize-handle:hover {
  background-color: #94a3b8;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

<style>
/* 深色模式样式 */
.dark {
  background-color: #1a1a2e;
  color: #e2e8f0;
}

.dark .card {
  background-color: #16213e;
  border-color: #0f3460;
  color: #e2e8f0;
}

.dark .bg-gray-50 {
  background-color: #0f3460;
  color: #e2e8f0;
}

.dark .bg-blue-50 {
  background-color: #1a365d;
  color: #e2e8f0;
}

.dark .bg-green-50 {
  background-color: #22543d;
  color: #e2e8f0;
}

.dark .bg-red-50 {
  background-color: #742a2a;
  color: #e2e8f0;
}

.dark .bg-gray-100 {
  background-color: #1e293b;
  color: #e2e8f0;
}

.dark .border-gray-300 {
  border-color: #475569;
}

.dark .text-gray-500 {
  color: #94a3b8;
}

.dark .text-gray-700 {
  color: #cbd5e1;
}

.dark .text-gray-800 {
  color: #f8fafc;
}

.dark .btn-primary {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
}

.dark .btn-primary:hover {
  background-color: #2563eb;
  border-color: #2563eb;
}

.dark .btn {
  background-color: #1e293b;
  border-color: #475569;
  color: #e2e8f0;
}

.dark .btn:hover {
  background-color: #334155;
  border-color: #64748b;
}

.dark input[type="text"],
.dark textarea,
.dark select {
  background-color: #1e293b;
  border-color: #475569;
  color: #e2e8f0;
}

.dark input[type="text"]:focus,
.dark textarea:focus,
.dark select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dark .hover\:bg-gray-50:hover {
  background-color: #334155;
}

.dark .hover\:bg-gray-100:hover {
  background-color: #475569;
}

.dark .hover\:border-blue-600:hover {
  border-color: #3b82f6;
}

/* 深色模式下的设置对话框 */
.dark .bg-white {
  background-color: #16213e;
  color: #e2e8f0;
}

.dark .text-gray-400 {
  color: #94a3b8;
}

.dark .text-gray-400:hover {
  color: #cbd5e1;
}

.dark .border-gray-300 {
  border-color: #475569;
}

.dark .bg-blue-50 {
  background-color: #1a365d;
  border-color: #3b82f6;
  color: #bfdbfe;
}

.dark .bg-gray-800 {
  background-color: #0f172a;
  border-color: #334155;
  color: #e2e8f0;
}

.dark .text-blue-600 {
  color: #3b82f6;
}

.dark .bg-blue-600 {
  background-color: #3b82f6;
  color: #ffffff;
}

.dark .bg-blue-600:hover {
  background-color: #2563eb;
}

.dark .text-white {
  color: #ffffff;
}

/* 深色模式下的记忆模块 */
.dark .bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, #1a365d, #1e3a8a);
}

.dark .border-blue-100 {
  border-color: #1e40af;
}

.dark .bg-white {
  background-color: #1e293b;
  border-color: #334155;
}

.dark .text-blue-500 {
  color: #60a5fa;
}

.dark .text-purple-500 {
  color: #a78bfa;
}

.dark .text-green-500 {
  color: #34d399;
}

.dark .text-orange-500 {
  color: #f97316;
}

.dark .bg-gray-100 {
  background-color: #334155;
  color: #e2e8f0;
}

.dark .bg-gray-100:hover {
  background-color: #475569;
}

/* 深色模式下的页眉页脚 */
.dark .bg-gradient-to-r {
  background-image: linear-gradient(to right, #16213e, #0f3460);
}

.dark .text-white {
  color: #ffffff;
}

.dark .text-gray-300 {
  color: #cbd5e1;
}

.dark .text-gray-300:hover {
  color: #ffffff;
}

.dark .border-b {
  border-color: #334155;
}

.dark .border-t {
  border-color: #334155;
}
</style>
