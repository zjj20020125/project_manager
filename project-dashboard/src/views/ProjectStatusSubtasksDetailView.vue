<template>
  <div class="project-status-subtasks-detail">
    <div class="header-section">
      <h2>{{ status }} 项目子任务详情</h2>
      <div class="back-button">
        <button @click="goBack" class="btn btn-primary">返回首页</button>
      </div>
    </div>



    <!-- 项目状态子任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>{{ status }} 项目子任务列表</span>
          <div class="filter-section">
            <el-select 
              v-model="statusFilter" 
              placeholder="按状态筛选" 
              style="width: 150px; margin-right: 10px;"
              @change="fetchSubtasks"
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
import { useRouter, useRoute } from 'vue-router'
import { projectApi } from '../api/index.js'

const router = useRouter()
const route = useRoute()

// 从路由参数获取状态
const status = ref(route.params.status || '')

// 数据状态
const loading = ref(false)
const subtasks = ref([])
const filteredTasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)
const statusFilter = ref('')
const searchKeyword = ref('')

// 统计数据
const subtaskStats = ref({
  totalSubtasks: 0,
  completedSubtasks: 0,
  pendingSubtasks: 0
})

// 数据格式转换函数
const convertTaskData = (task) => {
  return {
    taskName: task.task_name || '',
    projectName: task.project_name || '',
    wbsNo: task.wbs_code || '',
    taskType: task.task_type || '子任务',  // 如果没有task_type字段，默认为'子任务'
    owner: task.task_owner || '',
    status: task.task_status || '',
    planStart: task.planned_start_date || '',
    planEnd: task.planned_end_date || '',
    actual_start_date: task.actual_start_date || '',
    actual_end_date: task.actual_end_date || '',
    progress: task.progress || 0,
    created_at: task.created_at || '',
    taskId: task.task_id || ''
  };
};

// 获取项目状态子任务数据
const fetchSubtasks = async () => {
  loading.value = true
  try {
    // 根据项目状态获取对应的任务数据
    const response = await projectApi.getTasksByProjectStatusTasks(status.value)
    
    // 转换数据格式以匹配前端表格字段
    const convertedResponse = response.map(convertTaskData);
    
    subtasks.value = convertedResponse || []
    filteredTasks.value = subtasks.value
    totalTasks.value = subtasks.value.length
    
    // 计算统计信息（使用已获取的数据）
    calculateStats(subtasks.value)
  } catch (error) {
    console.error(`获取${status.value}项目子任务失败:`, error)
  } finally {
    loading.value = false
  }
}

// 计算统计信息
const calculateStats = (tasksData) => {
  const allSubtasks = tasksData || [];
  
  const total = allSubtasks.length
  // 根据数据库中的实际状态值进行统计
  const completed = allSubtasks.filter(task => task.status === '完成' || task.status === '延期完成').length  // 完成 + 延期完成 = 已完成子任务
  const pending = allSubtasks.filter(task => task.status === '异常').length  // 异常 = 待完成子任务
  
  subtaskStats.value = {
    totalSubtasks: total,
    completedSubtasks: completed,
    pendingSubtasks: pending
  }
  
  // 同时更新当前页面显示的数据
  subtasks.value = allSubtasks
  filteredTasks.value = allSubtasks.slice(
    (currentPage.value - 1) * pageSize.value,
    currentPage.value * pageSize.value
  )
  totalTasks.value = allSubtasks.length
}

// 获取所有子任务数据（保留此方法供分页使用）
const fetchAllSubtasks = async () => {
  try {
    // 根据项目状态获取对应的任务数据
    const response = await projectApi.getTasksByProjectStatusTasks(status.value)
    // 转换数据格式以匹配前端表格字段
    return response.map(convertTaskData) || [];
  } catch (error) {
    console.error(`获取所有${status.value}项目子任务失败:`, error)
    return [];
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

// 返回首页
const goBack = () => {
  router.push({ name: 'Home' })
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchSubtasks()
}

// 处理当前页变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchSubtasks()
}

// 处理搜索
const handleSearch = () => {
  let result = subtasks.value
  
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
  if (status.value) {
    fetchSubtasks()
  } else {
    console.error('未提供项目状态参数')
  }
})
</script>

<style scoped>
.project-status-subtasks-detail {
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