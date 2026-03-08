/**
 * 待办事项管理工具类
 * 负责待办事项的解析、处理和状态管理
 */
import JSON5 from 'json5';

/**
 * 处理内容并提取待办事项
 * @param {Object} app - 应用实例
 * @param {string} content - 内容
 * @returns {string} 处理后的内容
 */
export function processContentForTodos(app, content) {
  // 检查content是否为字符串类型
  if (typeof content !== 'string') {
    // 尝试将非字符串内容处理为字符串
    try {
      // 先尝试将其解析为JSON对象
      if (Array.isArray(content) || (typeof content === 'object' && content !== null)) {
        // 如果是数组或对象，直接转换为JSON字符串
        return JSON.stringify(content);
      } else {
        // 其他类型，尝试转换为字符串
        return String(content);
      }
    } catch (e) {
      console.error('Failed to process non-string content:', e);
      return '';
    }
  }
  
  if (content.includes('Returning structured response:')) {
    const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length;
    let structuredContent = content.substring(structuredStart).trim();
    
    try {
      if (structuredContent.includes('result=')) {
        const resultStart = structuredContent.indexOf('result=') + 'result='.length;
        let resultEnd = structuredContent.indexOf(' is_simple_and_unrelevant=');
        if (resultEnd === -1) {
          resultEnd = structuredContent.indexOf(' is_completed=');
        }
        if (resultEnd !== -1) {
          let resultStr = structuredContent.substring(resultStart, resultEnd).trim();
          if (resultStr.startsWith('\'')) {
            resultStr = resultStr.substring(1);
          }
          if (resultStr.endsWith('\'')) {
            resultStr = resultStr.substring(0, resultStr.length - 1);
          }
          return resultStr.replace(/\\n/g, '\n');
        }
      }
    } catch (e) {
      console.error('Failed to parse structured response:', e);
    }
    
    return structuredContent;
  }
  
  if (content.includes('Updated todo list to ')) {
    const startIdx = content.indexOf('Updated todo list to ') + 'Updated todo list to '.length;
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
    const todoListStr = content.substring(startIdx, endIdx);
    let todos = [];
    
    // 尝试解析待办事项列表
    try {
      // 使用JSON5解析，支持单引号、注释等
      todos = JSON5.parse(todoListStr);
      console.log('Successfully parsed todo list using JSON5');
    } catch (error) {
      console.error('Failed to parse todo list with JSON5:', error);
      // 解析失败时，设置为空数组
      todos = [];
    }
    
    // 更新待办事项和进度
    app.todos = todos;
    if (todos.length > 0) {
      const completedCount = todos.filter(todo => todo.status === 'completed').length;
      app.progress = (completedCount / todos.length) * 100;
    } else {
      app.progress = 0;
    }
    
    const remainingContent = content.substring(endIdx).trim();
    return remainingContent;
  }
  
  // 安全地分割字符串
  const lines = content.split('\n');
  const filteredLines = lines.filter(line => {
    if (/^\s*\d+\s*\./.test(line)) {
      return false;
    }
    if (line.trim().startsWith('`') && line.trim().endsWith('`')) {
      return false;
    }
    if (!line.trim()) {
      return false;
    }
    return true;
  });
  
  const filteredContent = filteredLines.join('\n').trim();
  return filteredContent;
}

/**
 * 更新待办事项列表状态
 * @param {Object} app - 应用实例
 */
export function updateTodoListOnCompletion(app) {
  if (!app.todos || app.todos.length === 0) {
    return;
  }
  
  let lastInProgressIndex = -1;
  for (let i = app.todos.length - 1; i >= 0; i--) {
    if (app.todos[i].status === 'in_progress') {
      lastInProgressIndex = i;
      break;
    }
  }
  
  if (lastInProgressIndex !== -1) {
      const updatedTodos = [...app.todos];
      updatedTodos[lastInProgressIndex].status = 'completed';
      
      if (lastInProgressIndex < updatedTodos.length - 1) {
        for (let i = lastInProgressIndex + 1; i < updatedTodos.length; i++) {
          updatedTodos[i].status = 'skipped';
        }
      }
      
      app.todos = updatedTodos;
      // 更新进度
      const completedCount = updatedTodos.filter(todo => todo.status === 'completed').length;
      app.progress = (completedCount / updatedTodos.length) * 100;
    }
}

/**
 * 计算待办事项进度
 * @param {Array} todos - 待办事项列表
 * @returns {number} 进度百分比
 */
export function calculateTodoProgress(todos) {
  if (!todos || todos.length === 0) {
    return 0;
  }
  const completedCount = todos.filter(todo => todo.status === 'completed').length;
  return (completedCount / todos.length) * 100;
}
