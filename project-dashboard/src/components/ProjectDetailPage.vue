<template>
  <el-container style="min-height: 100vh; padding-top: 120px;">
    <!-- 固定顶部标题栏 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            {{ pageTitle }}
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">
            {{ pageSubtitle }}
          </p>
        </div>
        <div style="color: white; font-size: 18px; text-align: right;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 顶部导航 -->
    <el-header style="background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; flex-shrink: 0;">
      <el-menu :default-active="activeMenu" mode="horizontal" background-color="#fff" text-color="#333" active-text-color="#409EFF">
        <el-menu-item index="1" @click="goBack">返回项目总览</el-menu-item>
      </el-menu>
    </el-header>

    <el-main style="padding: 20px">
      <!-- 项目列表 -->
      <el-card shadow="hover">
        <div slot="header" class="card-header">项目列表</div>
        <el-table :data="projects" border style="width: 100%" v-loading="loading" fit="true" :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }" :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }">
          <el-table-column prop="project_name" label="项目名称" min-width="200" align="center" header-align="center" />
          <el-table-column prop="project_manager" label="项目经理" width="120" align="center" header-align="center" />
          <el-table-column prop="planned_start_date" label="计划开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="planned_end_date" label="计划结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
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
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElContainer, ElHeader, ElMain, ElCard, ElMenu, ElMenuItem, ElTable, ElTableColumn, ElTag, ElMessage } from 'element-plus'
import { projectApi } from '@/api/index.js'

// 接收传入的项目状态参数
const props = defineProps({
  status: {
    type: String,
    default: 'total'
  }
})

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

// 页面标题和副标题
const pageTitle = ref('')
const pageSubtitle = ref('')

// 导航激活项
const activeMenu = ref('1')

// 项目列表数据
const projects = ref([])
const loading = ref(false)

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

// 设置页面标题和副标题
const setPageTitle = () => {
  switch (props.status) {
    case 'total':
      pageTitle.value = '全部项目列表'
      pageSubtitle.value = '查看所有项目详细信息'
      break
    case 'not_started':
      pageTitle.value = '未开始项目列表'
      pageSubtitle.value = '查看所有未开始项目详细信息'
      break
    case 'ongoing':
      pageTitle.value = '进行中项目列表'
      pageSubtitle.value = '查看所有进行中项目详细信息'
      break
    case 'completed':
      pageTitle.value = '已结项项目列表'
      pageSubtitle.value = '查看所有已结项项目详细信息'
      break
    default:
      pageTitle.value = '项目列表'
      pageSubtitle.value = '查看项目详细信息'
  }
}

// 获取项目列表数据
const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await projectApi.getProjectsByStatus(props.status)
    if (res) {
      projects.value = res
    }
  } catch (error) {
    console.error(`获取${getStatusText(props.status)}项目列表失败:`, error)
    ElMessage.error(`获取${getStatusText(props.status)}项目列表失败`)
  } finally {
    loading.value = false
  }
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
      return ''
  }
}

// 返回项目总览页面
const goBack = () => {
  // 使用history返回上一页
  window.history.back()
}

// 挂载时初始化数据
onMounted(async () => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)
  
  // 设置页面标题
  setPageTitle()
  
  // 获取项目列表数据
  await fetchProjects()
})

// 卸载时清理定时器
onUnmounted(() => {
  // 清理定时器
})
</script>

<style scoped>
.card-header {
  font-weight: 600;
  font-size: 14px;
  padding-bottom: 8px;
}
</style>