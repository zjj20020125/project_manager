import { createRouter, createWebHistory } from 'vue-router'
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

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router