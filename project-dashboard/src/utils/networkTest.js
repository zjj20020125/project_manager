// 网络连接测试工具
export const testNetworkConnection = async () => {
  try {
    console.log('开始网络连接测试...');
    
    // 测试基础连接
    const healthCheck = await fetch('/api/health');
    console.log('健康检查状态:', healthCheck.status);
    
    if (!healthCheck.ok) {
      throw new Error(`健康检查失败: ${healthCheck.status}`);
    }
    
    // 测试甘特图API
    const ganttTest = await fetch('/api/v1/task-gantt-data');
    console.log('甘特图API测试状态:', ganttTest.status);
    
    if (!ganttTest.ok) {
      throw new Error(`甘特图API测试失败: ${ganttTest.status}`);
    }
    
    const testData = await ganttTest.json();
    console.log('甘特图API返回数据:', testData);
    console.log('测试数据长度:', Array.isArray(testData) ? testData.length : 'Not an array');
    
    console.log('✅ 网络连接测试通过');
    return true;
  } catch (error) {
    console.error('❌ 网络连接测试失败:', error);
    return false;
  }
};

// 检查API可用性
export const checkApiAvailability = async () => {
  const apis = [
    { name: '健康检查', url: '/api/health' },
    { name: '甘特图数据', url: '/api/v1/task-gantt-data' },
    { name: '项目统计', url: '/api/v1/project/stats' }
  ];
  
  const results = [];
  
  for (const api of apis) {
    try {
      const response = await fetch(api.url, { method: 'GET', timeout: 5000 });
      results.push({
        name: api.name,
        url: api.url,
        status: response.status,
        ok: response.ok,
        error: null
      });
    } catch (error) {
      results.push({
        name: api.name,
        url: api.url,
        status: null,
        ok: false,
        error: error.message
      });
    }
  }
  
  console.table(results);
  return results;
};