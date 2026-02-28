<template>
  <el-container style="min-height: 100vh;">
    <!-- 固定的顶部导航 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="position: absolute; left: 30px;">
          <el-button @click="goBack" icon="ArrowLeft" size="large" style="font-size: 18px; padding: 12px;">
            返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            项目状态详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看项目详细状态信息</p>
        </div>
        <div style="display: flex; align-items: center; gap: 15px; position: absolute; right: 30px;">
          <el-button 
            type="primary" 
            @click="exportCurrentData"
            :loading="exportLoading"
            icon="Download"
            style="background-color: #67C23A; border-color: #67C23A;"
          >
            批量导出
          </el-button>
          <div style="color: white; font-size: 18px;">{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <el-card shadow="hover" v-if="projectData">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ getStatusDisplayName(projectData.status) }}项目详情</span>
          </div>
        </template>

        <!-- 项目基本信息 -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ projectData.project_name }}</el-descriptions-item>
          <el-descriptions-item label="项目经理">{{ projectData.project_manager }}</el-descriptions-item>
          <el-descriptions-item label="项目分类">
            <el-tag :type="getCategoryTagType(projectData.category)">
              {{ projectData.category }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(projectData.status)">
              {{ getStatusDisplayName(projectData.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计划开始时间">{{ formatDate(projectData.planned_start_date) }}</el-descriptions-item>
          <el-descriptions-item label="计划结束时间">{{ formatDate(projectData.planned_end_date) }}</el-descriptions-item>
          <el-descriptions-item label="实际开始时间">{{ formatDate(projectData.actual_start_date) }}</el-descriptions-item>
          <el-descriptions-item label="实际结束时间">{{ formatDate(projectData.actual_end_date) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(projectData.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(projectData.updated_at) }}</el-descriptions-item>
        </el-descriptions>

        <!-- 项目描述 -->
        <div v-if="projectData.description" style="margin-top: 20px;">
          <h3>项目描述</h3>
          <p>{{ projectData.description }}</p>
        </div>
      </el-card>

      <!-- 加载状态 -->
      <el-card shadow="hover" v-else>
        <div style="text-align: center; padding: 40px;">
          <el-text tag="ins">加载中...</el-text>
        </div>
      </el-card>

      <!-- 项目统计概览 -->
      <el-card shadow="hover" style="margin-top: 20px;" v-if="allProjects.length > 0">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">项目统计概览</span>
          </div>
        </template>
        
        <!-- 统计卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">项目总数</div>
                <div class="stat-value">{{ allProjects.length }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">项目经理数</div>
                <div class="stat-value" style="color: #409EFF;">{{ getUniqueManagersCount() }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">平均项目周期</div>
                <div class="stat-value" style="color: #67C23A;">{{ getAverageProjectDuration() }}天</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">完成率</div>
                <div class="stat-value" style="color: #E6A23C;">{{ getCompletionRate() }}%</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-card>

      <!-- 项目筛选和搜索 -->
      <el-card shadow="hover" style="margin-top: 20px;" v-if="allProjects.length > 0">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">项目筛选</span>
          </div>
        </template>
        
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="8">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索项目名称或项目经理" 
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <i class="el-icon-search"></i>
              </template>
            </el-input>
          </el-col>
          <el-col :span="8">
            <el-select 
              v-model="managerFilter" 
              placeholder="按项目经理筛选" 
              clearable
              @change="handleManagerFilter"
              style="width: 100%"
            >
              <el-option 
                v-for="manager in getUniqueManagers()" 
                :key="manager" 
                :label="manager" 
                :value="manager"
              />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-select 
              v-model="categoryFilter" 
              placeholder="按项目分类筛选" 
              clearable
              @change="handleCategoryFilter"
              style="width: 100%"
            >
              <el-option label="未开始" value="未开始" />
              <el-option label="进行中" value="进行中" />
              <el-option label="已结项" value="已结项" />
            </el-select>
          </el-col>
        </el-row>
      </el-card>

      <!-- 项目列表 -->
      <el-card shadow="hover" style="margin-top: 20px;" v-if="allProjects.length > 0">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ getStatusDisplayName(currentStatus) }}项目列表 ({{ (filteredProjects.length > 0 ? filteredProjects : allProjects).length }}个)</span>
          </div>
        </template>

        <el-table 
          :data="filteredProjects.length > 0 ? filteredProjects : allProjects" 
          style="width: 100%" 
          stripe
          border
        >
          <el-table-column prop="project_name" label="项目名称" min-width="200"></el-table-column>
          <el-table-column prop="project_manager" label="项目经理" width="120"></el-table-column>
          <el-table-column prop="category" label="项目分类" width="120">
            <template #default="scope">
              <el-tag :type="getCategoryTagType(scope.row.category)">
                {{ scope.row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="planned_start_date" label="计划开始时间" width="150">
            <template #default="scope">
              {{ formatDate(scope.row.planned_start_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="planned_end_date" label="计划结束时间" width="150">
            <template #default="scope">
              {{ formatDate(scope.row.planned_end_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150">
            <template #default="scope">
              {{ formatDate(scope.row.actual_start_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150">
            <template #default="scope">
              {{ formatDate(scope.row.actual_end_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      <el-card shadow="hover" style="margin-top: 20px;" v-if="subtasksData.length > 0">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ getStatusDisplayName(currentStatus) }}子任务详情</span>
            <el-button 
              style="float: right; padding: 3px 0" 
              type="text"
              @click="refreshSubtasks"
              :loading="subtasksLoading"
            >
              刷新
            </el-button>
          </div>
        </template>

        <!-- 子任务统计卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px;">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">总任务数</div>
                <div class="stat-value">{{ subtaskStats.total }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">进行中</div>
                <div class="stat-value" style="color: #409EFF;">{{ subtaskStats.ongoing }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">已完成</div>
                <div class="stat-value" style="color: #67C23A;">{{ subtaskStats.completed }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-title">未开始</div>
                <div class="stat-value" style="color: #E6A23C;">{{ subtaskStats.notStarted }}</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 子任务表格 -->
        <el-table 
          :data="subtasksData" 
          style="width: 100%" 
          v-loading="subtasksLoading"
          stripe
          border
        >
          <el-table-column prop="task_name" label="任务名称" min-width="150"></el-table-column>
          <el-table-column prop="assignee" label="负责人" width="120"></el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getSubtaskStatusTagType(scope.row.status)">
                {{ getSubtaskStatusDisplayName(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="120">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.progress" 
                :stroke-width="10"
                :color="getProgressColor(scope.row.progress)"
              ></el-progress>
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始时间" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.start_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="end_date" label="结束时间" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.end_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 无子任务数据提示 -->
      <el-card shadow="hover" style="margin-top: 20px;" v-else>
        <div style="text-align: center; padding: 40px;">
          <el-empty description="暂无子任务数据"></el-empty>
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElText, ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { projectApi } from '@/api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 项目数据状态
const projectData = ref(null)
const allProjects = ref([])  // 存储所有项目数据

// 子任务数据状态
const subtasksData = ref([])
const subtasksLoading = ref(false)
const currentStatus = ref('')
const subtaskStats = ref({
  total: 0,
  ongoing: 0,
  completed: 0,
  notStarted: 0
})

// 筛选和搜索状态
const searchKeyword = ref('')
const managerFilter = ref('')
const categoryFilter = ref('')
const filteredProjects = ref([])

// 导出状态
const exportLoading = ref(false)

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

// 获取状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 'not_started':
      return 'warning'
    case 'ongoing':
      return 'primary'
    case 'completed':
      return 'success'
    case '已结项':
      return 'success'
    case '进行中':
      return 'primary'
    case '未开始':
      return 'warning'
    default:
      return 'info'
  }
}

// 格式化日期显示
const formatDate = (dateValue) => {
  if (!dateValue || dateValue === '-' || dateValue === 'None') {
    return '-'
  }
  
  try {
    // 如果已经是字符串格式的日期
    if (typeof dateValue === 'string') {
      // 检查是否为有效日期字符串
      if (dateValue.match(/^\d{4}-\d{2}-\d{2}/)) {
        return dateValue
      }
      // 尝试解析其他格式
      const dateObj = new Date(dateValue)
      if (!isNaN(dateObj.getTime())) {
        return dateObj.toISOString().split('T')[0]
      }
    }
    
    // 如果是Date对象
    if (dateValue instanceof Date) {
      return dateValue.toISOString().split('T')[0]
    }
    
    return String(dateValue)
  } catch (error) {
    console.error('日期格式化错误:', error)
    return String(dateValue)
  }
}

// 获取子任务状态标签类型
const getSubtaskStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
    case '已验收':
      return 'success'
    default:
      return 'info'
  }
}

// 获取子任务状态显示名称
const getSubtaskStatusDisplayName = (status) => {
  return status || '未知状态'
}

// 获取进度颜色
const getProgressColor = (progress) => {
  if (progress >= 80) return '#67C23A'
  if (progress >= 50) return '#409EFF'
  if (progress >= 20) return '#E6A23C'
  return '#F56C6C'
}

// 获取状态显示名称
const getStatusDisplayName = (status) => {
  switch (status) {
    case 'not_started':
      return '未开始'
    case 'ongoing':
      return '进行中'
    case 'completed':
      return '已结项'
    case 'total':
      return '全部'
    default:
      return status || '未知状态'
  }
}

// 获取唯一项目经理数量
const getUniqueManagersCount = () => {
  if (!allProjects.value || allProjects.value.length === 0) return 0
  const managers = [...new Set(allProjects.value.map(p => p.project_manager).filter(Boolean))]
  return managers.length
}

// 获取平均项目周期
const getAverageProjectDuration = () => {
  if (!allProjects.value || allProjects.value.length === 0) return 0
  
  const durations = allProjects.value
    .map(project => {
      const start = project.planned_start_date ? new Date(project.planned_start_date) : null
      const end = project.planned_end_date ? new Date(project.planned_end_date) : null
      
      if (start && end && !isNaN(start.getTime()) && !isNaN(end.getTime())) {
        return (end - start) / (1000 * 60 * 60 * 24) // 转换为天数
      }
      return 0
    })
    .filter(duration => duration > 0)
  
  if (durations.length === 0) return 0
  
  const average = durations.reduce((sum, duration) => sum + duration, 0) / durations.length
  return Math.round(average)
}

// 获取完成率
const getCompletionRate = () => {
  if (!allProjects.value || allProjects.value.length === 0) return 0
  
  const completedCount = allProjects.value.filter(project => 
    project.category === '已结项'
  ).length
  
  return Math.round((completedCount / allProjects.value.length) * 100)
}

// 获取唯一项目经理列表
const getUniqueManagers = () => {
  if (!allProjects.value || allProjects.value.length === 0) return []
  return [...new Set(allProjects.value.map(p => p.project_manager).filter(Boolean))]
}

// 处理搜索
const handleSearch = () => {
  applyFilters()
}

// 处理项目经理筛选
const handleManagerFilter = () => {
  applyFilters()
}

// 处理分类筛选
const handleCategoryFilter = () => {
  applyFilters()
}

// 应用所有筛选条件
const applyFilters = () => {
  let result = [...allProjects.value]
  
  // 搜索筛选
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(project => 
      (project.project_name && project.project_name.toLowerCase().includes(keyword)) ||
      (project.project_manager && project.project_manager.toLowerCase().includes(keyword))
    )
  }
  
  // 项目经理筛选
  if (managerFilter.value) {
    result = result.filter(project => project.project_manager === managerFilter.value)
  }
  
  // 分类筛选
  if (categoryFilter.value) {
    result = result.filter(project => project.category === categoryFilter.value)
  }
  
  filteredProjects.value = result
}

// 刷新子任务数据
const refreshSubtasks = async () => {
  subtasksLoading.value = true
  try {
    // 这里可以添加刷新子任务的逻辑
    console.log('刷新子任务数据')
    // 模拟刷新延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('刷新子任务失败:', error)
  } finally {
    subtasksLoading.value = false
  }
}

// 获取项目详情
const fetchProjectDetail = async () => {
  try {
    // 从路由参数获取状态
    const status = route.params.status || route.query.status
    console.log('获取项目状态参数:', status)
    
    if (!status) {
      console.error('未找到项目状态参数')
      projectData.value = {
        project_name: '参数错误',
        project_manager: '系统',
        category: '未知',
        status: 'unknown',
        planned_start_date: '-',
        planned_end_date: '-',
        actual_start_date: '-',
        actual_end_date: '-',
        created_at: '-',
        updated_at: '-'
      }
      return
    }

    // 获取所有项目详情
    console.log('开始获取项目详情数据...')
    const response = await projectApi.getProjectsDetail()
    console.log('获取到的项目详情数据:', response)
    
    if (response && Array.isArray(response) && response.length > 0) {
      // 存储所有项目数据
      allProjects.value = [...response]
      currentStatus.value = status
      
      // 根据状态筛选项目
      let filteredProjects = []
      
      if (status === 'total') {
        // 总览：显示所有项目
        filteredProjects = [...response]
      } else {
        // 根据状态筛选
        filteredProjects = response.filter(project => {
          if (!project || typeof project !== 'object') return false
          
          // 统一处理日期
          const plannedStartDate = project.planned_start_date
          const plannedEndDate = project.planned_end_date
          const actualEndDate = project.actual_end_date
          
          // 转换日期为Date对象
          let startDateObj = null
          let endDateObj = null
          let actualEndDateObj = null
          
          if (plannedStartDate) {
            startDateObj = new Date(plannedStartDate)
          }
          if (plannedEndDate) {
            endDateObj = new Date(plannedEndDate)
          }
          if (actualEndDate) {
            actualEndDateObj = new Date(actualEndDate)
          }
          
          const currentDate = new Date()
          
          // 根据不同状态进行筛选
          switch (status) {
            case 'not_started':
              // 未开始：计划开始日期大于当前日期
              return startDateObj && startDateObj > currentDate
            
            case 'ongoing':
              // 进行中：当前日期在计划开始和结束之间
              return startDateObj && endDateObj && 
                     currentDate >= startDateObj && 
                     currentDate <= endDateObj &&
                     (!actualEndDateObj || actualEndDateObj >= currentDate)
            
            case 'completed':
              // 已结项：实际结束日期早于当前日期，或者计划结束日期早于当前日期且无实际结束日期
              return (actualEndDateObj && actualEndDateObj < currentDate) ||
                     (!actualEndDateObj && endDateObj && endDateObj < currentDate)
            
            default:
              return false
          }
        })
      }

      console.log(`筛选后的项目数量: ${filteredProjects.length}`)
      console.log('筛选后的项目列表:', filteredProjects)

      // 设置项目数据 - 显示统计信息
      projectData.value = {
        project_name: `${getStatusDisplayName(status)}项目 (${filteredProjects.length}个)`,
        project_manager: '系统',
        category: getStatusDisplayName(status),
        status: status,
        planned_start_date: '-',
        planned_end_date: '-',
        actual_start_date: '-',
        actual_end_date: '-',
        created_at: '-',
        updated_at: '-'
      }
      
      // 应用初始筛选
      applyFilters()
      
      console.log('设置的项目数据:', projectData.value)
    } else {
      console.log('未获取到项目数据或数据格式错误')
      // 如果没有获取到数据，显示默认信息
      projectData.value = {
        project_name: '暂无项目数据',
        project_manager: '系统',
        category: getStatusDisplayName(status),
        status: status,
        planned_start_date: '-',
        planned_end_date: '-',
        actual_start_date: '-',
        actual_end_date: '-',
        created_at: '-',
        updated_at: '-'
      }
      allProjects.value = []
      filteredProjects.value = []
      currentStatus.value = status
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    // 错误处理，显示错误信息
    const status = route.params.status || route.query.status || 'unknown'
    projectData.value = {
      project_name: '数据加载失败',
      project_manager: '系统',
      category: getStatusDisplayName(status),
      status: status,
      planned_start_date: '-',
      planned_end_date: '-',
      actual_start_date: '-',
      actual_end_date: '-',
      created_at: '-',
      updated_at: '-'
    }
  }
}

// 监听路由参数变化
watch(
  () => route.params.status,
  async (newStatus, oldStatus) => {
    if (newStatus !== oldStatus) {
      console.log('路由参数变化，重新获取数据:', newStatus)
      await fetchProjectDetail()
    }
  }
)

// 返回上一页
const goBack = () => {
  router.go(-1)  // 返回上一页
}

// 批量导出当前页面数据
const exportCurrentData = async () => {
  try {
    // 获取当前显示的数据
    const currentData = filteredProjects.value.length > 0 ? filteredProjects.value : allProjects.value
    
    if (currentData.length === 0) {
      ElMessage.warning('当前没有可导出的数据')
      return
    }
    
    // 询问用户确认
    await ElMessageBox.confirm(
      `确定要导出当前显示的 ${currentData.length} 条项目数据吗？`,
      '导出确认',
      {
        confirmButtonText: '确定导出',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    exportLoading.value = true
    
    // 获取所有项目ID
    const projectIds = currentData.map(project => project.project_id)
    
    // 调用导出API
    const blob = await projectApi.exportProjects(projectIds)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `项目_${getStatusDisplayName(currentStatus.value)}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`成功导出 ${currentData.length} 条项目数据`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出失败:', error)
      ElMessage.error('导出失败: ' + (error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

// 初始化数据
onMounted(async () => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)

  // 获取项目详情
  await fetchProjectDetail()
})

onUnmounted(() => {
  // 清理定时器（如果有的话）
})
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

.stat-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  padding: 10px 0;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}
</style>