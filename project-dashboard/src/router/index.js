import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import HomePage from '../views/HomePage.vue'
import ProjectDetailView from '../views/ProjectDetailView.vue'
import TaskDetailView from '../views/TaskDetailView.vue'
import ProjectSubtasksDetailView from '../views/ProjectSubtasksDetailView.vue'
import OwnerTaskDetailView from '../views/OwnerTaskDetailView.vue'
import ProjectStatusDetailView from '../views/ProjectStatusDetailView.vue'
import ProjectManagerDetailView from '../views/ProjectManagerDetailView.vue'
import OwnerProjectSubtasksView from '../views/OwnerProjectSubtasksView.vue'
import MilestoneTaskDetailView from '../views/MilestoneTaskDetailView.vue'
import CompletedMilestoneTaskDetailView from '../views/CompletedMilestoneTaskDetailView.vue'
import SubTaskDetailView from '../views/SubTaskDetailView.vue'
import AcceptedTaskDetailView from '../views/AcceptedTaskDetailView.vue'
import ProjectStatusSubtasksDetailView from '../views/ProjectStatusSubtasksDetailView.vue'
import NcrFlowChart from '../views/ncr/NcrFlowChart.vue'
import NcrStageDetail from '../views/ncr/NcrStageDetail.vue'
import NcrItemDetail from '../views/ncr/NcrItemDetail.vue'
import NcrHomePage from '../views/ncr/NcrHomePage.vue'
import AbnormalOwnerDetailView from '../views/AbnormalOwnerDetailView.vue'
import AbnormalTaskDetail from '../views/AbnormalTaskDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/home',
    name: 'HomePage',
    component: HomePage
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

export default router