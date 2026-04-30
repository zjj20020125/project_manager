// api/index.js - API服务接口
import axios from 'axios';
import { isExtensionInterferenceError, handleExtensionInterference } from '@/utils/extensionHandler';

// 创建axios实例，配置基础URL和默认参数
const apiClient = axios.create({
  baseURL: '/api', // API的基础路径，使用代理转发 - 代理会自动添加/v1前缀
  timeout: 30000, // 增加请求超时时间到30秒
  headers: {
    'Content-Type': 'application/json',
  },
  // 配置重试机制
  retry: 3,
  retryDelay: 1000
});

// 添加基础URL调试信息
console.log('API Client BaseURL:', apiClient.defaults.baseURL);
console.log('Current Location:', window.location.href);

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，比如添加认证token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加完整的请求URL信息
    const fullUrl = `${config.baseURL || ''}${config.url}`;
    console.log('发起API请求:', {
      method: config.method,
      url: fullUrl,
      baseURL: config.baseURL,
      path: config.url
    });
    
    return config;
  },
  error => {
    console.error('请求拦截器错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    console.log('✅ API 响应成功:', response.config.url, response.status); // 添加响应日志
    
    // 如果是 blob 类型的响应，直接返回 response.data
    if (response.config.responseType === 'blob') {
      return response.data;
    }
    
    return response.data;
  },
  async error => {
    console.log('❌ API响应错误:', error.message);
    
    // 处理Promise相关的异步错误
    if (error.message && (error.message.includes('message channel closed') || 
                          error.message.includes('A listener indicated an asynchronous response'))) {
      console.warn('🔧 检测到消息通道关闭错误，可能是扩展干扰');
      const config = error.config;
      
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
        console.log(`🔄 第 ${config.__retryCount} 次重试请求:`, config.url);
        
        // 延迟重试
        await new Promise(resolve => setTimeout(resolve, 1500));
        return apiClient(config);
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
    
    // 使用专门的扩展干扰处理工具
    if (isExtensionInterferenceError(error)) {
      console.warn('🔧 检测到扩展干扰错误，启动处理流程');
      const config = error.config;
      if (config) {
        try {
          return await handleExtensionInterference(error, config, () => apiClient(config));
        } catch (handledError) {
          // 如果处理工具返回了自定义错误对象
          console.error('🔄 扩展干扰处理失败:', handledError);
          return Promise.reject(handledError);
        }
      }
    }
    
    // 处理网络中断错误
    if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      console.warn('🌐 网络连接中断，尝试重新连接...');
      const config = error.config;
      if (config && (!config.__retryCount || config.__retryCount < 2)) {
        if (!config.__retryCount) config.__retryCount = 0;
        config.__retryCount += 1;
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            apiClient(config).then(resolve).catch(reject);
          }, 2000);
        });
      }
    }
    
    // 对其他响应错误做点什么
    console.error('💥 API Error Details:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message
    });
    
    // 根据错误类型提供更友好的错误信息
    if (error.code === 'ECONNABORTED') {
      console.error('⏰ 请求超时');
    } else if (error.response) {
      console.error(`📡 HTTP错误 ${error.response.status}: ${error.response.statusText}`);
    } else if (error.request) {
      console.error('🔌 网络错误：无法连接到服务器');
    } else {
      console.error('⚙️ 请求配置错误:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// 项目数据相关API
export const projectApi = {
  // 获取项目统计数据
  getProjectStats: () => apiClient.get('/v1/project/stats'),
  
  // 获取任务统计数据
  getTaskStats: () => apiClient.get('/v1/task/stats'),
  
  // 获取图表数据
  getChartData: () => apiClient.get('/v1/chart/data'),
  
  // 获取任务列表
  getTaskList: (params = {}) => {
    const { page = 1, limit = 20 } = params;
    const offset = (page - 1) * limit;
    return apiClient.get(`/v1/task/list?limit=${limit}&offset=${offset}`);
  },
  
  // 获取项目详细数据并分类
  getProjectsDetail: () => apiClient.get('/v1/projects/detail'),
  
  // 获取项目分类统计
  getProjectCategoryStats: () => apiClient.get('/v1/projects/stats'),
  
  // 根据项目状态获取项目列表
  getProjectsByStatus: (params = {}) => {
    const { status = '', page = 1, limit = 10 } = params;
    const offset = (page - 1) * limit;
    let url = `/v1/projects/status/${status}?limit=${limit}&offset=${offset}`;
    return apiClient.get(url);
  },
  
  // 根据任务类型获取任务列表
  getTasksByType: (params = {}) => {
    const { type = '', page = 1, limit = 10 } = params;
    const offset = (page - 1) * limit;
    let url = `/v1/tasks/type/${type}?limit=${limit}&offset=${offset}`;
    return apiClient.get(url);
  },
  
  // 获取指定类型任务的总数
  getTasksByTypeCount: (type) => {
    return apiClient.get(`/v1/tasks/type/${type}/count`);
  },
  
  // 获取项目状态分布数据
  getProjectStatusStats: () => apiClient.get('/v1/project-status-stats'),
  
  // 获取任务进度甘特图数据
  getTaskGanttData: (projectName = null) => {
    const params = projectName ? `?project_name=${encodeURIComponent(projectName)}` : '';
    return apiClient.get(`/v1/task-gantt-data${params}`);
  },
  
  // 获取异常节点负责人统计
  getAbnormalTaskOwnerStats: () => apiClient.get('/v1/abnormal-task-owner-stats'),
  
  // 获取项目列表
  getProjectsList: () => apiClient.get('/v1/projects-list'),
  
  // 获取指定负责人负责的任务详情
  getOwnerTasks: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/v1/owner-tasks/${encodedOwner}`);
  },
  
  // 获取指定负责人负责的异常任务详情
  getOwnerAbnormalTasks: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/v1/owner-abnormal-tasks/${encodedOwner}`);
  },
  
  // 获取指定负责人的异常任务详情（区分首个异常节点和进度推迟）
  getAbnormalTaskDetailByOwner: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/v1/task/abnormal-detail/${encodedOwner}`);
  },
  
  // 根据任务状态获取任务列表
  getTasksByStatus: (status, params = {}) => {
    const { page = 1, limit = 100 } = params;
    const offset = (page - 1) * limit;
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/v1/tasks/status/${encodedStatus}?limit=${limit}&offset=${offset}`);
  },
  
  // 根据项目状态获取对应的任务数据
  getTasksByProjectStatus: (status) => {
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/v1/tasks-by-status/${encodedStatus}`);
  },
  
  // 根据项目状态获取任务数据
  getTasksByProjectStatusTasks: (status) => {
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/v1/tasks-by-project-status/${encodedStatus}`);
  },
  
  // 根据状态获取project_tasks表中的完整数据
  getProjectTasksByStatus: (status) => {
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/v1/project-tasks/status/${encodedStatus}`);
  },
  
  // 根据项目ID或项目名称获取子任务数据
  getProjectSubtasks: (projectIdentifier) => {
    const encodedIdentifier = encodeURIComponent(projectIdentifier);
    return apiClient.get(`/v1/project-subtasks/${encodedIdentifier}`);
  },
  
  // 获取指定负责人任务总数
  getOwnerTasksCount: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/v1/owner-tasks-count/${encodedOwner}`);
  },
  
  // 获取NCR类型分布统计
  getNcrTypeDistribution: () => apiClient.get('/v1/ncr/type-distribution'),
  
  // 获取NCR发生阶段分布统计
  getNcrStageDistribution: () => apiClient.get('/v1/ncr/stage-distribution'),
  
  // 获取评审阶段责任人员分布统计
  getResponsibilityAnalysis: () => apiClient.get('/v1/ncr/responsibility-analysis'),
  
  // 根据阶段获取 NCR 数据
  getNcrByStage: (params = {}) => {
    const { stage = '', status = '', priority = '', page = 1, limit = 20 } = params;
    const queryParams = new URLSearchParams();
    if (stage) queryParams.append('stage', stage);
    if (status) queryParams.append('status', status);
    if (priority) queryParams.append('priority', priority);
    queryParams.append('page', page);
    queryParams.append('limit', limit);
      
    const url = `/v1/ncr/by-stage?${queryParams.toString()}`;
    console.log('🌐 API 请求 URL:', url);
      
    return apiClient.get(url);
  },
  
  // 获取NCR详情
  getNcrDetail: (processNo) => apiClient.get(`/v1/ncr/detail/${processNo}`),
  
  // 获取 NCR 列表
  getNcrList: (params = {}) => {
    const { page = 1, limit = 20 } = params;
    const queryParams = new URLSearchParams();
    queryParams.append('page', page);
    queryParams.append('limit', limit);
      
    return apiClient.get(`/v1/ncr/list?${queryParams.toString()}`);
  },
  
  // 获取NCR统计数据（用于顶部卡片）
  getNcrStats: () => apiClient.get('/v1/ncr/stats'),
    
  // 获取当前节点详情数据
  getNcrCurrentNodeDetail: (nodeInfo) => {
    return apiClient.post('/v1/ncr/current-node-detail', nodeInfo);
  },
  
  // 获取DQJD和WCZZ数据统计
  getDqjdWczzData: () => apiClient.get('/v1/dqjd-wczz-data'),
  
  // 获取未评审状态下的负责人统计（前15名）
  getUnreviewedResponsibilityStats: () => apiClient.get('/v1/ncr/unreviewed-responsibility'),
  
  // 获取未评审阶段责任人员分布统计（前15名）
  getUnreviewedStageResponsibility: () => apiClient.get('/v1/ncr/unreviewed-stage-responsibility'),
  
  // 获取SSCX字段统计（近一年数据）
  getSscxStatistics: () => apiClient.get('/v1/ncr/sscx-statistics'),
  
  // 获取SSCX时间趋势统计（按月份展示近一年数据）
  getSscxTrendStatistics: () => apiClient.get('/v1/ncr/sscx-trend'),
  
  // 获取 SSCX 字段近一年统计数据（前 15 名）
  getSscxYearlyStats: () => apiClient.get('/v1/ncr/sscx-yearly-stats'),
    
  // 获取问题导向三层级统计（wtdx -> wtfl -> wtflxf）
 getNcrProblemHierarchyStats: () => apiClient.get('/v1/ncr/problem-hierarchy-stats'),
  
  // 获取 NCR 统计趋势数据
  getNcrStatsTrend: () => apiClient.get('/v1/ncr/stats-trend'),
  
  // 获取问题层级详情列表（根据 wtdx/wtfl/wtflxf筛选）
 getNcrByProblemHierarchy: (params) => apiClient.get('/v1/ncr/problem-hierarchy-detail', { params }),
  
  // 导入项目数据
  importProjects: (formData, overwrite = false) => {
    const params = new URLSearchParams();
    if (overwrite) {
      params.append('overwrite', 'true');
    }
    
    return apiClient.post(`/v1/projects/import?${params.toString()}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // 更新项目信息
  updateProjectInfo: (projectData) => {
    return apiClient.put('/v1/projects/update', projectData);
  },
  
  // 导出项目数据
  exportProjects: (projectIds) => {
    return apiClient.post('/v1/projects/export', { project_ids: projectIds }, {
      responseType: 'blob'
    }).then(response => {
      console.log('导出响应数据:', {
        response,
        responseDataType: typeof response,
        isBlob: response instanceof Blob,
        responseSize: response.size
      });
        
      // 检查响应是否为 blob 类型
      if (response instanceof Blob) {
        return response; // 返回实际的 blob 数据
      } else {
        // 如果不是预期的 blob 响应，抛出错误
        console.error('意外的响应类型:', typeof response, response);
        throw new Error('服务器返回了意外的响应格式');
      }
    }).catch(error => {
      console.error('导出项目数据失败:', error);
      throw error;
    });
  },
  
  // 删除单个项目
  deleteProject: (projectId) => {
    return apiClient.delete(`/v1/projects/${projectId}`);
  },
  
  // 批量删除项目
  batchDeleteProjects: (projectIds) => {
    return apiClient.post('/v1/projects/batch-delete', projectIds);
  },
  
  // 修改项目信息（带项目ID）
  updateProject: (projectId, projectData) => {
    return apiClient.put(`/v1/projects/${projectId}`, projectData);
  },
  
  // 更新任务信息
  updateTask: (taskId, taskData) => {
    return apiClient.put(`/v1/task/${taskId}`, taskData);
  },
  
  // 刷新所有项目状态（根据最新任务数据重新计算）
  refreshProjectsStatus: () => {
    return apiClient.post('/v1/projects/refresh-status');
  }
};

// 客户反馈相关 API
export const feedbackApi = {
  // 获取反馈统计数据
  getFeedbackStats: () => apiClient.get('/v1/feedback/stats'),
  
  // 获取反馈列表
  getFeedbackList: (params = {}) => {
    const { page = 1, limit = 20, status, feedback_type, priority, keyword } = params;
    let url = `/v1/feedback/list?page=${page}&limit=${limit}`;
    if (status) url += `&status=${status}`;
    if (feedback_type) url += `&feedback_type=${feedback_type}`;
    if (priority) url += `&priority=${priority}`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
    return apiClient.get(url);
  },
  
  // 获取反馈详情
  getFeedbackDetail: (feedbackId) => apiClient.get(`/v1/feedback/${feedbackId}`),
  
  // 创建反馈
  createFeedback: (feedbackData) => apiClient.post('/v1/feedback/', feedbackData),
  
  // 更新反馈
  updateFeedback: (feedbackId, feedbackData) => apiClient.put(`/v1/feedback/${feedbackId}`, feedbackData),
  
  // 删除反馈
  deleteFeedback: (feedbackId) => apiClient.delete(`/v1/feedback/${feedbackId}`),
  
  // 导出反馈数据
  exportFeedback: (params = {}) => {
    const { status, feedback_type, start_date, end_date } = params;
    let url = '/v1/feedback/export/excel?';
    if (status) url += `&status=${status}`;
    if (feedback_type) url += `&feedback_type=${feedback_type}`;
    if (start_date) url += `&start_date=${start_date}`;
    if (end_date) url += `&end_date=${end_date}`;
    return apiClient.get(url);
  },
  
  // 获取质量问题统计数据
  getProblemStats: (params = {}) => {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    return apiClient.get(`/v1/feedback/problem/stats?${queryParams.toString()}`);
  },
  
  // 获取质量问题列表
  getProblemList: (params = {}) => {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    return apiClient.get(`/v1/feedback/problem/list?${queryParams.toString()}`);
  },
  
  // 获取质量问题详情
  getProblemDetail: (problemId) => apiClient.get(`/v1/feedback/problem/detail/${problemId}`),
  
  // 获取质量问题筛选条件选项
  getProblemFilters: () => apiClient.get('/v1/feedback/problem/filters'),
  
  // 创建质量问题
  createProblem: (problemData) => apiClient.post('/v1/feedback/problem/', problemData),
};

export default apiClient;