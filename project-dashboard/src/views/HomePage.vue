<template>
  <el-container style="min-height: 100vh; padding-top: 120px;">
    <!-- 项目总览标题栏 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);"> 
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="text-align: center;">
          <h1 v-if="currentView !== 'ncr'" style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">项目总览</h1>
          <h1 v-else style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">NCR管理</h1>
          <p v-if="currentView !== 'ncr'" style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">结构件事业部项目管理</p>
          <p v-else style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">NCR流程管理</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 0;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 顶部导航 -->
    <el-header style="background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; flex-shrink: 0; max-width: 1200px; margin: 0 auto; width: 100%;">
      <el-menu :default-active="activeMenu" mode="horizontal" background-color="#fff" text-color="#333" active-text-color="#409EFF" @select="handleMenuSelect">
        <el-menu-item index="1">项目总览</el-menu-item>
        <el-menu-item index="2">NCR管理</el-menu-item>
      </el-menu>
    </el-header>

    <el-main style="padding: 20px 0; display: flex; justify-content: center;">
      <div style="max-width: 1200px; width: 100%; padding: 0 20px;">
        <!-- 条件渲染：显示NCR管理界面或项目总览界面 -->
        <div v-if="currentView === 'ncr'">
          <el-card shadow="hover" margin-bottom="20px" style="margin-top: 20px;">
            <NcrFlowChart />
          </el-card>
        </div>
        <div v-else>
          <!-- 项目分类统计 -->
          <el-card shadow="hover" margin-bottom="20px" style="margin-top: 20px;">
            <div slot="header" class="card-header">项目分类统计</div>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('total')" class="clickable-card">
                  <div class="card-title">项目总数</div>
                  <div class="card-value" style="color: #f56c6c;">{{ projectCategoryStats.total_projects || 0 }}个</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('not_started')" class="clickable-card">
                  <div class="card-title">未开始项目</div>
                  <div class="card-value" style="color: #E6A23C;">{{ projectCategoryStats.not_started_projects || 0 }}个</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('ongoing')" class="clickable-card">
                  <div class="card-title">进行中项目</div>
                  <div class="card-value" style="color: #409EFF;">{{ projectCategoryStats.ongoing_projects || 0 }}个</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('completed')" class="clickable-card">
                  <div class="card-title">已结项项目</div>
                  <div class="card-value" style="color: #67C23A;">{{ projectCategoryStats.completed_projects || 0 }}个</div>
                </el-card>
              </el-col>
            </el-row>
          </el-card>

          <!-- 图表区域 -->
          <el-row :gutter="20" margin-bottom="20px">
            <!-- 项目状态分布（扇形图） -->
            <el-col :span="8">
              <el-card shadow="hover" class="clickable-card">
                <div slot="header" class="card-header">项目状态分布</div>
                <div ref="typePieRef" class="chart-container"></div>
              </el-card>
            </el-col>

            <!-- 任务负责人统计（表格形式） -->
            <el-col :span="8">
              <el-card shadow="hover">
                <div slot="header" class="card-header">任务负责人统计</div>
                <el-table 
                  :data="taskOwnerStats" 
                  border 
                  style="width: 100%" 
                  height="260"
                  :fit="true"
                  v-loading="ownerStatsLoading"
                >
                  <el-table-column prop="owner_name" label="负责人姓名" align="center" header-align="center">
                    <template #default="scope">
                      <span 
                        @click="goToOwnerTaskDetail(scope.row.owner_name)"
                        style="color: #409EFF; cursor: pointer; text-decoration: underline; display: block; width: 100%;"
                      >
                        {{ scope.row.owner_name }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="task_count" label="负责任务数" align="center" header-align="center">
                    <template #default="scope">
                      <el-tag type="success" style="text-align: center">{{ scope.row.task_count }} 项</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>

            <!-- 项目经理负载（横向柱状图） -->
            <el-col :span="8">
              <el-card shadow="hover" class="clickable-card">
                <div slot="header" class="card-header">项目经理负载</div>
                <div ref="loadBarRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 任务进度统计 -->
          <el-row :gutter="20" margin-bottom="20px">
            <el-col :span="6">
              <el-card shadow="hover" @click="goToMilestoneTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #74b9ff, #0984e3); color: white;">
                <div class="card-title" style="color: white;">里程碑任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.milestoneTasks }}个</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToCompletedMilestoneTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #00b894, #00a085); color: white;">
                <div class="card-title" style="color: white;">已验收里程碑任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.completedMilestones }}个</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToSubTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #fdcb6e, #e17055); color: white;">
                <div class="card-title" style="color: white;">子任务任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.subTasks }}个</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToAcceptedTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white;">
                <div class="card-title" style="color: white;">已验收任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.completedTasks }}个</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 项目任务甘特图 -->
          <el-card shadow="hover" margin-bottom="20px">
            <div slot="header" class="card-header">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ selectedProjectName || '项目任务甘特图' }}</span>
                <el-select v-model="selectedProjectId" placeholder="请选择项目" style="width: 200px;" @change="updateGanttChart">
                  <el-option
                    v-for="item in projectOptions"
                    :key="item.project_id"
                    :label="item.project_name"
                    :value="item.project_id"
                  >
                  </el-option>
                </el-select>
              </div>
            </div>
            <div ref="ganttRef" class="gantt-container"></div>
            <button @click="debugGanttData" style="margin-top: 10px;">调试甘特图数据</button>
          </el-card>

          <!-- 任务进度明细表 -->
          <el-card shadow="hover">
            <div slot="header" class="card-header">项目进度明细表</div>
            <el-table :data="projectDetails" border style="width: 100%" v-loading="projectDetailsLoading" header-align="center">
              <el-table-column prop="project_id" label="项目编号" width="100" align="center" header-align="center" />
              <el-table-column 
                prop="project_name" 
                label="项目名称" 
                min-width="200"
                align="center"
                header-align="center"
              >
                <template #default="scope">
                  <span 
                    @click="goToProjectSubtasks(scope.row.project_id, scope.row.project_name)"
                    style="color: #409EFF; cursor: pointer; text-decoration: underline;"
                  >
                    {{ scope.row.project_name }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="project_manager" label="项目经理" width="120" align="center" header-align="center" />
              <el-table-column prop="planned_start_date" label="计划开始时间" width="150" align="center" header-align="center" />
              <el-table-column prop="planned_end_date" label="计划结束时间" width="150" align="center" header-align="center" />
              <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center" />
              <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
              <el-table-column prop="project_status" label="项目状态" width="120" align="center" header-align="center" />
              <el-table-column prop="category" label="项目分类" width="120" align="center" header-align="center">
                <template #default="scope">
                  <el-tag :type="getCategoryTagType(scope.row.category)">
                    {{ scope.row.category }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" align="center" header-align="center" />
            </el-table>
          </el-card>
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import * as echarts from 'echarts'
import { ElContainer, ElHeader, ElMain, ElRow, ElCol, ElCard, ElMenu, ElMenuItem, ElTable, ElTableColumn, ElTag, ElProgress, ElMessage, vLoading } from 'element-plus'
import { useRouter } from 'vue-router'
import { projectApi } from '../api/index.js'  // 导入API
import NcrFlowChart from './ncr/NcrFlowChart.vue'
import 'element-plus/dist/index.css'

const router = useRouter()

// 当前显示的视图 ('project' 或 'ncr')
const currentView = ref('project')

// 当前时间状态
const currentTime = ref('')

// 更新当前时间
const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 导航激活项
const activeMenu = ref('1')

// 加载状态
const tableLoading = ref(false)

// 数据状态
const projectStats = reactive({
  totalProjects: 0,
  notStartedProjects: 0,
  runningProjects: 0,
  completedProjects: 0
})

const taskStats = reactive({
  milestoneTasks: 0,
  completedMilestones: 0,
  subTasks: 0,
  completedTasks: 0
})

// 项目详细数据状态
const projectDetails = ref([])
const projectDetailsLoading = ref(false)
const projectCategoryStats = ref({
  total_projects: 0,
  not_started_projects: 0,
  ongoing_projects: 0,
  completed_projects: 0
})

// 任务表格数据
const taskTableData = ref([])

// 任务负责人统计相关
const taskOwnerStats = ref([])
const ownerStatsLoading = ref(false)

// 项目选择相关
const selectedProjectId = ref('')
const selectedProjectName = ref('项目任务甘特图')
const projectOptions = ref([])

// 任务状态对应的标签类型
const statusTagType = {
  '未开始': 'warning',
  '进行中': 'info',
  '已完成': 'success',
  '已验收': 'primary',
  '已验收': 'primary'
}

// ECharts实例引用
const typePieRef = ref(null)
const sourceBarRef = ref(null)
const loadBarRef = ref(null)
const ganttRef = ref(null)

// 图表实例对象
let typePieChart = null
let sourceBarChart = null
let loadBarChart = null
let ganttChart = null

// 获取统计数据
const fetchStats = async () => {
  try {
    // 获取项目统计数据
    const statsRes = await projectApi.getProjectStats();
    if (statsRes) {
      projectStats.totalProjects = statsRes.total_projects || 0;
      projectStats.notStartedProjects = statsRes.unstarted_projects || 0;
      projectStats.runningProjects = statsRes.ongoing_projects || 0;
      projectStats.completedProjects = statsRes.completed_projects || 0;
    }
    
    // 获取任务统计数据
    const taskStatsRes = await projectApi.getTaskStats();
    if (taskStatsRes) {
      taskStats.milestoneTasks = taskStatsRes.total_milestones || 0;
      taskStats.completedMilestones = taskStatsRes.completed_milestones || 0;
      taskStats.subTasks = taskStatsRes.total_subtasks || 0;
      taskStats.completedTasks = taskStatsRes.completed_tasks || 0;
    }
    
    // 获取任务表格数据
    const taskListRes = await projectApi.getTaskList({ page: 1, limit: 10 });
    taskTableData.value = taskListRes?.data || [];
  } catch (error) {
    console.error('获取统计数据失败:', error);
    ElMessage.error('获取统计数据失败');
  }
}

// 获取项目分类统计数据
const fetchProjectCategoryStats = async () => {
  try {
    const statsRes = await projectApi.getProjectCategoryStats()
    if (statsRes) {
      projectCategoryStats.value = statsRes
    }
  } catch (error) {
    console.error('获取项目分类统计数据失败:', error)
    ElMessage.error('获取项目分类统计数据失败')
  }
}

// 获取项目详细分类数据
const fetchProjectDetails = async () => {
  projectDetailsLoading.value = true
  try {
    const detailRes = await projectApi.getProjectsDetail()
    if (detailRes) {
      projectDetails.value = detailRes
    }
  } catch (error) {
    console.error('获取项目详细分类数据失败:', error)
    ElMessage.error('获取项目详细分类数据失败')
  } finally {
    projectDetailsLoading.value = false
  }
}

// 获取项目列表
const fetchProjectsList = async () => {
  try {
    const response = await projectApi.getProjectsList()
    if (response) {
      projectOptions.value = response
      // 如果有项目，默认选中第一个项目
      if (response.length > 0) {
        selectedProjectId.value = response[0].project_id
        selectedProjectName.value = `${response[0].project_name} - 任务甘特图`
        // 更新甘特图以显示第一个项目的数据
        setTimeout(() => {
          initGantt()
        }, 100)
      }
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 更新甘特图
const updateGanttChart = async () => {
  // 根据选中的项目更新标题
  if (selectedProjectId.value) {
    const selectedProject = projectOptions.value.find(p => p.project_id === selectedProjectId.value)
    if (selectedProject) {
      selectedProjectName.value = `${selectedProject.project_name} - 任务甘特图`
    }
  } else {
    selectedProjectName.value = '项目任务甘特图'
  }
  
  // 重新初始化甘特图
  await initGantt()
}

// 获取项目分类标签类型
const getCategoryTagType = (category) => {
  switch (category) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已结项':
      return 'success'
    default:
      return 'info'
  }
}

// 跳转到项目详情页面
const goToProjectDetail = (status) => {
  // 使用路由跳转到项目详情页面
  router.push({ name: 'ProjectDetail', query: { status: status } })
}

// 跳转到任务详情页面
const goToTaskDetail = (taskType) => {
  // 使用路由跳转到任务详情页面
  router.push({ name: 'TaskDetail', query: { type: taskType } })
}

// 跳转到项目子任务详情页面
const goToProjectSubtasks = (projectId, projectName) => {
  // 使用路由跳转到项目子任务详情页面
  router.push({ 
    name: 'ProjectSubtasksDetail', 
    params: { projectId: projectId },
    query: { projectName: encodeURIComponent(projectName || '') }
  })
}

// 跳转到负责人项目子任务详情页面
const goToOwnerTaskDetail = (ownerName) => {
  // 使用路由跳转到负责人项目子任务详情页面
  router.push({ 
    name: 'OwnerProjectSubtasks', 
    params: { owner: encodeURIComponent(ownerName || '') }
  })
}

// 跳转到项目状态详情页面
const goToProjectStatusDetail = (status = null) => {
  // 使用路由跳转到项目状态详情页面，传递状态参数
  const routeParams = {
    name: 'ProjectStatusDetail'
  };
  
  if (status) {
    routeParams.params = { status: status };
  }
  
  router.push(routeParams);
}

// 跳转到项目状态的子任务详情页面
const goToProjectStatusSubtasks = (status) => {
  // 使用路由跳转到项目状态的子任务详情页面，传递状态参数
  router.push({ 
    name: 'ProjectStatusSubtasksDetail', 
    params: { status: status }
  })
}

// 跳转到项目经理详情页面
const goToProjectManagerDetail = (managerName) => {
  // 使用路由跳转到项目经理详情页面
  router.push({ 
    name: 'ProjectManagerDetail', 
    params: { manager: encodeURIComponent(managerName || '') }
  })
}

// 跳转到里程碑任务详情页面
const goToMilestoneTaskDetail = () => {
  // 使用路由跳转到里程碑任务详情页面
  router.push({ name: 'MilestoneTaskDetail' })
}

// 跳转到已验收里程碑任务详情页面
const goToCompletedMilestoneTaskDetail = () => {
  // 使用路由跳转到已验收里程碑任务详情页面
  router.push({ name: 'CompletedMilestoneTaskDetail' })
}

// 跳转到子任务详情页面
const goToSubTaskDetail = () => {
  // 使用路由跳转到子任务详情页面
  router.push({ name: 'SubTaskDetail' })
}

// 跳转到已验收任务详情页面
const goToAcceptedTaskDetail = () => {
  // 使用路由跳转到已验收任务详情页面
  router.push({ name: 'AcceptedTaskDetail' })
}

// 切换到NCR管理页面
const goToNcr = () => {
  currentView.value = 'ncr';
  activeMenu.value = '2';
}

// 导航到NCR流程图
const goToNcrFlowChart = () => {
  window.location.reload();
}

// 重新初始化图表
const reInitCharts = () => {
  setTimeout(() => {
    initTypePie();
    initSourceBar();
    initLoadBar();
    initGantt();
  }, 100);
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  if (index === '2') {
    currentView.value = 'ncr';
    activeMenu.value = '2';
  } else {
    currentView.value = 'project';
    activeMenu.value = '1';
    // 重新初始化图表以确保它们正确显示
    reInitCharts();
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'total':
      return '全部';
    case 'not_started':
      return '未开始';
    case 'ongoing':
      return '进行中';
    case 'completed':
      return '已结项';
    default:
      return '';
  }
}

// 调试甘特图数据
const debugGanttData = async () => {
  try {
    const projectName = selectedProjectId.value ? 
      projectOptions.value.find(p => p.project_id === selectedProjectId.value)?.project_name : null;
    
    const ganttData = await projectApi.getTaskGanttData(projectName);
    console.log('甘特图原始数据:', ganttData);
    
    // 检查是否有有效的日期数据
    if (ganttData && ganttData.length > 0) {
      ganttData.forEach((item, index) => {
        console.log(`任务 ${index + 1}:`, {
          task_name: item.task_name,
          project_name: item.project_name,
          planned_start_date: item.planned_start_date,
          planned_end_date: item.planned_end_date,
          start_valid: Boolean(item.planned_start_date),
          end_valid: Boolean(item.planned_end_date)
        });
      });
    } else {
      console.log('没有获取到甘特图数据');
    }
  } catch (error) {
    console.error('调试甘特图数据失败:', error);
  }
}

// 监听窗口 resize，自适应图表
const resizeCharts = () => {
  typePieChart?.resize()
  sourceBarChart?.resize()
  loadBarChart?.resize()
  ganttChart?.resize()
}

// 挂载时初始化图表
onMounted(async () => {
  // 更新当前时间
  updateTime();
  // 每秒更新一次时间
  setInterval(updateTime, 1000);
  
  try {
    // 并行获取所有数据
    await Promise.all([
      fetchStats(),
      fetchProjectCategoryStats(),
      fetchProjectDetails(),
      fetchProjectsList(),
      initTaskOwnerStats()  // 添加任务负责人统计初始化
    ]);
    
    // 使用setTimeout确保DOM完全渲染后再初始化图表
    setTimeout(() => {
      initTypePie();
      initSourceBar();
      initLoadBar();
      initGantt();
    }, 100);
  } catch (error) {
    console.error('初始化页面数据失败:', error);
    ElMessage.error('页面初始化失败，请刷新重试');
  }
  
  window.addEventListener('resize', resizeCharts)
})

// 卸载时销毁图表
onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (typePieChart) {
    typePieChart.dispose()
    typePieChart = null
  }
  if (sourceBarChart) {
    sourceBarChart.dispose()
    sourceBarChart = null
  }
  if (loadBarChart) {
    loadBarChart.dispose()
    loadBarChart = null
  }
  if (ganttChart) {
    // 移除resize监听器
    if (ganttChart._resizeHandler) {
      window.removeEventListener('resize', ganttChart._resizeHandler);
      ganttChart._resizeHandler = null;
    }
    ganttChart.dispose()
    ganttChart = null
  }
})

// 初始化项目类型饼图
const initTypePie = async () => {
  try {
    // 获取项目状态分布数据
    const pieData = await projectApi.getProjectStatusStats();
    
    // 销毁之前的图表实例（如果存在）
    if (typePieChart) {
      typePieChart.dispose();
      typePieChart = null;
    }
    
    // 确保DOM元素存在
    if (!typePieRef.value) {
      console.error('Type pie chart container not found');
      return;
    }
    
    typePieChart = echarts.init(typePieRef.value)
    
    // 根据状态名称设置颜色
    const getColorForStatus = (statusName) => {
      if (statusName.includes('异常')) {
        return '#f56c6c'; // 红色
      } else if (statusName.includes('延期完成')) {
        return '#e6a23c'; // 黄色
      } else if (statusName.includes('完成')) {
        return '#67c23a'; // 绿色
      } else if (statusName.includes('延期')) {
        return '#e6a23c'; // 黄色
      } else {
        return '#409eff'; // 默认蓝色
      }
    };
    
    // 为数据项添加颜色
    const coloredPieData = pieData.map(item => ({
      ...item,
      itemStyle: {
        color: getColorForStatus(item.name)
      }
    }));
    
    const option = {
      tooltip: { trigger: 'item' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%' },
      legend: {
        bottom: 10,
        left: 'center',
        itemWidth: 12,
        itemHeight: 12
      },
      series: [
        {
          name: '项目状态',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '40%'],
          data: coloredPieData,
          label: { show: false },
          labelLine: { show: false },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    typePieChart.setOption(option)
    
    // 添加点击事件监听
    typePieChart.on('click', function(params) {
      console.log('扇形图点击事件:', params)
      // 根据点击的扇形图部分传递相应的状态参数
      // 从测试结果我们知道数据库中的实际状态值
      let status = params.name; // 直接使用扇形图显示的名称
      console.log('传递的状态参数:', status)
      goToProjectStatusSubtasks(status);
    });
  } catch (error) {
    console.error('初始化项目类型饼图失败:', error);
  }
}

// 初始化项目来源柱状图
const initSourceBar = async () => {
  try {
    // 确保DOM元素存在
    if (!sourceBarRef.value) {
      console.error('Source bar chart container not found');
      return;
    }

    // 销毁之前的图表实例（如果存在）
    if (sourceBarChart) {
      sourceBarChart.dispose();
      sourceBarChart = null;
    }

    // 获取图表数据
    const chartData = await projectApi.getChartData();
    const barData = chartData.source_bar || [];
    
    // 解析数据
    const categories = barData.map(item => item.name);
    const values = barData.map(item => item.value);
    
    sourceBarChart = echarts.init(sourceBarRef.value)
    const option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '15%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: categories
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '项目数量',
          type: 'bar',
          data: values,
          barWidth: '40%',
          itemStyle: { color: '#409EFF' }
        }
      ]
    }
    sourceBarChart.setOption(option)
  } catch (error) {
    console.error('初始化项目来源柱状图失败:', error);
  }
}

// 获取项目经理负载图
const initLoadBar = async () => {
  try {
    // 获取图表数据
    const chartData = await projectApi.getChartData();
    const barData = chartData.load_bar || [];
    
    // 解析数据
    const managers = barData.map(item => item.name);
    const loads = barData.map(item => item.value);
    
    // 为每个经理定义不同的颜色
    const managerColors = [
      '#3498db', // 蓝色
      '#2ecc71', // 绿色
      '#e74c3c', // 红色
      '#9b59b6', // 紫色
      '#f1c40f', // 黄色
      '#1abc9c', // 青色
      '#d35400', // 橙色
      '#34495e', // 深灰
      '#7f8c8d', // 灰色
      '#e67e22', // 橙红
    ];
    
    // 为每个经理分配颜色
    const coloredLoads = loads.map((value, index) => ({
      value: value,
      itemStyle: {
        color: managerColors[index % managerColors.length]
      }
    }));
    
    // 销毁之前的图表实例（如果存在）
    if (loadBarChart) {
      loadBarChart.dispose();
      loadBarChart = null;
    }
    
    // 确保DOM元素存在
    if (!loadBarRef.value) {
      console.error('Load bar chart container not found');
      return;
    }
    
    loadBarChart = echarts.init(loadBarRef.value)
    const option = {
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const managerName = params[0].name;
          return `${managerName}<br/>负责任务数: ${params[0].value}`;
        }
      },
      grid: { left: '15%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: managers
      },
      series: [
        {
          name: '负载数',
          type: 'bar',
          data: coloredLoads,
          barWidth: '40%'
        }
      ]
    }
    loadBarChart.setOption(option)
    
    // 添加点击事件监听
    loadBarChart.on('click', function(params) {
      console.log('项目经理负载图点击事件:', params)
      // 跳转到项目经理详情页面
      goToProjectManagerDetail(params.name);
    });
  } catch (error) {
    console.error('初始化项目经理负载图失败:', error);
  }
}

