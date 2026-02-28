<template>
  <el-container style="min-height: 100vh;">
    <!-- 固定的顶部导航 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; position: relative;">
        <div style="position: absolute; left: 30px;">
          <el-button @click="goBack" icon="ArrowLeft" size="large" style="font-size: 18px; padding: 12px;">
            返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            {{ title }}
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">{{ subtitle }}</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <!-- 项目信息卡片 -->
      <el-card shadow="hover" style="margin-bottom: 20px;" v-if="projectInfo && Object.keys(projectInfo).length > 0">
        <div slot="header" class="card-header">{{ projectTitle }}</div>
        <el-descriptions :column="3" border v-if="projectInfo && Object.keys(projectInfo).length > 0">
          <el-descriptions-item label="项目编号">{{ projectInfo.project_id }}</el-descriptions-item>
          <el-descriptions-item label="项目经理">{{ projectInfo.project_manager }}</el-descriptions-item>
          <el-descriptions-item label="项目状态">
            <el-tag :type="getStatusTagType(projectInfo.project_status)">
              {{ projectInfo.project_status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计划开始时间">{{ projectInfo.planned_start_date }}</el-descriptions-item>
          <el-descriptions-item label="计划结束时间">{{ projectInfo.planned_end_date }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ projectInfo.created_at }}</el-descriptions-item>
          <el-descriptions-item label="实际开始时间">{{ projectInfo.actual_start_date || '未开始' }}</el-descriptions-item>
          <el-descriptions-item label="实际结束时间">{{ projectInfo.actual_end_date || '未完成' }}</el-descriptions-item>
          <el-descriptions-item label="项目分类">
            <el-tag :type="getCategoryTagType(projectInfo.category)">
              {{ projectInfo.category }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div v-else style="text-align: center; padding: 20px;">
          未找到项目信息
        </div>
      </el-card>

      <!-- 项目任务甘特图 -->
      <el-card shadow="hover" style="margin-bottom: 20px;" v-if="showGantt">
        <div slot="header" class="card-header">{{ ganttTitle }}</div>
        <div ref="ganttRef" class="gantt-container" v-if="ganttData && ganttData.length > 0"></div>
        <div v-else style="text-align: center; padding: 50px; color: #999;">
          暂无任务数据可供显示
        </div>
      </el-card>

      <!-- 项目列表 -->
      <el-card shadow="hover">
        <div slot="header" class="card-header">{{ listTitle }}</div>
        <el-table 
          :data="listData" 
          border 
          style="width: 100%" 
          v-loading="loading"
          v-if="listData && listData.length > 0"
          fit="true"
          :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }"
          :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
        >
          <el-table-column v-for="column in tableColumns" 
                          :key="column.prop" 
                          :prop="column.prop" 
                          :label="column.label" 
                          :width="column.width" 
                          :min-width="column.minWidth"
                          :align="column.align || 'center'"
                          :header-align="column.headerAlign || 'center'">
            <template #default="scope" v-if="column.render">
              <span v-if="column.type === 'tag'">
                <el-tag :type="column.getTagType ? column.getTagType(scope.row[column.prop]) : 'info'">
                  {{ scope.row[column.prop] }}
                </el-tag>
              </span>
              <span v-else-if="column.type === 'progress'">
                <el-progress :percentage="Number(scope.row[column.prop]?.replace('%','') || 0)" size="small" />
              </span>
              <span v-else>
                {{ scope.row[column.prop] }}
              </span>
            </template>
          </el-table-column>
        </el-table>
        <div v-else style="text-align: center; padding: 50px; color: #999;">
          {{ emptyMessage }}
        </div>
        
        <!-- 分页组件 -->
        <el-pagination
          v-if="showPagination"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalItems"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; text-align: right;"
        />
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, defineProps, defineEmits } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElContainer, ElMain, ElCard, ElButton, ElTable, ElTableColumn, ElTag, ElProgress, ElDescriptions, ElDescriptionsItem, ElPagination, vLoading } from 'element-plus'
import { projectApi } from '@/api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()
const emit = defineEmits(['data-loaded'])

// 接收配置参数
const props = defineProps({
  title: {
    type: String,
    default: '项目详情'
  },
  subtitle: {
    type: String,
    default: '查看项目详细信息'
  },
  projectTitle: {
    type: String,
    default: '项目基本信息'
  },
  ganttTitle: {
    type: String,
    default: '项目任务进度甘特图'
  },
  listTitle: {
    type: String,
    default: '项目列表'
  },
  showGantt: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  tableColumns: {
    type: Array,
    default: () => []
  },
  emptyMessage: {
    type: String,
    default: '暂无数据'
  },
  apiFunction: {
    type: Function,
    required: true
  }
})

