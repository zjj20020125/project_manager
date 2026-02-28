import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import HomePage from '../views/HomePage.vue'
import ProjectDetailView from '../views/project/ProjectDetailView.vue'
import TaskDetailView from '../views/project/TaskDetailView.vue'
import ProjectSubtasksDetailView from '../views/project/ProjectSubtasksDetailView.vue'
import OwnerTaskDetailView from '../views/project/OwnerTaskDetailView.vue'
import ProjectStatusDetailView from '../views/project/ProjectStatusDetailView.vue'
import ProjectManagerDetailView from '../views/project/ProjectManagerDetailView.vue'
import OwnerProjectSubtasksView from '../views/project/OwnerProjectSubtasksView.vue'
import MilestoneTaskDetailView from '../views/MilestoneTaskDetailView.vue'
import CompletedMilestoneTaskDetailView from '../views/CompletedMilestoneTaskDetailView.vue'
import SubTaskDetailView from '../views/project/SubTaskDetailView.vue'
import AcceptedTaskDetailView from '../views/AcceptedTaskDetailView.vue'
import ProjectStatusSubtasksDetailView from '../views/ProjectStatusSubtasksDetailView.vue'
import NcrFlowChart from '../views/ncr/NcrFlowChart.vue'
import NcrStageDetail from '../views/ncr/NcrStageDetail.vue'
import NcrItemDetail from '../views/ncr/NcrItemDetail.vue'
import NcrHomePage from '../views/ncr/NcrHomePage.vue'
import NcrDashboard from '../views/ncr/NcrDashboard.vue'
import NcrEnhancedDashboard from '../views/ncr/NcrEnhancedDashboard.vue'
import SscxStatistics from '../views/ncr/SscxStatistics.vue'
import ExtensionTest from '../views/ExtensionTest.vue'
import AbnormalOwnerDetailView from '../views/AbnormalOwnerDetailView.vue'
import AbnormalTaskDetail from '../views/AbnormalTaskDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '系统首页' }
  },
  {
    path: '/homepage',
    name: 'HomePage',
    component: HomePage,
    meta: { title: '项目管理' }
  },
  {
    path: '/project-detail',
    name: 'ProjectDetail',
    component: ProjectDetailView
  },
  {
    path: '/task-detail',
    name: 'TaskDetail',
    component: TaskDetailView
  },
  {
    path: '/project-subtasks/:projectId',
    name: 'ProjectSubtasksDetail',
    component: ProjectSubtasksDetailView,
    props: true
  },
  {
    path: '/owner-tasks/:owner',
    name: 'OwnerTaskDetail',
    component: OwnerTaskDetailView,
    props: true
  },
  {
    path: '/project-status-detail/:status?',
    name: 'ProjectStatusDetail',
    component: ProjectStatusDetailView,
    props: true
  },
  {
    path: '/project-manager-detail/:manager',
    name: 'ProjectManagerDetail',
    component: ProjectManagerDetailView,
    props: true
  },
  {
    path: '/owner-project-subtasks/:owner',
    name: 'OwnerProjectSubtasks',
    component: OwnerProjectSubtasksView,
    props: true
  },
  {
    path: '/milestone-task-detail',
    name: 'MilestoneTaskDetail',
    component: MilestoneTaskDetailView
  },
  {
    path: '/completed-milestone-task-detail',
    name: 'CompletedMilestoneTaskDetail',
    component: CompletedMilestoneTaskDetailView
  },
  {
    path: '/subtask-detail',
    name: 'SubTaskDetail',
    component: SubTaskDetailView
  },
  {
    path: '/accepted-task-detail',
    name: 'AcceptedTaskDetail',
    component: AcceptedTaskDetailView
  },
  {
    path: '/project-status-subtasks/:status',
    name: 'ProjectStatusSubtasksDetail',
    component: ProjectStatusSubtasksDetailView,
    props: true
  },
  {
    path: '/ncr-flow-chart',
    name: 'NcrFlowChart',
    component: NcrFlowChart
  },
  {
    path: '/ncr-stage-detail/:stage?',
    name: 'NcrStageDetail',
    component: NcrStageDetail,
    props: true
  },
  {
    path: '/ncr-item-detail/:processNo',
    name: 'NcrItemDetail',
    component: NcrItemDetail,
    props: true
  },
  {
    path: '/ncr-home',
    name: 'NcrHomePage',
    component: NcrHomePage
  },
  {
    path: '/ncr-dashboard',
    name: 'NcrDashboard',
    component: NcrDashboard
  },
  {
    path: '/ncr-enhanced',
    name: 'NcrEnhancedDashboard',
    component: NcrEnhancedDashboard,
    meta: { title: 'NCR管理' }
  },
  {
    path: '/extension-test',
    name: 'ExtensionTest',
    component: ExtensionTest
  },
  {
    path: '/sscx-statistics',
    name: 'SscxStatistics',
    component: SscxStatistics
  },
  {
    path: '/abnormal-owner-detail/:owner',
    name: 'AbnormalOwnerDetail',
    component: AbnormalOwnerDetailView,
    props: true
  },
  {
    path: '/abnormal-task-detail/:ownerName',
    name: 'AbnormalTaskDetail',
    component: AbnormalTaskDetail,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - 结构件事业部管理系统`
  } else {
    document.title = '结构件事业部管理系统'
  }
  next()
})

export default router