// 初始化任务负责人统计表格
const initTaskOwnerStats = async () => {
  ownerStatsLoading.value = true;
  try {
    const stats = await projectApi.getTaskOwnerStats();
    taskOwnerStats.value = stats;
  } catch (error) {
    console.error('获取任务负责人统计失败:', error);
    ElMessage.error('获取任务负责人统计失败');
  } finally {
    ownerStatsLoading.value = false;
  }
}

// 初始化甘特图
const initGantt = async () => {
  try {
    // 获取任务进度甘特图数据
    const projectName = selectedProjectId.value ? 
      projectOptions.value.find(p => p.project_id === selectedProjectId.value)?.project_name : null;
    
    // 等待API数据获取完成
    const ganttData = await projectApi.getTaskGanttData(projectName);
    
    // 确保DOM元素存在
    if (!ganttRef.value) {
      console.error('Gantt chart container not found');
      return;
    }
    
    // 销毁之前的图表实例（如果存在）
    if (ganttChart) {
      // 移除resize监听器
      if (ganttChart._resizeHandler) {
        window.removeEventListener('resize', ganttChart._resizeHandler);
        ganttChart._resizeHandler = null;
      }
      ganttChart.dispose();
      ganttChart = null;
    }
    
    ganttChart = echarts.init(ganttRef.value);
    
    // 如果没有数据，显示空图表
    if (!ganttData || ganttData.length === 0) {
      ganttChart.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center'
        }
      });
      return;
    }
    
    console.log('原始甘特图数据:', ganttData); // 调试信息
    
    // 准备数据 - 按照甘特图需求格式化数据
    const validTasks = [];
    
    ganttData.forEach((item, index) => {
      const startDateStr = item.planned_start_date;
      const endDateStr = item.planned_end_date;
      
      // 尝试解析日期字符串
      let startDate, endDate;
      
      if (startDateStr) {
        startDate = new Date(startDateStr);
      }
      if (endDateStr) {
        endDate = new Date(endDateStr);
      }
      
      // 如果其中一个日期为空或无效，尝试用另一个日期代替
      if (!startDate && endDate) {
        startDate = endDate;
      } else if (startDate && !endDate) {
        endDate = startDate;
      } else if (!startDate && !endDate) {
        // 即使没有日期信息，也要添加任务到列表中，但不显示时间区间
        console.info(`任务没有日期信息，将在甘特图中占位: ${item.task_name}`);
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false, // 标记为没有有效日期
          startDate: null,
          endDate: null,
          duration: 0
        });
        return; // 继续下一个任务
      }
      
      // 检查日期是否有效
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        console.warn(`无效的日期格式: ${item.task_name}, 开始: ${startDateStr}, 结束: ${endDateStr}`);
        // 即使日期无效，也要添加任务到列表中，但不显示时间区间
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false, // 标记为没有有效日期
          startDate: null,
          endDate: null,
          duration: 0
        });
        return; // 继续下一个任务
      }
      
      // 确保结束日期不早于开始日期，如果不符合则交换
      if (endDate < startDate) {
        console.warn(`日期顺序错误，已调整: ${item.task_name}, 从 ${startDateStr} 到 ${endDateStr}`);
        [startDate, endDate] = [endDate, startDate]; // 交换日期
      }
      
      validTasks.push({
        index: index,
        taskName: item.task_name,
        projectName: item.project_name,
        hasValidDates: true, // 标记为有有效日期
        startDate: startDate,
        endDate: endDate,
        duration: (endDate - startDate) / (1000 * 60 * 60 * 24), // 以天为单位
      });
    });
    
    console.log('处理后的有效任务:', validTasks); // 调试信息
    
    // 如果处理后的数据为空，显示提示
    if (validTasks.length === 0) {
      ganttChart.setOption({
        title: {
          text: '没有有效数据可以显示',
          left: 'center',
          top: 'center'
        }
      });
      return;
    }
    
    // 为每个任务计算起始和结束时间的数值（用于ECharts显示）
    const taskNames = validTasks.map(task => task.taskName);
    
    // 计算X轴范围，使用最早开始时间和最晚结束时间（仅针对有有效日期的任务）
    const validTasksWithDates = validTasks.filter(task => task.hasValidDates);
    
    let earliestStartDate, latestEndDate;
    
    if (validTasksWithDates.length > 0) {
      earliestStartDate = new Date(Math.min(...validTasksWithDates.map(task => task.startDate.getTime())));
      latestEndDate = new Date(Math.max(...validTasksWithDates.map(task => task.endDate.getTime())));
    } else {
      // 如果没有任务有有效日期，使用当前日期范围
      earliestStartDate = new Date();
      latestEndDate = new Date();
      earliestStartDate.setDate(earliestStartDate.getDate() - 7); // 一周前
      latestEndDate.setDate(latestEndDate.getDate() + 7); // 一周后
    }
    
    // 设置X轴的最小值为最早开始时间，最大值为最晚结束时间
    const adjustedMinTime = earliestStartDate.getTime();
    const adjustedMaxTime = latestEndDate.getTime();
    
    // 添加边距（比如增加10%的时间范围）
    const timeRange = adjustedMaxTime - adjustedMinTime;
    const marginTime = timeRange * 0.1; // 10%的边距
    
    const finalMinTime = adjustedMinTime - marginTime;
    const finalMaxTime = adjustedMaxTime + marginTime;
    
    // 额外的调试信息：显示最早开始时间和最晚结束时间
    console.log('最早开始时间:', earliestStartDate);
    console.log('最晚结束时间:', latestEndDate);
    console.log('X轴范围设置为:', {
      min: new Date(finalMinTime),
      max: new Date(finalMaxTime)
    });
    
    // 检查是否所有日期都在同一年内
    const allDatesInSameYear = earliestStartDate.getFullYear() === latestEndDate.getFullYear();
    console.log('所有日期是否在同一年:', allDatesInSameYear);
    
    // 构建图表选项 - 使用时间轴来精确表示任务时间范围
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: function(params) {
          const task = validTasks[params.dataIndex];
          if (task) {
            return `
              <div>项目：${task.projectName}</div>
              <div>任务：${task.taskName}</div>
              <div>开始时间：${task.startDate.toLocaleDateString()}</div>
              <div>结束时间：${task.endDate.toLocaleDateString()}</div>
              <div>持续时间：${Math.round(task.duration)} 天</div>
            `;
          }
          return '';
        }
      },
      grid: { 
        left: '15%', 
        right: '8%', 
        bottom: '15%', 
        top: '10%',
        containLabel: true 
      },
      xAxis: {
        type: 'time',
        min: finalMinTime,
        max: finalMaxTime,
        axisLabel: { 
          formatter: (val) => {
            const date = new Date(val);
            const year = date.getFullYear();
            const month = String(date.getMonth()+1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            if (allDatesInSameYear) {
              // 如果所有日期都在同一年，只显示月日
              return `${month}-${day}`;
            } else {
              // 如果跨越多个年份，显示年月日
              return `${year}-${month}-${day}`;
            }
          }
        },
        splitLine: { show: true }
      },
      yAxis: {
        type: 'category',
        data: taskNames, // 根据规范，只显示任务名称
        axisLabel: { 
          interval: 0, 
          fontSize: 12 // 适当增大字体大小以提高可读性
        },
        inverse: true,  // 反转Y轴，使最新的任务在上方
        splitLine: { show: true }
      },
      series: [{
        name: '任务时间范围',
        type: 'custom',
        renderItem: function(params, api) {
          const task = validTasks[params.dataIndex];
          if (!task) return;
          
          // 如果任务没有有效日期，则只显示一个点而不显示时间区间
          if (!task.hasValidDates || !task.startDate || !task.endDate) {
            // 获取y轴坐标
            const y = api.coord([0, params.dataIndex])[1];
            const height = api.size([0, 1])[1] * 0.6;
            
            // 返回一个小矩形作为占位符
            return {
              type: 'rect',
              shape: {
                x: api.coord([Date.now(), params.dataIndex])[0], // 使用当前时间作为占位
                y: y - height / 2,
                width: 1, // 很窄的矩形
                height: height
              },
              style: api.style({
                fill: '#cccccc' // 灰色表示无日期信息
              })
            };
          }
          
          // 获取开始和结束时间的x坐标
          const xStart = api.coord([task.startDate.getTime(), params.dataIndex])[0];
          const xEnd = api.coord([task.endDate.getTime(), params.dataIndex])[0];
          
          // 获取y轴坐标
          const y = api.coord([0, params.dataIndex])[1];
          const height = api.size([0, 1])[1] * 0.6;
          
          const width = xEnd - xStart;
          
          return {
            type: 'rect',
            shape: {
              x: xStart,
              y: y - height / 2,
              width: width,
              height: height
            },
            style: api.style({
              fill: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#409EFF' },
                { offset: 1, color: '#1E88E5' }
              ])
            })
          };
        },
        data: validTasks.map(task => task.hasValidDates ? 1 : 0) // 有日期的用1，没有日期的用0作为占位
      }]
    };
    
    ganttChart.setOption(option);
    
    // 为图表添加resize监听
    if (!ganttChart._resizeHandler) {
      ganttChart._resizeHandler = () => {
        ganttChart.resize();
      };
      window.addEventListener('resize', ganttChart._resizeHandler);
    }
    
    console.log('甘特图已渲染完成');
  } catch (error) {
    console.error('初始化甘特图失败:', error);
    
    // 如果有图表实例，显示错误信息
    if (ganttChart) {
      ganttChart.setOption({
        title: {
          text: '图表加载失败',
          left: 'center',
          top: 'center'
        }
      });
    }
  }
};
</script>