// 状态变量
const currentTime = ref('')
const loading = ref(false)
const listData = ref([])
const projectInfo = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

// 甘特图相关
const ganttData = ref([])
let ganttChart = null
const ganttRef = ref(null)

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
  router.go(-1)
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    // 调用传入的API函数
    const response = await props.apiFunction({
      page: currentPage.value,
      limit: pageSize.value
    })
    
    if (response) {
      if (Array.isArray(response)) {
        listData.value = response
        // 需要获取总数，这里假设API有获取总数的方法
        // 如果没有专门的总数API，我们暂时保留这种方式
        totalItems.value = response.length
      } else {
        // 处理可能的对象响应
        listData.value = response.data || response.items || []
        totalItems.value = response.total || response.count || response.length || listData.value.length
      }
    }
    
    emit('data-loaded', listData.value)
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取项目状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '未开始':
    case 'not_started':
      return 'warning'
    case '进行中':
    case 'in_progress':
      return 'primary'
    case '已完成':
    case 'completed':
      return 'success'
    case '已结项':
      return 'success'
    default:
      return 'info'
  }
}

// 获取分类标签类型
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

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchData()
}

// 初始化甘特图
const initGanttChart = async () => {
  if (!ganttRef.value || !ganttData.value || ganttData.value.length === 0) {
    return
  }

  if (ganttChart) {
    ganttChart.dispose()
  }

  ganttChart = echarts.init(ganttRef.value)
  
  // 准备甘特图数据
  const validTasks = []
  const taskNames = []
  
  ganttData.value.forEach((item, index) => {
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
      console.warn(`跳过没有日期信息的任务: ${item.task_name || item.project_name}`);
      return; // 跳过没有日期信息的任务
    }
    
    // 检查日期是否有效
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      console.warn(`无效的日期格式: ${item.task_name || item.project_name}, 开始: ${startDateStr}, 结束: ${endDateStr}`);
      return; // 跳过无效日期
    }
    
    // 确保结束日期不早于开始日期，如果不符合则交换
    if (endDate < startDate) {
      console.warn(`日期顺序错误，已调整: ${item.task_name || item.project_name}, 从 ${startDateStr} 到 ${endDateStr}`);
      [startDate, endDate] = [endDate, startDate]; // 交换日期
    }
    
    validTasks.push({
      index: index,
      taskName: item.task_name || item.project_name,
      projectName: item.project_name,
      startDate: startDate,
      endDate: endDate,
      duration: (endDate - startDate) / (1000 * 60 * 60 * 24),
    });
    
    taskNames.push(item.task_name || item.project_name);
  });
  
  if (validTasks.length === 0) {
    ganttChart.setOption({
      title: {
        text: '暂无甘特图数据',
        left: 'center',
        top: 'center'
      }
    })
    return
  }
  
  // 计算X轴范围
  const allDates = []
  validTasks.forEach(task => {
    allDates.push(task.startDate.getTime())
    allDates.push(task.endDate.getTime())
  })
  
  const minTime = Math.min(...allDates)
  const maxTime = Math.max(...allDates)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
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
      min: minTime,
      max: maxTime,
      axisLabel: { 
        formatter: (val) => {
          const date = new Date(val)
          return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        }
      }
    },
    yAxis: {
      type: 'category',
      data: taskNames,
      axisLabel: { interval: 0, fontSize: 10 },
      inverse: true
    },
    series: [{
      name: '任务时间范围',
      type: 'bar',
      data: validTasks.map(task => [task.startDate.getTime(), task.endDate.getTime()]),
      barWidth: 15,
      itemStyle: { color: '#409EFF' }
    }]
  }
  
  ganttChart.setOption(option)
}

// 在onMounted中初始化数据
onMounted(async () => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)
  
  // 获取数据
  await fetchData()
  
  // 如果需要显示甘特图，获取甘特图数据
  if (props.showGantt) {
    try {
      const ganttResponse = await projectApi.getTaskGanttData()
      ganttData.value = ganttResponse || []
      // 初始化甘特图
      await nextTick()
      initGanttChart()
    } catch (error) {
      console.error('获取甘特图数据失败:', error)
    }
  }
  
  window.addEventListener('resize', () => {
    if (ganttChart) {
      ganttChart.resize()
    }
  })
})

onUnmounted(() => {
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
  height: 400px;
}
</style>