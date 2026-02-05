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
      <!-- 异常子任务列表 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">异常子任务列表</span>
          </div>
        </template>
        <el-table 
          :data="abnormalTasks" 
          border 
          style="width: 100%" 
          v-loading="loading"
          :header-cell-style="{ textAlign: 'center', background: '#fef0f0' }"
          :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
        >
          <el-table-column prop="taskName" label="任务名称" min-width="200" align="center" header-align="center" />
          <el-table-column prop="projectName" label="所属项目" width="150" align="center" header-align="center" />
          <el-table-column prop="wbsNo" label="WBS编码" width="120" align="center" header-align="center" />
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
          :total="totalTasks"
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
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElTable, ElTableColumn, ElProgress, ElPagination } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 负责人姓名状态
const ownerName = ref('')

// 异常子任务数据状态
const abnormalTasks = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)

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

// 获取异常任务详情
const fetchAbnormalOwnerDetails = async () => {
  loading.value = true
  try {
    const owner = route.params.owner
    if (!owner) {
      console.error('未找到负责人名称')
      return
    }
    
    ownerName.value = decodeURIComponent(owner)
    
    // 获取该负责人负责的所有异常子任务
    const tasksResponse = await projectApi.getOwnerAbnormalTasks(ownerName.value)
    
    if (tasksResponse) {
      abnormalTasks.value = tasksResponse
      totalTasks.value = tasksResponse.length
    }
  } catch (error) {
    console.error('获取异常节点负责人详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  // 这里可以根据需要重新获取数据
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  // 这里可以根据需要重新获取数据
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
</style>