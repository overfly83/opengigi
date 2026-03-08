<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg">
      <div class="container mx-auto px-4 py-3">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="flex items-center mb-2 md:mb-0">
            <div class="w-8 h-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center mr-2">
              <i class="fas fa-brands fa-bots text-white text-xl"></i>
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
              @keydown.ctrl.enter="startAgent"
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
                   :class="['p-2 mb-1 rounded-lg', getMessageBgColor(log.type)]">
                <div class="flex items-start">
                  <div class="flex items-center">
                    <i :class="['fas', MessageIcon[log.type] || 'fa-comment-dots', 'mt-1', 'mr-2', getMessageColor(log.type)]"></i>
                    <span v-if="log.tool_name" class="text-xs text-gray-500 mr-2">{{ log.tool_name }}</span>
                  </div>
                  <div class="flex-1">
                    <div class="text-xs text-gray-500 mb-1">{{ log.timestamp }}</div>
                    <div class="text-xs whitespace-pre-wrap">{{ formatMessageContent(log.type, log.content) }}</div>
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
import { MessageType, MessageIcon, getMessageColor, getMessageBgColor, normalizeMessageType } from './utils/messageTypes'
import { saveHistory, loadHistory, createHistoryItem } from './utils/HistoryManager'
import { generateUuid, startNewConversation, handleLoadThread, handleThreadDeleted } from './utils/SessionManager'
import { loadSettings, handleSettingsSave, updateSidebarWidth as updateSidebarWidthUtil } from './utils/SettingsManager'
import { processContentForTodos, updateTodoListOnCompletion } from './utils/TodoManager'
import { scrollToBottom, startResize as startResizeUtil, stopResize as stopResizeUtil, formatMessageContent } from './utils/UIManager'

// 导入全局样式
import './assets/styles/global.css'

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
    this.sessionUuid = generateUuid()
    // 加载设置和历史记录
    this.loadSettings()
    this.history = loadHistory()
  },
  data() {
    return {
      MessageIcon,
      goal: '',
      mode: 'streaming',
      sessionUuid: '',
      userId: 'user1',
      isRunning: false,
      processLogs: [],
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
  },
  methods: {
    getMessageColor,
    getMessageBgColor,
    formatMessageContent,
    startAgent() {
      if (!this.goal.trim()) return
      
      // 保留历史对话，只清空待办事项
      this.isRunning = true
      this.currentStream = null
      this.todos = []
      this.agentStatus = '执行中...' // 设置执行状态
      this.progress = 0 // 重置进度
      
      // 添加新任务开始的标记
      this.addLog(MessageType.SYSTEM, `开始新任务: ${this.goal}`)
      
      if (this.mode === 'streaming') {
        this.startStreamingMode()
      } else {
        this.startNonStreamingMode()
      }
    },
    
    addLog(type, content) {
      const normalizedType = normalizeMessageType(type)
      // 处理换行符，确保\n被转换为\n
      const processedContent = content.replace(/\\n/g, '\n')
      const timestamp = new Date().toLocaleTimeString('zh-CN', { hour12: false })
      this.processLogs.push({ type: normalizedType, content: processedContent, timestamp })
      this.$nextTick(() => {
        scrollToBottom()
      })
    },
    
    startStreamingMode() {
      const streamHandler = new StreamHandler(this)
      streamHandler.startStreamingMode()
    },

    startNonStreamingMode() {
      this.addLog(MessageType.SYSTEM, '开始执行自主决策Agent（非流式模式）')
      this.addLog(MessageType.SYSTEM, `目标: ${this.goal}`)
      this.addLog(MessageType.SYSTEM, '正在执行，请稍候...')
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
          // 直接处理响应数据
          if (response.data.thought || response.data.result) {
            if (response.data.thought) {
              this.addLog(MessageType.AI, `思考: ${response.data.thought}`)
            }
            if (response.data.result) {
              this.addLog(MessageType.AI, `结果: ${response.data.result}`)
            }
          }
          
          updateTodoListOnCompletion(this)
          this.isRunning = false
          this.agentStatus = null // 清除状态
          saveHistory(this) // 保存执行历史
        } else {
          this.addLog(MessageType.ERROR, '执行失败: ' + response.data.message)
          this.isRunning = false
          this.agentStatus = null // 清除状态
          saveHistory(this) // 保存执行历史
        }
      })
      .catch(error => {
        console.error('API请求失败:', error)
        this.addLog(MessageType.ERROR, '执行失败，请重试')
        this.isRunning = false
        this.agentStatus = null // 清除状态
        saveHistory(this) // 保存执行历史
      })
    },
    
    loadHistoryItem(item) {
      // 加载历史记录项到当前界面
      this.goal = item.goal
      this.mode = item.mode
      this.todos = [...item.todos]
      this.showHistory = false
    },
    
    // 委托给工具类的方法
    startNewConversation() {
      startNewConversation(this)
    },
    
    handleLoadThread(thread) {
      handleLoadThread(this, thread)
    },
    
    handleThreadDeleted(deletedThreadId) {
      handleThreadDeleted(this, deletedThreadId)
    },
    
    updateSidebarWidth(width) {
      updateSidebarWidthUtil(this, width)
    },
    
    handleSettingsSave(settings) {
      handleSettingsSave(this, settings)
    },
    
    loadSettings() {
      loadSettings(this)
    }
  }
}
</script>

<style scoped>
.process-container {
  max-height: 800px;
  overflow-y: auto;
}
</style>

<style>
/* 导入共享样式 */
@import './assets/styles/shared.css';
</style>

