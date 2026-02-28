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
            {{ ownerName || '任务负责人' }} - 项目子任务详情
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">查看{{ ownerName || '该负责人' }}负责的项目及其子任务</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <!-- 任务负责人负责的项目列表 -->
      <el-card shadow="hover" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">负责的项目列表</span>
          </div>
        </template>
        <el-table 
          :data="ownedProjects" 
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
          <el-table-column prop="project_status" label="项目状态" width="120">
            <template #default="scope">
              <el-tag :type="getProjectStatusTagType(scope.row.project_status)">
                {{ scope.row.project_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="项目分类" width="120">
            <template #default="scope">
              <el-tag :type="getCategoryTagType(scope.row.category)">
                {{ scope.row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewProjectSubtasks(scope.row)"
              >
                查看子任务
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 任务负责人负责的所有子任务列表 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">负责的所有子任务</span>
          </div>
        </template>
        <el-table 
          :data="allOwnedTasks" 
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
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElTable, ElTableColumn, ElProgress, ElPagination } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '@/api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 当前时间状态
const currentTime = ref('')

// 任务负责人信息状态
const ownerName = ref('')
const ownerInfo = ref(null)

// 项目和任务数据状态
const ownedProjects = ref([])
const allOwnedTasks = ref([])
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

// 获取任务负责人详情
const fetchOwnerDetails = async () => {
  loading.value = true
  try {
    const owner = route.params.owner
    if (!owner) {
      console.error('未找到任务负责人名称')
      return
    }
    
    ownerName.value = decodeURIComponent(owner)
    
    // 获取所有项目详情
    const projectsResponse = await projectApi.getProjectsDetail()
    if (projectsResponse) {
      // 直接获取该负责人负责的任务
      const ownedTasks = await projectApi.getOwnerTasks(ownerName.value)
      
      if (ownedTasks) {
        // 转换任务数据格式以匹配表格期望的字段名
        const formattedTasks = ownedTasks.map(task => ({
          ...task,
          taskName: task.task_name,
          projectName: task.project_name,
          wbsNo: task.wbs_code,
          owner: task.task_owner,
          planStart: task.planned_start_date,
          planEnd: task.planned_end_date,
          status: task.task_status
        }))
        
        // 从任务中提取项目名称，找出该负责人负责的项目
        const projectNames = [...new Set(formattedTasks.map(task => task.projectName || task.project_name))]
        const ownedProjectsTemp = projectsResponse.filter(project => 
          projectNames.includes(project.project_name)
        )
        
        ownedProjects.value = ownedProjectsTemp
        
        // 设置负责人信息
        ownerInfo.value = {
          name: ownerName.value,
          position: '项目成员',
          projectCount: ownedProjectsTemp.length,
          taskCount: formattedTasks.length,
          completionRate: calculateCompletionRate(formattedTasks),
          department: '相关部门'
        }
        
        // 更新所有任务数据（当前页）
        updateTaskPage(formattedTasks)
      }
    }
  } catch (error) {
    console.error('获取任务负责人详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算完成率
const calculateCompletionRate = (tasks) => {
  if (!tasks || tasks.length === 0) return 0
  
  const completedTasks = tasks.filter(task => {
    const status = task.status || task.task_status
    return status === '完成' || 
           status === '已完成' || 
           status === '已验收' ||
           status === 'completed' ||
           status === 'accepted'
  }).length
  
  return Number(((completedTasks / tasks.length) * 100).toFixed(1))
}

// 更新任务分页数据
const updateTaskPage = (allTasks) => {
  // 计算总数
  totalTasks.value = allTasks.length
  
  // 计算当前页的数据
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  allOwnedTasks.value = allTasks.slice(startIndex, endIndex)
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  applyPagination()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  applyPagination()
}

// 应用分页
const applyPagination = async () => {
  const owner = route.params.owner
  if (!owner) return
  
  // 重新获取该负责人负责的任务数据并分页
  const ownedTasks = await projectApi.getOwnerTasks(decodeURIComponent(owner))
  
  if (ownedTasks) {
    // 转换任务数据格式以匹配表格期望的字段名
    const formattedTasks = ownedTasks.map(task => ({
      ...task,
      taskName: task.task_name,
      projectName: task.project_name,
      wbsNo: task.wbs_code,
      owner: task.task_owner,
      planStart: task.planned_start_date,
      planEnd: task.planned_end_date,
      status: task.task_status
    }))
    
    updateTaskPage(formattedTasks)
  }
}

// 查看项目子任务
const viewProjectSubtasks = (project) => {
  router.push({ 
    name: 'ProjectSubtasksDetail', 
    params: { projectId: project.project_id },
    query: { projectName: encodeURIComponent(project.project_name) }
  })
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
    case '按时完成':
    case 'completed_on_time':
      return 'success'
    case '延期完成':
    case 'delayed_completion':
      return 'warning'
    case '完成':
    case 'completed':
      return 'primary'
    case '已验收':
    case 'accepted':
      return 'success'
    case '异常':
    case 'exception':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取项目状态标签类型
const getProjectStatusTagType = (status) => {
  switch (status) {
    case '未开始':
      return 'warning'
    case '进行中':
      return 'info'
    case '已完成':
      return 'success'
    case '已结项':
      return 'success'
    case '已验收':
      return 'primary'
    default:
      return 'info'
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

  // 获取任务负责人详情
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
</style>