<template>
  <div class="memory-component">
    <h3 class="text-base font-semibold mb-3 flex items-center text-gray-800 dark:text-white">
      <i class="fas fa-history mr-2 text-blue-600 dark:text-blue-400 text-sm"></i>
      Conversation History
    </h3>
    
    <div class="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900 dark:to-indigo-900 p-4 rounded-lg border border-blue-100 dark:border-blue-800 h-full overflow-hidden flex flex-col">
      <div v-if="loading" class="flex items-center justify-center py-4">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        </div>
        <span class="text-xs text-gray-500 dark:text-blue-200 ml-2">Loading...</span>
      </div>
      
      <div v-else-if="conversationHistory.length > 0" class="flex-1 overflow-y-auto space-y-2">
        <div 
          v-for="(thread, index) in conversationHistory" 
          :key="thread.thread_id"
          class="relative group"
        >
          <div 
            @click="loadThread(thread)"
            :class="[
              'p-3 rounded-lg cursor-pointer transition-all duration-200 border',
              isActiveThread(thread) 
                ? 'bg-blue-100 dark:bg-blue-800 border-blue-400 dark:border-blue-500' 
                : 'bg-white dark:bg-blue-800 dark:bg-opacity-50 border-gray-200 dark:border-blue-700 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'
            ]"
          >
            <div class="flex items-start justify-between mb-1">
              <div class="flex-1 min-w-0 pr-6">
                <div class="flex items-center">
                  <i class="fas fa-comment text-blue-500 dark:text-blue-400 mr-2 text-xs"></i>
                  <h4 class="text-xs font-medium text-gray-700 dark:text-white truncate">
                    {{ getThreadTitle(thread) }}
                  </h4>
                </div>
              </div>
              <span v-if="isActiveThread(thread)" class="ml-2">
                <i class="fas fa-check-circle text-green-500 text-xs"></i>
              </span>
            </div>
            
            <div class="text-[10px] text-gray-500 dark:text-blue-200 mb-1">
              <i class="fas fa-calendar mr-1"></i>
              {{ thread.date }}
            </div>
            
            <div class="text-[10px] text-gray-500 dark:text-blue-200">
              <i class="fas fa-comments mr-1"></i>
              {{ thread.messages.length }} messages
            </div>
          </div>
          
          <button 
            @click.stop="deleteThread(thread)"
            class="absolute top-2 right-2 w-5 h-5 flex items-center justify-center rounded-full bg-red-100 hover:bg-red-200 text-red-600 hover:text-red-700 transition-all duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100"
            title="Delete conversation"
          >
            <i class="fas fa-times text-[10px]"></i>
          </button>
        </div>
      </div>
      
      <div v-else class="flex-1 flex flex-col items-center justify-center text-center">
        <div class="w-16 h-16 bg-blue-100 dark:bg-blue-600 dark:bg-opacity-30 rounded-full flex items-center justify-center mb-3">
          <i class="fas fa-inbox text-2xl text-blue-600 dark:text-blue-300"></i>
        </div>
        
        <h4 class="text-sm font-medium text-gray-800 dark:text-white mb-1">No conversations yet</h4>
        <p class="text-xs text-gray-500 dark:text-blue-200">
          Start your first conversation to see it here
        </p>
      </div>
      
      <div class="mt-3 pt-3 border-t border-blue-200 dark:border-blue-700">
        <button 
          @click="refreshHistory"
          class="w-full btn bg-white dark:bg-blue-800 text-gray-700 dark:text-white hover:bg-gray-100 dark:hover:bg-blue-700 text-xs py-1.5 flex items-center justify-center"
        >
          <i class="fas fa-sync-alt mr-1"></i>
          Refresh
        </button>
      </div>
    </div>
    
    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :visible="showDeleteDialog"
      title="Delete Conversation"
      :message="deleteConfirmMessage"
      confirmText="Delete"
      cancelText="Cancel"
      :isDanger="true"
      @confirm="confirmDeleteThread"
      @cancel="cancelDeleteThread"
    />
  </div>
</template>

<script>
import axios from 'axios'
import ConfirmDialog from './ConfirmDialog.vue'

export default {
  name: 'MemoryComponent',
  components: {
    ConfirmDialog
  },
  props: {
    userId: {
      type: String,
      default: 'user1'
    },
    currentSessionUuid: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      conversationHistory: [],
      loading: false,
      showDeleteDialog: false,
      threadToDelete: null
    }
  },
  computed: {
    deleteConfirmMessage() {
      if (!this.threadToDelete) {
        return 'Are you sure you want to delete this conversation?'
      }
      const title = this.getThreadTitle(this.threadToDelete)
      return `Are you sure you want to delete this conversation?\n\n"${title}"`
    }
  },
  watch: {
    userId: {
      immediate: true,
      handler() {
        this.loadHistory()
      }
    }
  },
  methods: {
    async loadHistory() {
      this.loading = true
      try {
        const response = await axios.get(`http://localhost:8000/history/${this.userId}`)
        if (response.data.success) {
          this.conversationHistory = response.data.data.sort((a, b) => 
            new Date(b.updated_at) - new Date(a.updated_at)
          )
        }
      } catch (error) {
        console.error('Failed to load conversation history:', error)
      } finally {
        this.loading = false
      }
    },
    
    refreshHistory() {
      this.loadHistory()
    },
    
    getThreadTitle(thread) {
      const firstHumanMessage = thread.messages.find(m => m.type === 'human')
      if (firstHumanMessage) {
        const content = firstHumanMessage.content.trim()
        if (content.length > 30) {
          return content.substring(0, 30) + '...'
        }
        return content || 'Untitled Conversation'
      }
      return 'Untitled Conversation'
    },
    
    isActiveThread(thread) {
      return thread.thread_id === this.currentSessionUuid
    },
    
    loadThread(thread) {
      this.$emit('load-thread', thread)
    },
    
    deleteThread(thread) {
      this.threadToDelete = thread
      this.showDeleteDialog = true
    },
    
    async confirmDeleteThread() {
      try {
        await axios.delete(`http://localhost:8000/history/${this.userId}/${this.threadToDelete.thread_id}`)
        // Refresh the conversation list
        this.loadHistory()
        // If the deleted thread was active, emit event to notify parent
        if (this.threadToDelete.thread_id === this.currentSessionUuid) {
          this.$emit('thread-deleted', this.threadToDelete.thread_id)
        }
      } catch (error) {
        console.error('Failed to delete thread:', error)
        alert('Failed to delete conversation. Please try again.')
      } finally {
        this.showDeleteDialog = false
        this.threadToDelete = null
      }
    },
    
    cancelDeleteThread() {
      this.showDeleteDialog = false
      this.threadToDelete = null
    }
  }
}
</script>

<style scoped>
.memory-component p {
  line-height: 1.2;
}
</style>
