<template>
  <el-container style="min-height: 100vh;">
    <!-- 顶部导航栏 -->
    <el-header style="background: #409EFF; padding: 0; color: white; display: flex; align-items: center;">
      <div style="max-width: 1200px; margin: 0 auto; width: 100%; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="position: absolute; left: 0;">
          <el-button @click="goBack" type="primary" plain style="margin-right: 20px;">
            <i class="el-icon-arrow-left"></i> 返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h2 style="margin: 0; font-size: 20px;">{{ projectName || '项目' }} - 子任务详情</h2>
        </div>
        <div style="color: white; font-size: 16px; position: absolute; right: 0;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </el-header>

    <el-main style="padding: 20px; display: flex; justify-content: center;">
      <div style="max-width: 1200px; width: 100%;">
        <!-- 项目信息卡片 -->
        <el-card shadow="hover" style="margin-bottom: 20px;" v-if="projectInfo && Object.keys(projectInfo).length > 0">
          <div slot="header" class="card-header">项目基本信息</div>
          <el-descriptions :column="3" border v-if="projectInfo && Object.keys(projectInfo).length > 0">
            <el-descriptions-item label="项目编号">{{ projectInfo.project_id || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="项目经理">{{ projectInfo.project_manager || '未指定' }}</el-descriptions-item>
            <el-descriptions-item label="项目状态">
              <el-tag :type="getStatusTagType(projectInfo.project_status)">
                {{ projectInfo.project_status || '未设定' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="计划开始时间">{{ projectInfo.planned_start_date || '未设定' }}</el-descriptions-item>
            <el-descriptions-item label="计划结束时间">{{ projectInfo.planned_end_date || '未设定' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ projectInfo.created_at || '未记录' }}</el-descriptions-item>
            <el-descriptions-item label="实际开始时间">{{ projectInfo.actual_start_date || '未开始' }}</el-descriptions-item>
            <el-descriptions-item label="实际结束时间">{{ projectInfo.actual_end_date || '未完成' }}</el-descriptions-item>
            <el-descriptions-item label="项目分类">
              <el-tag :type="getCategoryTagType(projectInfo.category)">
                {{ projectInfo.category || '未分类' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <div v-else style="text-align: center; padding: 20px;">
            未找到项目信息
          </div>
        </el-card>

       

        <!-- 项目子任务列表 -->
        <el-card shadow="hover">
          <div slot="header" class="card-header">{{ projectName || '项目' }} - 子任务列表</div>
          <el-table 
            :data="subtasksData" 
            border 
            style="width: 100%" 
            v-loading="loading"
            v-if="subtasksData && subtasksData.length > 0"
            fit="true"
            :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }"
            :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
          >
            <el-table-column prop="task_name" label="任务名称" min-width="200" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.task_name || scope.row.taskName || '未命名任务' }}
              </template>
            </el-table-column>
            <el-table-column prop="wbs_code" label="WBS编码" width="120" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.wbs_code || scope.row.wbsNo || 'N/A' }}
              </template>
            </el-table-column>
            <el-table-column prop="task_owner" label="任务负责人" width="120" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.task_owner || scope.row.owner || '未指定' }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_start_date" label="计划开始时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.planned_start_date || scope.row.planStart || '未设定' }}
              </template>
            </el-table-column>
            <el-table-column prop="planned_end_date" label="计划结束时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.planned_end_date || scope.row.planEnd || '未设定' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.actual_start_date || scope.row.actualStart || '未开始' }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center">
              <template #default="scope">
                {{ scope.row.actual_end_date || scope.row.actualEnd || '未完成' }}
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="任务进度" width="120" align="center" header-align="center">
              <template #default="scope">
                <el-progress :percentage="Number(scope.row.progress?.toString().replace('%','') || 0)" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="task_status" label="任务状态" width="120" align="center" header-align="center">
              <template #default="scope">
                <el-tag :type="getTaskStatusTagType(scope.row.task_status)">
                  {{ scope.row.task_status || scope.row.status || '未设定' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-else style="text-align: center; padding: 50px; color: #999;">
            暂无子任务数据
          </div>
        </el-card>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElContainer, ElHeader, ElMain, ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElProgress, ElDescriptions, ElDescriptionsItem, vLoading } from 'element-plus'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 状态变量
const projectName = ref('')
const projectId = ref('')
const currentTime = ref('')
const loading = ref(false)
const subtasksData = ref([])
const projectInfo = ref({})

// ECharts实例
let ganttChart = null
const ganttRef = ref(null)

// 在onMounted中初始化数据
onMounted(() => {
  // 从路由参数获取项目信息
  projectId.value = route.params.projectId
  projectName.value = route.query.projectName || '项目'
  
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)
  
  // 获取子任务数据
  fetchSubtasksData()
  
  window.addEventListener('resize', resizeCharts)
})

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

