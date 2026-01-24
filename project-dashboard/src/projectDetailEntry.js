import { createApp } from 'vue'
import ProjectDetailPage from './components/ProjectDetailPage.vue'

// 获取URL参数中的状态值
const urlParams = new URLSearchParams(window.location.search);
const status = urlParams.get('status') || 'total';

// 创建Vue应用并挂载到DOM
const app = createApp(ProjectDetailPage, {
  status: status
});
app.mount('#project-detail-app');