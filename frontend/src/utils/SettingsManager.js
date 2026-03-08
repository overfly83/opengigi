/**
 * 设置管理工具类
 * 负责设置的加载、保存和应用
 */

// 设置相关常量
const SETTINGS_KEY = 'appSettings';

// 默认设置
const DEFAULT_SETTINGS = {
  theme: 'light',
  fontSize: 'normal',
  sidebarWidth: 320
};

/**
 * 从本地存储加载设置
 * @returns {Object} 设置对象
 */
export function loadSettings() {
  const savedSettings = localStorage.getItem(SETTINGS_KEY);
  return savedSettings ? { ...DEFAULT_SETTINGS, ...JSON.parse(savedSettings) } : DEFAULT_SETTINGS;
}

/**
 * 保存设置到本地存储
 * @param {Object} settings - 设置对象
 */
export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

/**
 * 应用设置
 * @param {Object} settings - 设置对象
 */
export function applySettings(settings) {
  // 应用主题
  if (settings.theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  
  // 应用字体大小
  document.documentElement.classList.remove('text-sm', 'text-base', 'text-lg');
  switch (settings.fontSize) {
    case 'small':
      document.documentElement.classList.add('text-sm');
      break;
    case 'large':
      document.documentElement.classList.add('text-lg');
      break;
    default:
      document.documentElement.classList.add('text-base');
  }
}

/**
 * 处理设置保存事件
 * @param {Object} app - 应用实例
 * @param {Object} settings - 设置对象
 */
export function handleSettingsSave(app, settings) {
  // 保存设置
  saveSettings(settings);
  // 更新应用状态
  app.sidebarWidth = settings.sidebarWidth;
  app.settings = settings;
  // 应用设置
  applySettings(settings);
}

/**
 * 更新侧边栏宽度
 * @param {Object} app - 应用实例
 * @param {number} width - 新的宽度
 */
export function updateSidebarWidth(app, width) {
  app.sidebarWidth = width;
  // 更新设置
  const updatedSettings = { ...app.settings, sidebarWidth: width };
  app.settings = updatedSettings;
  saveSettings(updatedSettings);
}
