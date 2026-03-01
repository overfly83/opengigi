<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md mx-4">
      <div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white flex items-center">
          <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
          {{ title }}
        </h3>
        <button 
          class="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-white" 
          @click="cancel"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="p-6">
        <div class="mb-6">
          <p class="text-gray-700 dark:text-gray-300 text-sm">
            {{ message }}
          </p>
        </div>
        
        <div class="flex justify-end space-x-3">
          <button 
            @click="cancel"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors duration-200"
          >
            {{ cancelText }}
          </button>
          <button 
            @click="confirm"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
              isDanger 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            ]"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Confirm'
    },
    message: {
      type: String,
      default: 'Are you sure?'
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    isDanger: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    confirm() {
      this.$emit('confirm')
    },
    cancel() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
/* Component-specific styles */
</style>
