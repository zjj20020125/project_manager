// utils/extensionHandler.js - 浏览器扩展干扰处理工具
import { ElMessage } from 'element-plus';

// 全局错误通知标志，避免重复提示
window.extensionErrorNotified = false;

/**
 * 检测是否为浏览器扩展干扰错误
 * @param {Error} error - 错误对象
 * @returns {boolean} 是否为扩展干扰错误
 */
export function isExtensionInterferenceError(error) {
  if (!error || !error.message) return false;
  
  const interferencePatterns = [
    'A listener indicated an asynchronous response',
    'message channel closed',
    'Unchecked runtime.lastError',
    'Extension',
    'listener',
    'chrome-extension',
    'moz-extension'
  ];
  
  const message = error.message.toLowerCase();
  return interferencePatterns.some(pattern => 
    message.includes(pattern.toLowerCase())
  );
}

/**
 * 处理浏览器扩展干扰错误
 * @param {Error} error - 错误对象
 * @param {Object} config - 请求配置
 * @param {Function} retryFunction - 重试函数
 * @returns {Promise} 处理结果
 */
export async function handleExtensionInterference(error, config, retryFunction) {
  console.warn('检测到浏览器扩展干扰:', error.message);
  
  // 清理Chrome运行时错误
  if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.lastError) {
    chrome.runtime.lastError = null;
  }
  
  // 设置重试计数
  if (!config.__retryCount) {
    config.__retryCount = 0;
  }
  
  // 限制重试次数
  if (config.__retryCount < 3) {
    config.__retryCount += 1;
    console.log(`第 ${config.__retryCount} 次重试请求:`, config.url);
    
    // 延迟重试
    await new Promise(resolve => setTimeout(resolve, 1500));
    return retryFunction();
  } else {
    // 重试次数用完，显示用户友好的错误提示
    showExtensionError();
    return Promise.reject({
      message: '浏览器扩展干扰，请尝试以下解决方案：\n1. 禁用广告拦截器或隐私保护扩展\n2. 刷新页面重试\n3. 使用无痕/隐私模式浏览',
      type: 'extension_interference',
      originalError: error.message
    });
  }
}

/**
 * 显示浏览器扩展干扰错误提示
 */
export function showExtensionError() {
  // 避免重复提示
  if (window.extensionErrorNotified) {
    return;
  }
  
  window.extensionErrorNotified = true;
  
  ElMessage({
    message: `
      <div style="text-align: left;">
        <strong>🚨 检测到浏览器扩展干扰</strong><br>
        请尝试以下解决方案：<br>
        1. 🔧 禁用广告拦截器或隐私保护扩展<br>
        2. 🔄 刷新页面重试<br>
        3. 👻 使用无痕/隐私模式浏览<br>
        4. 🌐 更换浏览器测试
      </div>
    `,
    type: 'warning',
    duration: 10000,
    showClose: true,
    dangerouslyUseHTMLString: true,
    grouping: true
  });
  
  // 60秒后重置通知标志
  setTimeout(() => {
    window.extensionErrorNotified = false;
  }, 60000);
}

/**
 * 初始化扩展干扰监控
 */
export function initExtensionMonitoring() {
  // 监控未处理的Promise拒绝
  window.addEventListener('unhandledrejection', (event) => {
    if (isExtensionInterferenceError(event.reason)) {
      console.warn('捕获到未处理的扩展干扰错误:', event.reason.message);
      event.preventDefault(); // 阻止错误冒泡到控制台
    }
  });
  
  // 监控全局错误
  window.addEventListener('error', (event) => {
    if (isExtensionInterferenceError(event.error)) {
      console.warn('捕获到扩展干扰错误:', event.error.message);
      event.preventDefault();
    }
  });
}

// 自动初始化监控
initExtensionMonitoring();

export default {
  isExtensionInterferenceError,
  handleExtensionInterference,
  showExtensionError,
  initExtensionMonitoring
};