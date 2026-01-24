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
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <el-card shadow="hover" v-if="projectData">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ projectData.project_name }}</span>
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
              {{ projectData.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计划开始时间">{{ projectData.planned_start_date }}</el-descriptions-item>
          <el-descriptions-item label="计划结束时间">{{ projectData.planned_end_date }}</el-descriptions-item>
          <el-descriptions-item label="实际开始时间">{{ projectData.actual_start_date }}</el-descriptions-item>
          <el-descriptions-item label="实际结束时间">{{ projectData.actual_end_date }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ projectData.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ projectData.updated_at }}</el-descriptions-item>
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
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElText } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 项目数据状态
const projectData = ref(null)

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

// 获取项目详情
const fetchProjectDetail = async () => {
  try {
    // 从路由参数获取状态
    const status = route.params.status
    if (!status) {
      console.error('未找到项目状态参数')
      return
    }

    // 获取所有项目详情
    const response = await projectApi.getProjectsDetail()
    if (response && response.length > 0) {
      // 根据状态筛选项目
      const filteredProjects = response.filter(project => {
        // 根据项目状态进行筛选
        if (status === 'not_started') {
          // 未开始：计划开始日期大于当前日期
          return project.planned_start_date && new Date(project.planned_start_date) > new Date()
        } else if (status === 'ongoing') {
          // 进行中：当前日期在计划开始和结束之间
          const currentDate = new Date()
          const startDate = project.planned_start_date ? new Date(project.planned_start_date) : null
          const endDate = project.planned_end_date ? new Date(project.planned_end_date) : null
          return startDate && endDate && currentDate >= startDate && currentDate <= endDate
        } else if (status === 'completed') {
          // 已结项：实际结束日期早于当前日期
          return project.actual_end_date && new Date(project.actual_end_date) < new Date()
        } else {
          // total 或其他情况，返回所有项目
          return true
        }
      })

      // 如果有筛选结果，取第一个项目作为示例
      if (filteredProjects.length > 0) {
        projectData.value = filteredProjects[0]
      }
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
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
</style>