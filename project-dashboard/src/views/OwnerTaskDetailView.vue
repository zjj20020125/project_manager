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
            任务负责人详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看任务负责人的详细信息及分配的任务</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <!-- 任务负责人信息卡片 -->
      <el-card shadow="hover" style="margin-bottom: 20px;" v-if="ownerInfo">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">负责人信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="负责人姓名">{{ ownerInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ ownerInfo.position }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ ownerInfo.department }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ ownerInfo.contact }}</el-descriptions-item>
          <el-descriptions-item label="负责任务数">{{ ownerInfo.taskCount }}</el-descriptions-item>
          <el-descriptions-item label="完成率">{{ ownerInfo.completionRate }}%</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 负责人任务列表 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">负责的任务列表</span>
          </div>
        </template>
        <el-table 
          :data="ownerTasks" 
          border 
          style="width: 100%" 
          v-loading="loading"
        >
          <el-table-column prop="task_name" label="任务名称" min-width="200" />
          <el-table-column prop="project_name" label="所属项目" width="150" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="scope">
              <el-tag :type="getPriorityTagType(scope.row.priority)">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="assigned_date" label="分配日期" width="150" />
          <el-table-column prop="due_date" label="截止日期" width="150" />
          <el-table-column prop="progress" label="进度" width="100">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress" :show-text="false" />
              <span>{{ scope.row.progress }}%</span>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalTasks"
          :page-sizes="[5, 10, 20, 50]"
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
import { ElContainer, ElMain, ElTable, ElTableColumn, ElTag, ElPagination, ElButton, ElCard, ElDescriptions, ElDescriptionsItem, ElProgress } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 负责人信息状态
const ownerInfo = ref(null)

// 任务数据状态
const ownerTasks = ref([])
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

// 获取优先级标签类型
const getPriorityTagType = (priority) => {
  switch (priority) {
    case '高':
      return 'danger'
    case '中':
      return 'warning'
    case '低':
      return 'success'
    case 'High':
      return 'danger'
    case 'Medium':
      return 'warning'
    case 'Low':
      return 'success'
    default:
      return 'info'
  }
}

// 获取状态标签类型
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
    case '已延期':
    case 'overdue':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取负责人详情
const fetchOwnerDetails = async () => {
  loading.value = true
  try {
    // 从路由参数获取负责人名称
    const ownerName = route.params.owner
    if (!ownerName) {
      console.error('未找到负责人名称')
      return
    }
    
    // 获取负责人任务列表
    const response = await projectApi.getOwnerTasks(ownerName)
    
    if (response && response.length > 0) {
      ownerTasks.value = response
      totalTasks.value = response.length
      
      // 设置负责人信息（从第一个任务中获取）
      const firstTask = response[0]
      ownerInfo.value = {
        name: firstTask.task_owner || ownerName,
        position: '项目成员',
        department: '相关部门',
        contact: '邮箱或电话',
        taskCount: response.length,
        completionRate: calculateCompletionRate(response)
      }
    } else {
      ownerTasks.value = []
      totalTasks.value = 0
      
      // 设置默认负责人信息
      ownerInfo.value = {
        name: ownerName,
        position: '项目成员',
        department: '相关部门',
        contact: '邮箱或电话',
        taskCount: 0,
        completionRate: 0
      }
    }
  } catch (error) {
    console.error('获取负责人详情失败:', error)
    ownerTasks.value = []
    totalTasks.value = 0
    
    // 设置默认负责人信息
    ownerInfo.value = {
      name: route.params.owner || '未知',
      position: '项目成员',
      department: '相关部门',
      contact: '邮箱或电话',
      taskCount: 0,
      completionRate: 0
    }
  } finally {
    loading.value = false
  }
}

// 计算完成率
const calculateCompletionRate = (tasks) => {
  if (!tasks || tasks.length === 0) return 0
  
  const completedTasks = tasks.filter(task => 
    task.task_status === '完成' || 
    task.task_status === '已完成' || 
    task.task_status === '已验收'
  ).length
  
  return Number(((completedTasks / tasks.length) * 100).toFixed(1))
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchOwnerDetails()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchOwnerDetails()
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

  // 获取负责人详情
  await fetchOwnerDetails()
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