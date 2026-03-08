/**
 * 会话管理工具类
 * 负责会话的创建、加载和管理
 */
import { normalizeMessageType, MessageType } from './messageTypes';
import { scrollToBottom } from './UIManager';

/**
 * 生成唯一的UUID
 * @returns {string} UUID
 */
export function generateUuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * 开始新对话
 * @param {Object} app - 应用实例
 */
export function startNewConversation(app) {
  app.sessionUuid = generateUuid();
  app.goal = '';
  app.processLogs = [];
  app.todos = [];
  app.agentStatus = null;
  app.progress = 0;
}

/**
 * 处理会话删除
 * @param {Object} app - 应用实例
 * @param {string} deletedThreadId - 删除的会话ID
 */
export function handleThreadDeleted(app, deletedThreadId) {
  // If the deleted thread was the active one, start a new conversation
  if (deletedThreadId === app.sessionUuid) {
    startNewConversation(app);
  }
}

/**
 * 加载历史对话
 * @param {Object} app - 应用实例
 * @param {Object} thread - 会话线程
 */
export function handleLoadThread(app, thread) {
  // 加载历史对话
  app.sessionUuid = thread.thread_id;
  
  // 清空当前状态
  app.goal = '';
  app.processLogs = [];
  app.todos = [];
  app.agentStatus = null;
  app.progress = 0;
  
  // 显示历史对话消息
  app.addLog('system', `Loaded conversation from ${thread.date}`);
  
  // 添加历史消息到 processLogs
  thread.messages.forEach(msg => {
    let type = 'system';
    let content = '';
    
    if (msg.type === 'human') {
      type = MessageType.HUMAN;
      content = msg.content;
    } else if (msg.type === 'ai') {
      type = MessageType.AI;
      // 确保 content 是字符串
      let aiContent = msg.content;
      if (typeof aiContent === 'object' && aiContent !== null) {
        // 检查是否是工具调用
        if (aiContent.type === 'tool_call' && aiContent.args) {
          // 提取工具调用信息
          if (aiContent.args.result) {
            // 直接使用结果
            content = aiContent.args.result;
          } else {
            // 提取工具调用信息
            const toolName = aiContent.name || aiContent.type;
            const args = JSON.stringify(aiContent.args);
            content = `${toolName} - ${args}`;
          }
        } else if (aiContent.phase && aiContent.result) {
          // 提取结构化结果
          content = aiContent.result;
        } else if (aiContent.result) {
          // 提取结果
          content = aiContent.result;
        } else {
          // 其他情况，尝试转换为字符串并解析
          try {
            const contentStr = JSON.stringify(aiContent);
            const parsed = JSON.parse(contentStr);
            if (parsed.args && parsed.args.result) {
              content = parsed.args.result;
            } else if (parsed.result) {
              content = parsed.result;
            } else {
              content = contentStr;
            }
          } catch (e) {
            content = String(aiContent);
          }
        }
      } else if (typeof aiContent === 'string') {
        // 字符串类型，尝试解析为JSON
        try {
          const parsed = JSON.parse(aiContent);
          if (parsed.args && parsed.args.result) {
            content = parsed.args.result;
          } else if (parsed.result) {
            content = parsed.result;
          } else if (parsed.type === 'tool_call' && parsed.args) {
            if (parsed.args.result) {
              content = parsed.args.result;
            } else {
              const toolName = parsed.name || parsed.type;
              const args = JSON.stringify(parsed.args);
              content = `${toolName} - ${args}`;
            }
          } else {
            content = aiContent;
          }
        } catch (e) {
          // 不是JSON字符串，尝试提取result
          if (aiContent.includes('Returning structured response:')) {
            const structuredStart = aiContent.indexOf('Returning structured response:') + 'Returning structured response:'.length;
            let structuredContent = aiContent.substring(structuredStart).trim();
            
            // 尝试提取result值
            const resultMatch = structuredContent.match(/result='([^']+)'/);
            if (resultMatch && resultMatch[1]) {
              content = resultMatch[1];
            } else {
              const resultMatchDoubleQuote = structuredContent.match(/result="([^"]+)"/);
              if (resultMatchDoubleQuote && resultMatchDoubleQuote[1]) {
                content = resultMatchDoubleQuote[1];
              } else {
                content = structuredContent;
              }
            }
          } else {
            content = aiContent;
          }
        }
      } else {
        content = aiContent || '(empty response)';
      }
      // 处理换行符
      if (typeof content === 'string') {
        content = content.replace(/\n/g, '\n');
        // 去除多余的空白字符
        content = content.trim();
      } else {
        // 如果content不是字符串，转换为字符串
        content = String(content);
      }
    } else if (msg.type === 'tool') {
      type = MessageType.TOOL_RESULT;
      // 确保 content 是字符串
      let toolContent = msg.content;
      if (typeof toolContent === 'object' && toolContent !== null) {
        // 检查是否是结构化响应
        if (typeof toolContent === 'string' && toolContent.includes('Returning structured response:')) {
          // 提取结果部分
          const structuredStart = toolContent.indexOf('Returning structured response:') + 'Returning structured response:'.length;
          let structuredContent = toolContent.substring(structuredStart).trim();
          
          // 尝试解析为JSON
          try {
            // 尝试将structuredContent转换为有效的JSON
            const jsonStr = structuredContent.replace(/'/g, '"');
            const parsed = JSON.parse(jsonStr);
            if (parsed.result) {
              content = parsed.result;
            } else {
              // 尝试提取result值
              const resultMatch = structuredContent.match(/result='([^']+)'/);
              if (resultMatch && resultMatch[1]) {
                content = resultMatch[1];
              } else {
                const resultMatchDoubleQuote = structuredContent.match(/result="([^"]+)"/);
                if (resultMatchDoubleQuote && resultMatchDoubleQuote[1]) {
                  content = resultMatchDoubleQuote[1];
                } else {
                  content = structuredContent;
                }
              }
            }
          } catch (e) {
            // 解析失败，尝试提取result值
            const resultMatch = structuredContent.match(/result='([^']+)'/);
            if (resultMatch && resultMatch[1]) {
              content = resultMatch[1];
            } else {
              const resultMatchDoubleQuote = structuredContent.match(/result="([^"]+)"/);
              if (resultMatchDoubleQuote && resultMatchDoubleQuote[1]) {
                content = resultMatchDoubleQuote[1];
              } else {
                content = structuredContent;
              }
            }
          }
        } else if (toolContent.status === 'success' && toolContent.current) {
          // 天气工具结果
          const location = toolContent.location.name || '未知位置';
          const current = toolContent.current;
          content = `${location}当前天气：\n`;
          if (current.temp) content += `温度：${current.temp}°C\n`;
          if (current.condition && current.condition.text) content += `天气：${current.condition.text}\n`;
          if (current.wind_kph) content += `风力：${current.wind_kph} km/h\n`;
          if (current.humidity) content += `湿度：${current.humidity}%\n`;
          if (current.air_quality && current.air_quality.us_epa_index) {
            const airQuality = current.air_quality.us_epa_index;
            content += `空气质量：${airQuality === 1 ? '优' : airQuality === 2 ? '良' : airQuality === 3 ? '轻度污染' : airQuality === 4 ? '中度污染' : airQuality === 5 ? '重度污染' : '严重污染'}\n`;
          }
        } else {
          // 其他工具结果，尝试解析为JSON
          try {
            const contentStr = JSON.stringify(toolContent);
            const parsed = JSON.parse(contentStr);
            if (parsed.result) {
              content = parsed.result;
            } else if (parsed.args && parsed.args.result) {
              content = parsed.args.result;
            } else {
              content = contentStr;
            }
          } catch (e) {
            content = String(toolContent);
          }
        }
      } else if (typeof toolContent === 'string') {
        // 字符串类型，尝试解析为JSON
        try {
          const parsed = JSON.parse(toolContent);
          if (parsed.result) {
            content = parsed.result;
          } else if (parsed.args && parsed.args.result) {
            content = parsed.args.result;
          } else if (toolContent.includes('Returning structured response:')) {
            // 提取结果部分
            const structuredStart = toolContent.indexOf('Returning structured response:') + 'Returning structured response:'.length;
            let structuredContent = toolContent.substring(structuredStart).trim();
            
            // 尝试提取result值
            const resultMatch = structuredContent.match(/result='([^']+)'/);
            if (resultMatch && resultMatch[1]) {
              content = resultMatch[1];
            } else {
              const resultMatchDoubleQuote = structuredContent.match(/result="([^"]+)"/);
              if (resultMatchDoubleQuote && resultMatchDoubleQuote[1]) {
                content = resultMatchDoubleQuote[1];
              } else {
                content = structuredContent;
              }
            }
          } else {
            content = toolContent;
          }
        } catch (e) {
          // 不是JSON字符串，直接使用
          content = toolContent;
        }
      } else {
        content = toolContent;
      }
      // 处理换行符
      if (typeof content === 'string') {
        content = content.replace(/\n/g, '\n');
        // 去除多余的空白字符
        content = content.trim();
      } else {
        // 如果content不是字符串，转换为字符串
        content = String(content);
      }
    }
    
    if (content) {
      const normalizedType = normalizeMessageType(type);
      const timestamp = new Date(msg.timestamp).toLocaleTimeString('zh-CN', { hour12: false });
      const logItem = {
        type: normalizedType,
        content: content,
        timestamp
      };
      // 添加tool_name字段（如果有）
      if (msg.name) {
        logItem.tool_name = msg.name;
      }
      app.processLogs.push(logItem);
    }
  });
  
  app.$nextTick(() => {
    scrollToBottom();
  });
}
