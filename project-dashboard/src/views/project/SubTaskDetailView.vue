<template>
  <div class="sub-task-detail">
    <div class="header-section">
      <h2>子任务详情</h2>
      <div class="back-button">
        <button @click="goBack" class="btn btn-primary">返回</button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ subTaskStats.totalSubTasks }}</div>
          <div class="stat-label">子任务总数</div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number" :style="{ color: '#67C23A' }">{{ subTaskStats.acceptedSubTasks }}</div>
          <div class="stat-label">已验收子任务</div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-number" :style="{ color: '#E6A23C' }">{{ subTaskStats.pendingSubTasks }}</div>
          <div class="stat-label">待验收子任务</div>
        </div>
      </el-card>
    </div>

    <!-- 子任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>子任务列表</span>
          <div class="filter-section">
            <el-select 
              v-model="statusFilter" 
              placeholder="按状态筛选" 
              style="width: 150px; margin-right: 10px;"
              @change="fetchSubTasks"
            >
              <el-option label="全部" value=""></el-option>
              <el-option label="未开始" value="未开始"></el-option>
              <el-option label="进行中" value="进行中"></el-option>
              <el-option label="已完成" value="已完成"></el-option>
              <el-option label="已验收" value="已验收"></el-option>
            </el-select>
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索任务名称或负责人" 
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
        height="500"
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
      <div class="pagination-section">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElCard, ElTable, ElTableColumn, ElTag, ElProgress, ElPagination, ElSelect, ElOption, ElInput } from 'element-plus'
import { useRouter } from 'vue-router'
import { projectApi } from '@/api/index.js'

const router = useRouter()

// 数据状态
const loading = ref(false)
const subTasks = ref([])
const filteredTasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)
const statusFilter = ref('')
const searchKeyword = ref('')

// 统计数据
const subTaskStats = ref({
  totalSubTasks: 0,
  acceptedSubTasks: 0,
  pendingSubTasks: 0
})

// 获取子任务数据
const fetchSubTasks = async () => {
  loading.value = true
  try {
    // 获取所有子任务（wbsNo包含小数点）
    const response = await projectApi.getTasksByType({
      type: 'subtask',  // 获取所有子任务
      page: currentPage.value,
      limit: pageSize.value
    })
    
    subTasks.value = response || []
    filteredTasks.value = subTasks.value
    totalTasks.value = await getSubTasksCount()
    
    // 计算统计信息
    calculateStats()
  } catch (error) {
    console.error('获取子任务失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取所有子任务数据
const fetchAllSubTasks = async () => {
  try {
    // 获取所有子任务（使用大分页一次性获取）
    const response = await projectApi.getTasksByType({
      type: 'subtask',
      page: 1,
      limit: 10000  // 获取足够大的数量以包含所有数据
    })
    
    return response || []
  } catch (error) {
    console.error('获取所有子任务失败:', error)
    return []
  }
}

// 计算统计信息
const calculateStats = async () => {
  // 获取所有子任务来准确计算统计信息
  const allSubTasks = await fetchAllSubTasks()
  
  const total = allSubTasks.length
  const accepted = allSubTasks.filter(task => task.actual_start_date && task.actual_end_date).length
  const pending = total - accepted
  
  subTaskStats.value = {
    totalSubTasks: total,
    acceptedSubTasks: accepted,
    pendingSubTasks: pending
  }
  
  // 同时更新当前页面显示的数据
  subTasks.value = allSubTasks
  filteredTasks.value = allSubTasks.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  )
  totalTasks.value = allSubTasks.length
}

// 获取子任务总数
const getSubTasksCount = async () => {
  try {
    const count = await projectApi.getTasksByTypeCount('subtask')
    return count || 0
  } catch (error) {
    console.error('获取子任务总数失败:', error)
    return 0
  }
}

// 根据状态获取标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'info'
    case '进行中':
      return 'warning'
    case '已完成':
      return 'success'
    case '已验收':
      return 'primary'
    default:
      return 'info'
  }
}

// 获取进度条颜色
const getProgressColor = (progress) => {
  if (progress < 30) return '#F56C6C'  // 红色
  if (progress < 70) return '#E6A23C'  // 黄色
  return '#67C23A'  // 绿色
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toISOString().split('T')[0]
}

// 返回上一页
const goBack = () => {
  router.push({ name: 'HomePage' })
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSubTasks()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchSubTasks()
}

// 处理搜索
const handleSearch = () => {
  let result = subTasks.value
  
  // 按状态筛选
  if (statusFilter.value) {
    result = result.filter(task => task.status === statusFilter.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task => 
      task.taskName.toLowerCase().includes(keyword) || 
      task.owner.toLowerCase().includes(keyword) ||
      task.projectName.toLowerCase().includes(keyword)
    )
  }
  
  filteredTasks.value = result
  totalTasks.value = result.length
}

// 页面加载时获取数据
onMounted(() => {
  fetchSubTasks()
})
</script>

<style scoped>
.sub-task-detail {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.back-button .btn {
  padding: 8px 16px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 200px;
  text-align: center;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.task-list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  display: flex;
  gap: 10px;
}

.task-name {
  font-weight: 500;
  color: #303133;
}

.project-name {
  color: #606266;
}

.owner-name {
  color: #409EFF;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-cards {
    flex-direction: column;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-section {
    width: 100%;
  }
}
</style>