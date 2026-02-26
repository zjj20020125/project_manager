<template>
  <div class="extension-test-page">
    <h2>浏览器扩展干扰测试</h2>
    
    <el-card class="test-section">
      <template #header>
        <div class="card-header">
          <span>测试区域</span>
        </div>
      </template>
      
      <div class="test-content">
        <el-button type="primary" @click="testApiCall">
          测试API调用
        </el-button>
        
        <el-button type="success" @click="testExtensionDetection">
          测试扩展检测
        </el-button>
        
        <el-button type="warning" @click="simulateExtensionError">
          模拟扩展错误
        </el-button>
      </div>
      
      <div class="result-section" v-if="testResult">
        <h3>测试结果:</h3>
        <pre>{{ testResult }}</pre>
      </div>
    </el-card>
    
    <el-card class="info-section">
      <template #header>
        <div class="card-header">
          <span>常见解决方案</span>
        </div>
      </template>
      
      <ul>
        <li>禁用广告拦截器扩展（如AdBlock、uBlock Origin）</li>
        <li>禁用隐私保护扩展（如Privacy Badger、Ghostery）</li>
        <li>在无痕/隐私模式下浏览</li>
        <li>刷新页面重试</li>
        <li>检查网络连接是否稳定</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { projectApi } from '@/api';
import { isExtensionInterferenceError, showExtensionError } from '@/utils/extensionHandler';

const testResult = ref('');

const testApiCall = async () => {
  try {
    testResult.value = '正在测试API调用...';
    const result = await projectApi.getProjectStats();
    testResult.value = `API调用成功: ${JSON.stringify(result, null, 2)}`;
    ElMessage.success('API调用测试成功');
  } catch (error) {
    testResult.value = `API调用失败: ${JSON.stringify(error, null, 2)}`;
    if (isExtensionInterferenceError(error)) {
      ElMessage.warning('检测到浏览器扩展干扰');
    } else {
      ElMessage.error('API调用失败');
    }
  }
};

const testExtensionDetection = () => {
  // 创建一个模拟的扩展干扰错误
  const mockError = new Error('A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received');
  
  const isInterference = isExtensionInterferenceError(mockError);
  testResult.value = `扩展干扰检测结果: ${isInterference ? '检测到干扰' : '未检测到干扰'}`;
  
  if (isInterference) {
    showExtensionError();
    ElMessage.info('已显示扩展干扰提示');
  }
};

const simulateExtensionError = () => {
  // 模拟一个真实的扩展错误场景
  testResult.value = '模拟扩展干扰错误...';
  
  // 创建一个Promise来模拟异步错误
  new Promise((_, reject) => {
    setTimeout(() => {
      const error = new Error('A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received');
      reject(error);
    }, 100);
  }).catch(error => {
    if (isExtensionInterferenceError(error)) {
      testResult.value = `成功识别扩展干扰错误: ${error.message}`;
      showExtensionError();
    } else {
      testResult.value = `未能识别为扩展干扰错误: ${error.message}`;
    }
  });
};
</script>

<style scoped>
.extension-test-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section, .info-section {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
}

.test-content {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.result-section {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

.result-section pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.info-section ul {
  margin: 0;
  padding-left: 20px;
}

.info-section li {
  margin-bottom: 8px;
}
</style>