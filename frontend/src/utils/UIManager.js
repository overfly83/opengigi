/**
 * UI管理工具类
 * 负责UI辅助功能，如滚动、布局调整等
 */

/**
 * 滚动到页面底部
 */
export function scrollToBottom() {
  const container = document.querySelector('.process-container');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

/**
 * 开始调整大小
 * @param {Object} app - 应用实例
 * @param {string} type - 调整类型
 * @param {Event} event - 鼠标事件
 */
export function startResize(app, type, event) {
  app.isResizing = true;
  app.resizeType = type;
  app.startX = event.clientX;
  
  document.addEventListener('mousemove', (e) => resize(app, e));
  document.addEventListener('mouseup', () => stopResize(app));
  
  event.preventDefault();
}

/**
 * 调整大小
 * @param {Object} app - 应用实例
 * @param {Event} event - 鼠标事件
 */
function resize(app, event) {
  if (!app.isResizing) return;
  
  const deltaX = event.clientX - app.startX;
  
  if (app.resizeType === 'sidebar') {
    let newWidth = app.sidebarWidth + deltaX;
    newWidth = Math.max(200, newWidth);
    
    const containerWidth = document.getElementById('main-container').offsetWidth;
    newWidth = Math.min(containerWidth * 0.5, newWidth);
    
    app.sidebarWidth = newWidth;
    app.startX = event.clientX;
  }
}

/**
 * 停止调整大小
 * @param {Object} app - 应用实例
 */
export function stopResize(app) {
  app.isResizing = false;
  app.resizeType = null;
  document.removeEventListener('mousemove', (e) => resize(app, e));
  document.removeEventListener('mouseup', () => stopResize(app));
}

/**
 * 格式化消息内容
 * @param {string} type - 消息类型
 * @param {string} content - 消息内容
 * @returns {string} 格式化后的内容
 */
export function formatMessageContent(type, content) {
  if (type === 'tool_result') {
    // 处理工具类型消息，去除技术术语
    let formattedContent = content;
    
    // 去除开头的技术术语，支持单引号和双引号
    if (formattedContent.includes('Returning structured response:')) {
      formattedContent = formattedContent.replace(/Returning structured response: phase='[^']+' result=(['"])([\s\S]+?)\1/g, '$2');
    }
    
    // 去除结尾的技术术语，处理有空格的情况
    formattedContent = formattedContent.replace(/\s*["']?\s*is_simple_and_unrelevant=None is_completed=True todos=None/g, '');
    
    // 将\n转义序列替换为实际的换行符，确保whitespace-pre-wrap类能正确处理
    formattedContent = formattedContent.replace(/\\n/g, '\n');
    
    return formattedContent;
  }
  // 对于人类和AI类型消息，直接返回内容
  return content;
}
