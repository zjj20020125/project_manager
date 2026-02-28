
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
      <!-- 统计卡片区域 -->
      <div class="stats-cards" v-if="showStatsCards">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ stats.totalTasks }}</div>
            <div class="stat-label">{{ totalTasksLabel }}</div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number" :style="{ color: '#67C23A' }">{{ stats.completedTasks }}</div>
            <div class="stat-label">{{ completedTasksLabel }}</div>
          </div>
        </el-card>
        
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number" :style="{ color: '#E6A23C' }">{{ stats.pendingTasks }}</div>
            <div class="stat-label">{{ pendingTasksLabel }}</div>
          </div>
        </el-card>
      </div>

      <!-- 任务列表 -->
      <el-card class="task-list-card">
        <template #header>
          <div class="card-header">
            <span>{{ listTitle }}</span>
            <div class="filter-section" v-if="showFilters">
              <el-select 
                v-model="statusFilter" 
                :placeholder="statusPlaceholder" 
                style="width: 150px; margin-right: 10px;"
                @change="fetchTasks"
              >
                <el-option label="全部" value=""></el-option>
                <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value"></el-option>
              </el-select>
              <el-input 
                v-model="searchKeyword" 
                :placeholder="searchPlaceholder" 
                style="width: 200px;"
                @input="handleSearch"
              ></el-input>
            </div>
          </div>
        </template>

        <el-table 
          :data="filteredTasks" 
          v-loading="loading"
          style="width: 100%"
          stripe
          border
          :height="tableHeight"
        >
          <el-table-column prop="taskName" label="任务名称" min-width="200">
            <template #default="scope">
              <span class="task-name">{{ scope.row.taskName }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="projectName" label="所属项目" width="150">
            <template #default="scope">
              <span class="project-name">{{ scope.row.projectName }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="wbsNo" label="WBS编码" width="100">
            <template #default="scope">
              <el-tag type="info">{{ scope.row.wbsNo }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="owner" label="负责人" width="120">
            <template #default="scope">
              <span class="owner-name">{{ scope.row.owner }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="taskType" label="任务类型" width="100" v-if="showTaskType">
            <template #default="scope">
              <el-tag :type="scope.row.taskType === '里程碑' ? 'warning' : 'info'">{{ scope.row.taskType }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="planStart" label="计划开始" width="120">
            <template #default="scope">
              <span>{{ formatDate(scope.row.planStart) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="planEnd" label="计划结束" width="120">
            <template #default="scope">
              <span>{{ formatDate(scope.row.planEnd) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="actualStart" label="实际开始" width="120">
            <template #default="scope">
              <span>{{ formatDate(scope.row.actual_start_date) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="actualEnd" label="实际结束" width="120">
            <template #default="scope">
              <span>{{ formatDate(scope.row.actual_end_date) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="progress" label="进度" width="100">
            <template #default="scope">
              <el-progress 
                :percentage="parseFloat(scope.row.progress)" 
                :color="getProgressColor(parseFloat(scope.row.progress))"
                :stroke-width="10"
              />
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-section" v-if="showPagination">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalTasks"
          >
          </el-pagination>
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import { ElContainer, ElMain, ElCard, ElTable, ElTableColumn, ElTag, ElProgress, ElPagination, ElSelect, ElOption, ElInput, ElButton } from 'element-plus'
import { useRouter } from 'vue-router'
import { projectApi } from '@/api/index.js'

const router = useRouter()
const emit = defineEmits(['data-loaded'])

// 接收配置参数
const props = defineProps({
  title: {
    type: String,
    default: '任务详情'
  },
  subtitle: {
    type: String,
    default: '查看任务详细信息'
  },
  taskType: {
    type: String,
    default: 'all' // milestone, subtask, completed_task, completed_milestone, etc.
  },
  showStatsCards: {
    type: Boolean,
    default: true
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  showTaskType: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  tableHeight: {
    type: Number,
    default: 500
  },
  totalTasksLabel: {
    type: String,
    default: '总任务数'
  },
  completedTasksLabel: {
    type: String,
    default: '已完成任务'
  },
  pendingTasksLabel: {
    type: String,
    default: '待完成任务'
  },
  listTitle: {
    type: String,
    default: '任务列表'
  },
  statusPlaceholder: {
    type: String,
    default: '按状态筛选'
  },
  searchPlaceholder: {
    type: String,
    default: '搜索任务名称或负责人'
  },
  statusOptions: {
    type: Array,
    default: () => [
      { label: '未开始', value: '未开始' },
      { label: '进行中', value: '进行中' },
      { label: '完成', value: '完成' },
      { label: '延期完成', value: '延期完成' },
      { label: '异常', value: '异常' }
    ]
  }
})

// 数据状态
const loading = ref(false)
const tasks = ref([])
const filteredTasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)
const statusFilter = ref('')
const searchKeyword = ref('')

// 统计数据
const stats = ref({
  totalTasks: 0,
  completedTasks: 0,
  pendingTasks: 0
})

// 当前时间
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

// 获取任务数据
const fetchTasks = async () => {
  loading.value = true
  try {
    // 并行获取任务数据和总数
    const [response, totalCount] = await Promise.all([
      projectApi.getTasksByType({
        type: props.taskType,
        page: currentPage.value,
        limit: pageSize.value
      }),
      projectApi.getTasksByTypeCount(props.taskType)
    ])
    
    tasks.value = response || []
    filteredTasks.value = tasks.value
    totalTasks.value = totalCount
    
    // 计算统计信息
    calculateStats()
    
    emit('data-loaded', tasks.value)
  } catch (error) {
    console.error(`获取${props.title}失败:`, error)
  } finally {
    loading.value = false
  }
}

// 计算统计数据
const calculateStats = () => {
  const completed = tasks.value.filter(task => 
    task.status === '按时完成' || task.status === '延期完成' || task.status === '完成'  // 所有完成类状态
  ).length
  const pending = tasks.value.filter(task => 
    task.status === '异常'  // 异常 = 待完成任务
  ).length
  
  stats.value = {
    totalTasks: tasks.value.length,
    completedTasks: completed,
    pendingTasks: pending
  }
}

// 搜索处理
const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    filteredTasks.value = tasks.value
  } else {
    filteredTasks.value = tasks.value.filter(task =>
      task.taskName.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      task.owner.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTasks()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchTasks()
}

// 状态标签类型
const getStatusTagType = (status) => {
  if (!status) return 'info';
  
  switch (status) {
    case '未开始':
    case 'not_started':
      return 'warning'
    case '进行中':
    case 'in_progress':
      return 'info'
    case '完成':
    case '已完成':
    case 'completed':
      return 'success'
    case '延期完成':
    case 'overdue_completed':
      return 'danger'
    case '异常':
    case 'exception':
      return 'danger'
    default:
      return 'info'
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 进度条颜色
const getProgressColor = (percentage) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 初始化
onMounted(() => {
  // 更新当前时间
  updateTime()
  setInterval(updateTime, 1000)
  
  // 获取数据
  fetchTasks()
})
</script>

<style scoped>
.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  display: flex;
  align-items: center;
}

.pagination-section {
  margin-top: 20px;
  text-align: center;
}
</style>