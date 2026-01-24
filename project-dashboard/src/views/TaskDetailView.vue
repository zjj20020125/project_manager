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
            任务详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看任务详细信息</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">
              {{ getTaskTypeName(taskType) }}
            </span>
          </div>
        </template>
        
        <!-- 任务列表 -->
        <el-table 
          :data="taskList" 
          border 
          style="width: 100%" 
          v-loading="loading"
          :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }"
          :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
        >
          <el-table-column prop="taskName" label="任务名称" min-width="200" align="center" header-align="center" />
          <el-table-column prop="projectName" label="所属项目" width="150" align="center" header-align="center" />
          <el-table-column prop="wbsNo" label="WBS编码" width="120" align="center" header-align="center" />
          <el-table-column prop="owner" label="任务负责人" width="120" align="center" header-align="center" />
          <el-table-column prop="planStart" label="计划开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="planEnd" label="计划结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="progress" label="任务进度" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-progress :percentage="Number(scope.row.progress || 0)" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="任务状态" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-tag :type="getTaskStatusTagType(scope.row.status)">
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
      
      <!-- 加载状态 -->
      <el-card shadow="hover" v-if="!taskList.length && loading">
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
import { ElContainer, ElMain, ElCard, ElTag, ElButton, ElText, ElTable, ElTableColumn, ElProgress, ElPagination } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '../api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 任务列表状态
const taskList = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalTasks = ref(0)
const taskType = ref('')

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


// 获取任务类型名称
const getTaskTypeName = (type) => {
  switch (type) {
    case 'milestone':
      return '里程碑任务详情'
    case 'completed_milestone':
      return '已验收里程碑任务详情'
    case 'subtask':
      return '子任务详情'
    case 'completed_task':
      return '已验收任务详情'
    default:
      return '任务详情'
  }
}

// 获取任务状态标签类型
const getTaskStatusTagType = (status) => {
  // 处理可能的空值
  if (!status) return 'info';
  
  switch (status) {
    case '未开始':
    case 'not_started':
      return 'warning'
    case '进行中':
    case 'in_progress':
      return 'info'
    case '已完成':
    case '完成':
    case 'completed':
      return 'success'
    case '已验收':
    case 'accepted':
      return 'primary'
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

// 获取任务详情
const fetchTaskDetail = async () => {
  loading.value = true
  try {
    // 从路由参数获取任务类型
    const type = route.query.type
    if (!type) {
      console.error('未找到任务类型参数')
      return
    }
    
    taskType.value = type
    
    // 根据任务类型获取任务列表
    const response = await projectApi.getTasksByType({ type: type, page: currentPage.value, limit: pageSize.value })
    if (response) {
      // 转换任务数据格式以匹配表格期望的字段名
      const formattedTasks = response.map(task => ({
        ...task,
        taskName: task.task_name,
        projectName: task.project_name,
        wbsNo: task.wbs_no || task.wbs_code,
        owner: task.task_owner,
        planStart: task.planned_start_date,
        planEnd: task.planned_end_date,
        status: task.task_status
      }))
      
      taskList.value = formattedTasks
      
      // 获取总任务数用于分页
      const totalCount = await projectApi.getTasksByTypeCount(type)
      totalTasks.value = totalCount
    }
  } catch (error) {
    console.error('获取任务详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchTaskDetail()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchTaskDetail()
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

  // 获取任务详情
  await fetchTaskDetail()
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