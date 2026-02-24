<template>
  <el-container style="min-height: 100vh;">
    <!-- 固定的顶部导航 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #F56C6C 0%, #f78989 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="position: absolute; left: 30px;">
          <el-button @click="goBack" icon="ArrowLeft" size="large" style="font-size: 18px; padding: 12px;">
            返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            {{ ownerName || '异常节点负责人' }} - 异常任务详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看{{ ownerName || '该负责人' }}负责的异常子任务详情</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <!-- 统计概览卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">异常任务总数</div>
              <div class="stat-value">{{ totalTasks }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">首个异常节点</div>
              <div class="stat-value" style="color: #F56C6C;">{{ firstAbnormalCount }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-title">进度推迟</div>
              <div class="stat-value" style="color: #E6A23C;">{{ delayedProgressCount }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 筛选和搜索区域 -->
      <el-card shadow="hover" style="margin-bottom: 20px;">
        <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
          <el-select 
            v-model="abnormalTypeFilter" 
            placeholder="按异常类型筛选" 
            clearable
            @change="handleFilterChange"
            style="width: 200px;"
          >
            <el-option label="全部" value=""></el-option>
            <el-option label="首个异常节点" value="first_abnormal"></el-option>
            <el-option label="进度推迟" value="delayed_progress"></el-option>
          </el-select>
          
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索任务名称或项目名称" 
            style="width: 300px;"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <i class="el-icon-search"></i>
            </template>
          </el-input>
          
          <el-button 
            type="primary" 
            @click="exportData"
            :loading="exportLoading"
          >
            <i class="el-icon-download"></i> 导出数据
          </el-button>
        </div>
      </el-card>

      <!-- 异常子任务列表 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">异常子任务列表</span>
            <span style="float: right; color: #999; font-size: 14px;">
              显示 {{ filteredTasks.length }} / {{ totalTasks }} 条记录
            </span>
          </div>
        </template>
        <el-table 
          :data="filteredTasks" 
          border 
          style="width: 100%" 
          v-loading="loading"
          :header-cell-style="{ textAlign: 'center', background: '#fef0f0' }"
          :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
        >
          <el-table-column prop="taskName" label="任务名称" min-width="200" align="center" header-align="center" />
          <el-table-column prop="projectName" label="所属项目" width="150" align="center" header-align="center" />
          <el-table-column prop="wbsNo" label="WBS编码" width="120" align="center" header-align="center" />
          <el-table-column prop="abnormal_type" label="异常类型" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-tag :type="getAbnormalTypeTag(scope.row.abnormal_type_en)">
                {{ scope.row.abnormal_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="planStart" label="计划开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="planEnd" label="计划结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="progress" label="任务进度" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-progress :percentage="Number(scope.row.progress || 0)" size="small" status="exception" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="任务状态" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-tag type="danger">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredTasks.length"
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElTable, ElTableColumn, ElProgress, ElPagination, ElSelect, ElOption, ElInput, ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 从路由参数获取统计信息
const getOwnerStatsFromRoute = () => {
  try {
    const statsParam = route.query.stats;
    if (statsParam) {
      return JSON.parse(decodeURIComponent(statsParam));
    }
  } catch (error) {
    console.error('解析统计信息失败:', error);
  }
  return null;
}

// 当前时间状态
const currentTime = ref('')

// 负责人姓名状态
const ownerName = ref('')

// 异常子任务数据状态
const abnormalTasks = ref([])
const loading = ref(false)
const exportLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选和搜索状态
const abnormalTypeFilter = ref('')
const searchKeyword = ref('')

// 从路由获取的统计信息
const routeStats = getOwnerStatsFromRoute();

// 计算属性 - 优先使用路由传递的统计信息
const totalTasks = computed(() => routeStats ? routeStats.total_count : abnormalTasks.value.length)

const firstAbnormalCount = computed(() => routeStats ? routeStats.first_abnormal_count : abnormalTasks.value.filter(task => task.abnormal_type_en === 'first_abnormal').length)

const delayedProgressCount = computed(() => routeStats ? routeStats.delayed_progress_count : abnormalTasks.value.filter(task => task.abnormal_type_en === 'delayed_progress').length)

const filteredTasks = computed(() => {
  let result = [...abnormalTasks.value]
  
  // 按异常类型筛选
  if (abnormalTypeFilter.value) {
    result = result.filter(task => task.abnormal_type_en === abnormalTypeFilter.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(task => 
      (task.taskName && task.taskName.toLowerCase().includes(keyword)) ||
      (task.projectName && task.projectName.toLowerCase().includes(keyword))
    )
  }
  
  return result
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

// 获取异常任务详情（使用新的API）
const fetchAbnormalOwnerDetails = async () => {
  loading.value = true
  try {
    const owner = route.params.owner
    if (!owner) {
      console.error('未找到负责人名称')
      return
    }
    
    ownerName.value = decodeURIComponent(owner)
    
    // 使用新的API获取带有分类信息的异常任务详情
    const tasksResponse = await projectApi.getAbnormalTaskDetailByOwner(ownerName.value)
    
    if (tasksResponse) {
      abnormalTasks.value = tasksResponse
    }
  } catch (error) {
    console.error('获取异常节点负责人详情失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取异常类型标签样式
const getAbnormalTypeTag = (type) => {
  switch (type) {
    case 'first_abnormal':
      return 'danger'  // 红色 - 首个异常节点
    case 'delayed_progress':
      return 'warning' // 黄色 - 进度推迟
    default:
      return 'info'
  }
}

// 处理筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

// 导出数据功能
const exportData = async () => {
  exportLoading.value = true
  try {
    // 准备导出数据
    const exportData = filteredTasks.value.map(task => ({
      '任务名称': task.taskName,
      '所属项目': task.projectName,
      'WBS编码': task.wbsNo,
      '异常类型': task.abnormal_type,
      '计划开始时间': task.planStart,
      '计划结束时间': task.planEnd,
      '实际开始时间': task.actual_start_date,
      '实际结束时间': task.actual_end_date,
      '任务进度': `${task.progress || 0}%`,
      '任务状态': task.status
    }))
    
    // 创建CSV内容
    const headers = Object.keys(exportData[0]).join(',')
    const rows = exportData.map(row => 
      Object.values(row).map(field => `"${field}"`).join(',')
    )
    const csvContent = [headers, ...rows].join('\n')
    
    // 创建下载链接
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `异常任务详情_${ownerName.value}_${new Date().toISOString().slice(0, 10)}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exportLoading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.go(-1)  // 返回上一页
}

// 初始化数据
onMounted(async () => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)

  // 获取异常节点负责人详情
  await fetchAbnormalOwnerDetails()
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

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  text-align: center;
  padding: 20px;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
</style>