/**
 * 历史记录管理工具类
 * 负责历史记录的保存、加载和管理
 */

// 历史记录相关常量
const HISTORY_KEY = 'appHistory';
const MAX_HISTORY_ITEMS = 10;

/**
 * 保存执行历史到本地存储
 * @param {Object} app - App组件实例
 * @returns {Array} 更新后的历史记录列表
 */
export function saveHistory(app) {
  // 从App组件实例中提取必要的信息
  const historyItem = {
    id: Date.now(),
    goal: app.goal || '',
    mode: app.mode || 'streaming',
    todos: app.todos || [],
    timestamp: new Date().toLocaleString(),
    status: (app.todos && app.todos.length > 0) ? 
      app.todos.every(todo => todo.status === 'completed') ? 'Completed' : 'Partial' : 'No Tasks'
  };
  
  // 从本地存储加载现有历史记录
  const existingHistory = localStorage.getItem(HISTORY_KEY);
  let history = existingHistory ? JSON.parse(existingHistory) : [];
  
  // 添加新的历史记录项
  history.unshift(historyItem);
  
  // 限制历史记录数量为最近10条
  if (history.length > MAX_HISTORY_ITEMS) {
    history = history.slice(0, MAX_HISTORY_ITEMS);
  }
  
  // 保存到本地存储
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  
  return history;
}

/**
 * 从本地存储加载历史记录
 * @returns {Array} 历史记录列表
 */
export function loadHistory() {
  const savedHistory = localStorage.getItem(HISTORY_KEY);
  return savedHistory ? JSON.parse(savedHistory) : [];
}

/**
 * 清除所有历史记录
 */
export function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}

/**
 * 创建历史记录项
 * @param {string} goal - 目标
 * @param {string} mode - 执行模式
 * @param {Array} todos - 待办事项列表
 * @returns {Object} 历史记录项
 */
export function createHistoryItem(goal, mode, todos) {
  return {
    id: Date.now(),
    goal: goal,
    mode: mode,
    todos: [...todos],
    timestamp: new Date().toLocaleString(),
    status: todos.length > 0 ? 
      todos.every(todo => todo.status === 'completed') ? 'Completed' : 'Partial' : 'No Tasks'
  };
}
