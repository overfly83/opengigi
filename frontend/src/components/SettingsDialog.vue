<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Settings</h3>
        <button class="text-gray-400 hover:text-gray-600" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="space-y-4">
        <!-- Theme Setting -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Theme</label>
          <div class="flex space-x-2">
            <button 
              class="flex-1 py-2 px-4 rounded-md border" 
              :class="settings.theme === 'light' ? 'bg-blue-50 border-blue-500 text-blue-600' : 'border-gray-300'"
              @click="settings.theme = 'light'"
            >
              <i class="fas fa-sun mr-1"></i> Light
            </button>
            <button 
              class="flex-1 py-2 px-4 rounded-md border" 
              :class="settings.theme === 'dark' ? 'bg-gray-800 border-gray-600 text-white' : 'border-gray-300'"
              @click="settings.theme = 'dark'"
            >
              <i class="fas fa-moon mr-1"></i> Dark
            </button>
          </div>
        </div>
        
        <!-- Font Size Setting -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Font Size</label>
          <select v-model="settings.fontSize" class="w-full p-2 border border-gray-300 rounded-md">
            <option value="small">Small</option>
            <option value="normal">Normal</option>
            <option value="large">Large</option>
          </select>
        </div>
        
        <!-- Sidebar Width Setting -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sidebar Width: {{ settings.sidebarWidth }}px</label>
          <input 
            type="range" 
            v-model.number="settings.sidebarWidth" 
            min="200" 
            max="400" 
            class="w-full"
            @change="updateSidebarWidth"
          >
        </div>
      </div>
      
      <div class="mt-6 flex justify-between space-x-2">
        <button class="px-4 py-2 border border-red-300 rounded-md text-red-700 hover:bg-red-50" @click="resetSettings">
          Reset to Default
        </button>
        <div class="flex space-x-2">
          <button class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50" @click="close">
            Cancel
          </button>
          <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700" @click="saveSettings">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    settings: {
      type: Object,
      default: () => ({
        theme: 'light',
        fontSize: 'normal',
        sidebarWidth: 320
      })
    }
  },
  methods: {
    close() {
      this.$emit('update:visible', false)
    },
    saveSettings() {
      // 保存设置到本地存储
      localStorage.setItem('appSettings', JSON.stringify(this.settings))
      // 应用主题
      this.applyTheme()
      // 应用字体大小
      this.applyFontSize()
      // 关闭设置对话框
      this.close()
      // 触发保存事件
      this.$emit('save', this.settings)
    },
    resetSettings() {
      // 重置设置为默认值
      const defaultSettings = {
        theme: 'light',
        fontSize: 'normal',
        sidebarWidth: 320
      }
      // 从本地存储中移除设置
      localStorage.removeItem('appSettings')
      // 应用默认设置
      this.$emit('update:settings', defaultSettings)
      this.applyTheme()
      this.applyFontSize()
    },
    updateSidebarWidth() {
      this.$emit('update:sidebarWidth', this.settings.sidebarWidth)
    },
    applyTheme() {
      if (this.settings.theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },
    applyFontSize() {
      // 移除所有字体大小类
      document.documentElement.classList.remove('text-sm', 'text-base', 'text-lg')
      // 添加新的字体大小类
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
  }
}
</script>

<style scoped>
/* Component-specific styles can be added here */
</style>