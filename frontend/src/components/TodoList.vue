<template>
  <div class="todo-list">
    <h3 class="text-base font-semibold mb-2 flex items-center">
      <i class="fas fa-tasks mr-2 text-blue-600 text-sm"></i>
      Task List
    </h3>
    
    <div v-if="todos.length > 0" class="space-y-1">
      <div
        v-for="(todo, index) in todos"
        :key="index"
        class="todo-item p-2 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors duration-200"
        :class="{'border-green-200': todo.status === 'completed', 'border-blue-200': todo.status === 'in_progress', 'border-yellow-200': todo.status === 'pending', 'border-gray-200': todo.status === 'skipped'}"
      >
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center flex-1 min-w-0">
            <div class="mr-2 flex-shrink-0">
              <div class="relative">
                <i
                  v-if="todo.status === 'completed'"
                  class="fas fa-check-circle text-green-500 text-sm"
                  :title="getStatusText(todo.status)"
                ></i>
                <i
                  v-else-if="todo.status === 'in_progress'"
                  class="fas fa-spinner fa-spin text-blue-500 text-sm"
                  :title="getStatusText(todo.status)"
                ></i>
                <i
                  v-else-if="todo.status === 'skipped'"
                  class="fas fa-ban text-gray-400 text-sm"
                  :title="getStatusText(todo.status)"
                ></i>
                <i
                  v-else
                  class="fas fa-circle text-gray-300 text-sm"
                  :title="getStatusText(todo.status)"
                ></i>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="relative">
                <p
                  class="text-xs font-medium truncate"
                  :class="{
                    'line-through text-gray-500': todo.status === 'completed',
                    'line-through text-gray-400': todo.status === 'skipped'
                  }"
                  :title="todo.content"
                >
                  {{ todo.content }}
                </p>
              </div>
            </div>
          </div>
          <div class="ml-2 flex-shrink-0">
            <div class="relative">
              <span
                class="text-xs px-1.5 py-0.5 rounded-full text-xs"
                :class="{
                  'bg-green-100 text-green-600': todo.status === 'completed',
                  'bg-blue-100 text-blue-600': todo.status === 'in_progress',
                  'bg-yellow-100 text-yellow-600': todo.status === 'pending',
                  'bg-gray-100 text-gray-500': todo.status === 'skipped'
                }"
                :title="getStatusText(todo.status)"
              >
                <i
                  v-if="todo.status === 'completed'"
                  class="fas fa-check text-xs"
                ></i>
                <i
                  v-else-if="todo.status === 'in_progress'"
                  class="fas fa-spinner text-xs"
                ></i>
                <i
                  v-else-if="todo.status === 'skipped'"
                  class="fas fa-ban text-xs"
                ></i>
                <i
                  v-else
                  class="fas fa-hourglass-start text-xs"
                ></i>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state p-3 bg-gray-50 rounded-md text-center text-gray-500">
      <i class="fas fa-clipboard-list text-lg mb-1"></i>
      <p class="text-xs">No tasks</p>
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
          return 'Completed';
        case 'in_progress':
          return 'In Progress';
        case 'skipped':
          return 'Skipped';
        default:
          return 'Pending';
      }
    }
  }
}
</script>

<style scoped>
/* Additional component-specific styles can be added here */
</style>
