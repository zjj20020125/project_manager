// api/index.js - API服务接口
import axios from 'axios';

// 创建axios实例，配置基础URL和默认参数
const apiClient = axios.create({
  baseURL: '/api', // API的基础路径，使用代理转发 - 代理会自动添加/v1前缀
  timeout: 15000, // 增加请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，比如添加认证token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('发起API请求:', config.url, config.method); // 添加请求日志
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
    console.log('API响应成功:', response.config.url, response.status); // 添加响应日志
    return response.data;
  },
  error => {
    // 对响应错误做点什么
    console.error('API Error:', error.response || error.message || error);
    
    // 根据错误类型提供更友好的错误信息
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时');
    } else if (error.response) {
      console.error(`HTTP错误 ${error.response.status}: ${error.response.statusText}`);
    } else if (error.request) {
      console.error('网络错误：无法连接到服务器');
    } else {
      console.error('请求配置错误:', error.message);
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
  
  // 获取任务负责人统计
  getTaskOwnerStats: () => apiClient.get('/v1/task-owner-stats'),
  
  // 获取项目列表
  getProjectsList: () => apiClient.get('/v1/projects-list'),
  
  // 获取指定负责人负责的任务详情
  getOwnerTasks: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/v1/owner-tasks/${encodedOwner}`);
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
  
  // 根据阶段获取NCR数据
  getNcrByStage: (params = {}) => {
    const { stage = '', status = '', priority = '', page = 1, limit = 20 } = params;
    const queryParams = new URLSearchParams();
    if (stage) queryParams.append('stage', stage);
    if (status) queryParams.append('status', status);
    if (priority) queryParams.append('priority', priority);
    queryParams.append('page', page);
    queryParams.append('limit', limit);
    
    return apiClient.get(`/v1/ncr/by-stage?${queryParams.toString()}`);
  },
  
  // 获取NCR详情
  getNcrDetail: (processNo) => apiClient.get(`/v1/ncr/detail/${processNo}`),
  
  // 获取NCR列表
  getNcrList: (params = {}) => {
    const { page = 1, limit = 20 } = params;
    const queryParams = new URLSearchParams();
    queryParams.append('page', page);
    queryParams.append('limit', limit);
    
    return apiClient.get(`/v1/ncr/list?${queryParams.toString()}`);
  },
  
  // 获取DQJD和WCZZ数据统计
  getDqjdWczzData: () => apiClient.get('/v1/dqjd-wczz-data'),
  
  // 导入项目数据
  importProjects: (formData) => apiClient.post('/v1/projects/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  
  // 导出项目数据
  exportProjects: (projectIds) => {
    return apiClient.post('/v1/projects/export', { project_ids: projectIds }, {
      responseType: 'blob'
    }).then(response => {
      // 检查响应是否为blob类型
      if (response && response.data instanceof Blob) {
        return response.data; // 返回实际的blob数据
      } else {
        // 如果不是预期的blob响应，抛出错误
        throw new Error('服务器返回了意外的响应格式');
      }
    }).catch(error => {
      console.error('导出项目数据失败:', error);
      throw error;
    });
  }
};

export default apiClient;