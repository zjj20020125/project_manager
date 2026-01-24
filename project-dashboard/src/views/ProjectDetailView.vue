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
            {{ statusText }}项目详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看{{ statusText }}项目的详细信息</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;"> <!-- 调整内边距以避免内容被固定头部遮挡 -->
      <el-card shadow="hover">
        <el-table 
          :data="filteredProjects" 
          border 
          style="width: 100%" 
          v-loading="loading"
        >
          <el-table-column prop="project_name" label="项目名称" min-width="200" />
          <el-table-column prop="project_manager" label="项目经理" width="120" />
          <el-table-column prop="planned_start_date" label="计划开始时间" width="150" />
          <el-table-column prop="planned_end_date" label="计划结束时间" width="150" />
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150" />
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150" />
          <el-table-column prop="category" label="项目分类" width="120">
            <template #default="scope">
              <el-tag :type="getCategoryTagType(scope.row.category)">
                {{ scope.row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
        </el-table>
        
        <!-- 分页组件 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalProjects"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElContainer, ElMain, ElTable, ElTableColumn, ElTag, ElPagination, ElButton, ElCard } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 页面数据状态
const filteredProjects = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalProjects = ref(0)

// 获取状态参数
const statusParam = ref('')
const statusText = ref('')

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

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'total':
      return '全部'
    case 'not_started':
      return '未开始'
    case 'ongoing':
      return '进行中'
    case 'completed':
      return '已结项'
    default:
      return '全部'
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

// 获取项目数据
const fetchProjectsByStatus = async () => {
  loading.value = true
  try {
    // 根据状态参数获取相应项目数据
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      status: statusParam.value
    }
    
    // 根据具体状态过滤项目
    const response = await projectApi.getProjectsByStatus(params)
    
    if (response) {
      // 处理响应数据格式
      if (Array.isArray(response)) {
        filteredProjects.value = response
        totalProjects.value = response.length
      } else {
        // 根据API的实际返回格式处理
        filteredProjects.value = response
        totalProjects.value = response.length
      }
    } else {
      filteredProjects.value = []
      totalProjects.value = 0
    }
  } catch (error) {
    console.error(`获取${statusText.value}项目失败:`, error)
    filteredProjects.value = []
    totalProjects.value = 0
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchProjectsByStatus()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchProjectsByStatus()
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

  // 从URL参数获取状态值
  statusParam.value = route.query.status || 'total'
  statusText.value = getStatusText(statusParam.value)

  // 获取项目数据
  await fetchProjectsByStatus()
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
.chart-container {
  width: 100%;
  height: 260px;
}
.gantt-container {
  width: 100%;
  height: 300px;
}
</style>