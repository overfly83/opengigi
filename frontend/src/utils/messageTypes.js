/**
 * 消息类型定义
 * 与后台保持一致
 */

// 消息类型枚举
export const MessageType = {
  // 基础消息类型
  HUMAN: 'human',        // 人类消息
  AI: 'ai',              // AI消息
  TOOL_CALL: 'tool_call', // 工具调用
  TOOL_RESULT: 'tool_result', // 工具结果
  SYSTEM: 'system',      // 系统消息
  ERROR: 'error',        // 错误消息
  STREAMING: 'streaming', // 流式消息
  MESSAGE_DELTA: 'message_delta', // 消息增量
  MESSAGE_COMPLETE: 'message_complete', // 消息完成
  DONE: 'done'          // 完成标记
};

// 消息类型对应的图标
export const MessageIcon = {
  [MessageType.HUMAN]: 'fa-comment-dots',
  [MessageType.AI]: 'fa-robot',
  [MessageType.TOOL_CALL]: 'fa-tools',
  [MessageType.TOOL_RESULT]: 'fa-toolbox',
  [MessageType.SYSTEM]: 'fa-info-circle',
  [MessageType.ERROR]: 'fa-exclamation-circle',
  [MessageType.STREAMING]: 'fa-play-circle'
};

// 消息类型对应的颜色
export const MessageColor = {
  [MessageType.HUMAN]: 'text-blue-500',
  [MessageType.AI]: 'text-orange-300',
  [MessageType.TOOL_CALL]: 'text-purple-500',
  [MessageType.TOOL_RESULT]: 'text-indigo-500',
  [MessageType.SYSTEM]: 'text-gray-500',
  [MessageType.ERROR]: 'text-red-500',
  [MessageType.STREAMING]: 'text-gray-500'
};

// 消息类型对应的背景色
export const MessageBgColor = {
  [MessageType.HUMAN]: 'bg-blue-50',
  [MessageType.AI]: 'bg-teal-50',
  [MessageType.TOOL_CALL]: 'bg-purple-50',
  [MessageType.TOOL_RESULT]: 'bg-indigo-50',
  [MessageType.SYSTEM]: 'bg-gray-50',
  [MessageType.ERROR]: 'bg-red-50',
  [MessageType.STREAMING]: 'bg-gray-100'
};

/**
 * 根据消息类型获取图标
 * @param {string} messageType - 消息类型
 * @returns {string} 图标类名
 */
export function getMessageIcon(messageType) {
  return MessageIcon[messageType] || 'fa-comment';
}

/**
 * 根据消息类型获取颜色
 * @param {string} messageType - 消息类型
 * @returns {string} 颜色类名
 */
export function getMessageColor(messageType) {
  return MessageColor[messageType] || 'text-gray-500';
}

/**
 * 根据消息类型获取背景色
 * @param {string} messageType - 消息类型
 * @returns {string} 背景色类名
 */
export function getMessageBgColor(messageType) {
  return MessageBgColor[messageType] || 'bg-gray-50';
}

/**
 * 标准化消息类型
 * @param {string} messageType - 消息类型
 * @returns {string} 标准化后的消息类型
 */
export function normalizeMessageType(messageType) {
  const validTypes = Object.values(MessageType);
  return validTypes.includes(messageType) ? messageType : MessageType.SYSTEM;
}