// 返回上一页
const goBack = () => {
  router.go(-1)  // 返回上一页
}

// 获取项目子任务数据
const fetchSubtasksData = async () => {
  loading.value = true
  try {
    console.log('正在获取项目ID:', projectId.value)
    console.log('正在获取项目名称:', route.query.projectName)
    
    // 使用项目标识符获取项目详细信息
    let projectIdentifier = null;
    
    // 优先使用路由参数中的项目ID，如果不存在则使用项目名称
    if (route.params.projectId) {
      projectIdentifier = route.params.projectId;
    } else if (route.query.projectName) {
      projectIdentifier = decodeURIComponent(route.query.projectName);
    }
    
    if (!projectIdentifier) {
      console.error('没有提供项目ID或项目名称');
      return;
    }
    
    // 获取项目详细信息
    const projectDetailResponse = await projectApi.getProjectsDetail()
    console.log('项目详细信息:', projectDetailResponse)
    
    let project = null;
    // 首先尝试根据项目ID查找
    if (projectId.value) {
      project = projectDetailResponse.find(p => String(p.project_id) === String(projectId.value));
    }
    
    // 如果通过ID未找到，尝试通过项目名称查找
    if (!project && route.query.projectName) {
      const queryProjectName = decodeURIComponent(route.query.projectName);
      project = projectDetailResponse.find(p => p.project_name === queryProjectName);
    }
    
    if (project) {
      projectInfo.value = project
      projectName.value = project.project_name
      document.title = `${projectName.value} - 子任务详情` // 更新页面标题
      console.log('找到项目信息:', project)
    } else {
      console.log('未找到项目，尝试使用第一个项目')
      // 如果找不到项目，使用第一个项目作为备选
      if (projectDetailResponse.length > 0) {
        const firstProject = projectDetailResponse[0]
        projectInfo.value = firstProject
        projectName.value = firstProject.project_name
        console.log('使用第一个项目信息:', firstProject)
      }
    }

    // 直接使用新API根据项目标识符获取子任务数据
    console.log('准备调用API，项目标识符:', projectIdentifier);
    try {
      const projectSubtasksResponse = await projectApi.getProjectSubtasks(projectIdentifier);
      console.log('项目子任务数据:', projectSubtasksResponse);
      
      // 标准化字段名，确保所有任务都有统一的字段结构
      const standardizedTasks = projectSubtasksResponse.map(task => {
        // 从任务对象中提取所有可能的字段名
        return {
          ...task,
          task_name: task.task_name || task.taskName || task.task_name || task.name || '未知任务',
          wbs_code: task.wbs_code || task.wbsNo || task.wbs_code || task.wbsCode || task.wbs_no || '',
          task_owner: task.task_owner || task.owner || task.task_owner || task.taskOwner || task.responsible || '未指定',
          planned_start_date: task.planned_start_date || task.planStart || task.planned_start_date || task.plan_start || task.plannedStart || '',
          planned_end_date: task.planned_end_date || task.planEnd || task.planned_end_date || task.plan_end || task.plannedEnd || '',
          actual_start_date: task.actual_start_date || task.actual_start_date || task.actualStart || task.actual_start || task['actual-start-time'] || '',
          actual_end_date: task.actual_end_date || task.actual_end_date || task.actualEnd || task.actual_end || task['actual-end-time'] || '',
          progress: (task.progress && typeof task.progress === 'string' && !task.progress.endsWith('%')) ? `${task.progress}%` : (task.progress || '0%'),
          task_status: task.task_status || task.status || task.task_status || task.taskStatus || task.Status || '未开始'
        };
      });
      
      console.log(`最终找到 ${standardizedTasks.length} 个任务属于项目 ${projectName.value}`);
      console.log('标准化后的任务数据:', standardizedTasks);
      subtasksData.value = standardizedTasks;
      
      // 初始化甘特图
      await initGanttChart();
    } catch (apiError) {
      console.error('API调用失败:', apiError);
      console.error('错误详情:', {
        message: apiError.message,
        response: apiError.response,
        request: apiError.request,
        config: apiError.config
      });
      
      // 显示用户友好的错误信息
      if (apiError.response) {
        console.error('HTTP错误状态:', apiError.response.status);
        console.error('HTTP错误数据:', apiError.response.data);
      }
      
      // 即使出错也要隐藏加载状态
      subtasksData.value = [];
    }
  } catch (error) {
    console.error('获取子任务数据失败:', error);
    console.error(error.stack);
    // 即使出错也要隐藏加载状态
    subtasksData.value = [];
  } finally {
    loading.value = false;
  }
}

