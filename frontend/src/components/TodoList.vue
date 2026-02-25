<template>
  <div class="todo-list">
    <h3 class="text-lg font-semibold mb-4 flex items-center">
      <i class="fas fa-tasks mr-2 text-primary"></i>
      任务列表
    </h3>
    
    <div v-if="todos.length > 0" class="space-y-2">
      <div
        v-for="(todo, index) in todos"
        :key="index"
        class="todo-item"
        :class="{
          'todo-item-completed': todo.status === 'completed',
          'todo-item-in-progress': todo.status === 'in_progress',
          'todo-item-pending': todo.status !== 'completed' && todo.status !== 'in_progress'
        }"
      >
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center">
            <div class="mr-3">
              <i
                v-if="todo.status === 'completed'"
                class="fas fa-check-circle text-success text-xl"
              ></i>
              <i
                v-else-if="todo.status === 'in_progress'"
                class="fas fa-spinner fa-spin text-info text-xl"
              ></i>
              <i
                v-else-if="todo.status === 'skipped'"
                class="fas fa-ban text-gray-400 text-xl"
              ></i>
              <i
                v-else
                class="fas fa-circle text-gray-300 text-xl"
              ></i>
            </div>
            <div class="flex-1">
              <p
                class="text-sm font-medium"
                :class="{
                  'line-through text-gray-500': todo.status === 'completed',
                  'line-through text-gray-400': todo.status === 'skipped'
                }"
              >
                {{ todo.content }}
              </p>
            </div>
          </div>
          <div class="ml-2">
            <span
              class="text-xs px-2 py-1 rounded-full"
              :class="{
                'bg-success bg-opacity-20 text-success': todo.status === 'completed',
                'bg-info bg-opacity-20 text-info': todo.status === 'in_progress',
                'bg-warning bg-opacity-20 text-warning': todo.status === 'pending',
                'bg-gray-200 text-gray-500': todo.status === 'skipped'
              }"
            >
              {{ getStatusText(todo.status) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state p-4 bg-gray-50 rounded-md text-center text-gray-500">
      <i class="fas fa-clipboard-list text-2xl mb-2"></i>
      <p class="text-sm">暂无任务</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TodoList',
  props: {
    todos: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getStatusText(status) {
      switch (status) {
        case 'completed':
          return '已完成';
        case 'in_progress':
          return '进行中';
        case 'skipped':
          return '已跳过';
        default:
          return '待开始';
      }
    }
  }
}
</script>

<style scoped>
/* Additional component-specific styles can be added here */
</style>
