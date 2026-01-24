// api/index.js - API服务接口
import axios from 'axios';

// 创建axios实例，配置基础URL和默认参数
const apiClient = axios.create({
  baseURL: '/api/v1', // API的基础路径，使用代理转发 - 修改为后端实际API前缀
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
  getProjectStats: () => apiClient.get('/project/stats'),
  
  // 获取任务统计数据
  getTaskStats: () => apiClient.get('/task/stats'),
  
  // 获取图表数据
  getChartData: () => apiClient.get('/chart/data'),
  
  // 获取任务列表
  getTaskList: (params = {}) => {
    const { page = 1, limit = 20 } = params;
    const offset = (page - 1) * limit;
    return apiClient.get(`/task/list?limit=${limit}&offset=${offset}`);
  },
  
  // 获取项目详细数据并分类
  getProjectsDetail: () => apiClient.get('/projects/detail'),
  
  // 获取项目分类统计
  getProjectCategoryStats: () => apiClient.get('/projects/stats'),
  
  // 根据项目状态获取项目列表
  getProjectsByStatus: (params = {}) => {
    const { status = '', page = 1, limit = 10 } = params;
    const offset = (page - 1) * limit;
    let url = `/projects/status/${status}?limit=${limit}&offset=${offset}`;
    return apiClient.get(url);
  },
  
  // 根据任务类型获取任务列表
  getTasksByType: (params = {}) => {
    const { type = '', page = 1, limit = 10 } = params;
    const offset = (page - 1) * limit;
    let url = `/tasks/type/${type}?limit=${limit}&offset=${offset}`;
    return apiClient.get(url);
  },
  
  // 获取指定类型任务的总数
  getTasksByTypeCount: (type) => {
    return apiClient.get(`/tasks/type/${type}/count`);
  },
  
  // 获取项目状态分布数据
  getProjectStatusStats: () => apiClient.get('/project-status-stats'),
  
  // 获取任务进度甘特图数据
  getTaskGanttData: (projectName = null) => {
    const params = projectName ? `?project_name=${encodeURIComponent(projectName)}` : '';
    return apiClient.get(`/task-gantt-data${params}`);
  },
  
  // 获取任务负责人统计
  getTaskOwnerStats: () => apiClient.get('/task-owner-stats'),
  
  // 获取项目列表
  getProjectsList: () => apiClient.get('/projects-list'),
  
  // 获取指定负责人负责的任务详情
  getOwnerTasks: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/owner-tasks/${encodedOwner}`);
  },
  
  // 根据任务状态获取任务列表
  getTasksByStatus: (status, params = {}) => {
    const { page = 1, limit = 100 } = params;
    const offset = (page - 1) * limit;
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/tasks/status/${encodedStatus}?limit=${limit}&offset=${offset}`);
  },
  
  // 根据项目状态获取对应的任务数据
  getTasksByProjectStatus: (status) => {
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/tasks-by-status/${encodedStatus}`);
  },
  
  // 根据项目状态获取任务数据
  getTasksByProjectStatusTasks: (status) => {
    const encodedStatus = encodeURIComponent(status);
    return apiClient.get(`/tasks-by-project-status/${encodedStatus}`);
  },
  
  // 获取指定负责人任务总数
  getOwnerTasksCount: (owner) => {
    const encodedOwner = encodeURIComponent(owner);
    return apiClient.get(`/owner-tasks-count/${encodedOwner}`);
  }
};

export default apiClient;