// 初始化甘特图
const initGanttChart = async () => {
  if (!ganttRef.value || !subtasksData.value || subtasksData.value.length === 0) {
    console.log('甘特图不需要初始化：没有数据或DOM元素')
    return
  }
  
  // 销毁之前的图表实例
  if (ganttChart) {
    ganttChart.dispose()
  }
  
  // 确保DOM元素已经渲染
  await nextTick()
  
  ganttChart = echarts.init(ganttRef.value)
  
  // 准备甘特图数据 - 任务只要有开始或结束日期之一即可显示
  const filteredTasks = subtasksData.value.filter(task => 
    task.planned_start_date || task.planned_end_date
  )
  
  if (filteredTasks.length === 0) {
    ganttChart.setOption({
      title: {
        text: '暂无任务数据',
        left: 'center',
        top: 'center'
      }
    })
    return
  }
  
  const processedData = []
  const validTasks = []
  
  filteredTasks.forEach(task => {
    // 尝试多个可能的日期字段名
    const startDateStr = task.planned_start_date || task.planStart;
    const endDateStr = task.planned_end_date || task.planEnd;
    
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
      // 如果两个日期都无效，创建一个当前日期的点作为占位符
      const today = new Date();
      startDate = new Date(today);
      endDate = new Date(today);
      endDate.setDate(endDate.getDate() + 1); // 结束日期设为明天
      console.log('使用默认日期的任务', task.task_name || task.taskName || '未知任务');
    }
    
    // 检查日期是否有效
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      // 如果解析失败，使用当前日期
      const today = new Date();
      startDate = new Date(today);
      endDate = new Date(today);
      endDate.setDate(endDate.getDate() + 1);
      console.log('使用默认日期的任务（原日期无效）', task.task_name || task.taskName || '未知任务');
    }
    
    // 确保结束日期不早于开始日期，如果不符合则交换
    if (endDate < startDate) {
      console.log('日期顺序错误，已调整', task, startDateStr, endDateStr);
      [startDate, endDate] = [endDate, startDate]; // 交换日期
    }
    
    processedData.push({
      name: task.task_name || task.taskName || task.task_name || '未知任务',
      value: [startDate.getTime(), endDate.getTime()],
      itemStyle: {
        color: '#409EFF'
      }
    });
    validTasks.push(task);
  });
  
  if (processedData.length === 0) {
    ganttChart.setOption({
      title: {
        text: '没有有效数据可以显示',
        left: 'center',
        top: 'center'
      }
    })
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const task = validTasks[params.dataIndex]
        if (!task) return ''
        const taskName = task.task_name || task.taskName || task.task_name || '未知任务'
        const taskOwner = task.task_owner || task.owner || '未知负责人'
        const plannedStartDate = task.planned_start_date || task.planStart || '未知'
        const plannedEndDate = task.planned_end_date || task.planEnd || '未知'
        const actualStartDate = task.actual_start_date || task.actualStartTime || '未开始'
        const actualEndDate = task.actual_end_date || task.actualEndTime || '未完成'
        
        return `
          <div>任务：${taskName}</div>
          <div>负责人：${taskOwner}</div>
          <div>计划时间：${plannedStartDate} ~ ${plannedEndDate}</div>
          <div>实际时间：${actualStartDate} ~ ${actualEndDate}</div>
        `
      }
    },
    grid: { left: '15%', right: '8%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'time',
      min: Math.min(...processedData.map(d => d.value[0])),
      max: Math.max(...processedData.map(d => d.value[1])),
      axisLabel: { 
        formatter: (val) => {
          const date = new Date(val)
          return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        }
      }
    },
    yAxis: {
      type: 'category',
      data: validTasks.map(task => task.task_name || task.taskName || task.task_name || '未知任务'),
      axisLabel: { interval: 0, fontSize: 10 },
      inverse: true
    },
    series: [
      {
        name: '任务进度',
        type: 'bar',
        data: processedData,
        barWidth: 15,
        itemStyle: {
          color: '#409EFF',
          borderRadius: 4
        }
      }
    ]
  }
  
  ganttChart.setOption(option)
  
  // 为图表添加resize监听
  if (!ganttChart._resizeHandler) {
    ganttChart._resizeHandler = () => {
      ganttChart.resize()
    }
    window.addEventListener('resize', ganttChart._resizeHandler)
  }
}

// 获取任务状态标签类型
const getTaskStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
      return 'success'
    case '已验收':
      return 'primary'
    default:
      return 'info'
  }
}

// 获取项目状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
      return 'success'
    case '已验收':
      return 'primary'
    default:
      return 'info'
  }
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

// 监听窗口resize事件
const resizeCharts = () => {
  ganttChart?.resize()
}

// 确保使用nextTick

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  // 销毁图表实例
  if (ganttChart) {
    ganttChart.dispose()
  }
})
</script>

<style scoped>
.card-header {
  font-weight: 600;
  font-size: 14px;
  padding-bottom: 8px;
}
.gantt-container {
  width: 100%;
  height: 500px;
}
</style>