<style scoped>
.card-header {
  font-weight: 600;
  font-size: 14px;
  padding-bottom: 8px;
}
.card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}
.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}
.chart-container {
  width: 100%;
  height: 260px; /* 增加高度以避免重叠 */
}
.gantt-container {
  width: 100%;
  height: 600px;
  min-height: 400px; /* 确保最小高度 */
  overflow: auto; /* 添加滚动条以防内容超出 */
}
/* 添加媒体查询以适配不同屏幕尺寸 */
@media (max-width: 768px) {
  .gantt-container {
    height: 400px; /* 在小屏幕上降低高度 */
    min-height: 300px;
  }
}
@media (max-width: 480px) {
  .gantt-container {
    height: 300px; /* 在更小的屏幕上进一步降低高度 */
    min-height: 250px;
  }
}
/* 添加可点击卡片样式 */
.clickable-card {
  cursor: pointer;
  transition: all 0.3s ease;
}
.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
/* 任务负责人统计表格样式 */
.el-table .el-table__cell {
  text-align: center;
  vertical-align: middle;
  display: table-cell;
}
.el-table .cell {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 100%;
}
.el-table td {
  padding: 0;
  height: 40px;
}
.el-table th {
  padding: 8px 0;
  height: 40px;
}
.el-table--border, .el-table--group {
  border: 1px solid #dfe2e6;
}
.el-table--border::after, .el-table--group::after, .el-table::before {
  background-color: #dfe2e6;
}
.el-table__body-wrapper, .el-table__header-wrapper {
  overflow: hidden;
}
.el-table {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>