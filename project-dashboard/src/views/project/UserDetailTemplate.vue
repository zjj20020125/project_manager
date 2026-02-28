<template>
  <el-container style="min-height: 100vh;">
    <!-- 固定的顶部导航 -->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; position: relative;">
        <div style="position: absolute; left: 30px;">
          <el-button @click="goBack" icon="ArrowLeft" size="large" style="font-size: 18px; padding: 12px;">
            返回
          </el-button>
        </div>
        <div style="text-align: center; flex-grow: 1; margin: 0 20px;">
          <h1 style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">
            {{ title }}
          </h1>
          <p style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">{{ subtitle }}</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 30px;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <el-main style="padding-top: 160px;">
      <!-- 用户信息卡片 -->
      <el-card shadow="hover" style="margin-bottom: 20px;" v-if="userInfo">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ userInfoTitle }}</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="userFields.nameLabel || '姓名'">{{ userInfo.name }}</el-descriptions-item>
          <el-descriptions-item :label="userFields.positionLabel || '职位'">{{ userInfo.position }}</el-descriptions-item>
          <el-descriptions-item :label="userFields.departmentLabel || '部门'">{{ userInfo.department }}</el-descriptions-item>
          <el-descriptions-item :label="userFields.contactLabel || '联系方式'">{{ userInfo.contact }}</el-descriptions-item>
          <el-descriptions-item :label="userFields.countLabel || '负责项目数'">{{ userInfo.projectCount }}</el-descriptions-item>
          <el-descriptions-item :label="userFields.rateLabel || '完成率'">{{ userInfo.completionRate }}%</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 项目列表 -->
      <el-card shadow="hover" style="margin-bottom: 20px;" v-if="showProjectList">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ projectListTitle }}</span>
          </div>
        </template>
        <el-table 
          :data="projects" 
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
          <el-table-column v-if="showProjectActions" label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="onProjectAction(scope.row)"
              >
                {{ projectActionButtonText }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 任务列表 -->
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="font-size: 18px; font-weight: bold;">{{ taskListTitle }}</span>
          </div>
        </template>
        <el-table 
          :data="tasks" 
          border 
          style="width: 100%" 
          v-loading="loading"
          :header-cell-style="{ textAlign: 'center', background: '#f5f7fa' }"
          :cell-style="{ textAlign: 'center', verticalAlign: 'middle' }"
        >
          <el-table-column v-for="column in taskColumns" 
                          :key="column.prop" 
                          :prop="column.prop" 
                          :label="column.label" 
                          :width="column.width" 
                          :min-width="column.minWidth"
                          :align="column.align || 'center'"
                          :header-align="column.headerAlign || 'center'">
            <template #default="scope" v-if="column.render">
              <span v-if="column.type === 'tag'">
                <el-tag :type="column.getTagType ? column.getTagType(scope.row[column.prop]) : 'info'">
                  {{ scope.row[column.prop] }}
                </el-tag>
              </span>
              <span v-else-if="column.type === 'progress'">
                <el-progress :percentage="Number(scope.row[column.prop] || 0)" size="small" />
              </span>
              <span v-else>
                {{ scope.row[column.prop] }}
              </span>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页组件 -->
        <el-pagination
          v-if="showPagination"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalItems"
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
import { ref, onMounted, onUnmounted, defineProps, defineEmits } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElContainer, ElMain, ElCard, ElDescriptions, ElDescriptionsItem, ElTag, ElButton, ElTable, ElTableColumn, ElProgress, ElPagination } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectApi } from '@/api/index.js'

// 获取路由参数
const route = useRoute()
const router = useRouter()
const emit = defineEmits(['data-loaded', 'project-action'])

// 接收配置参数
const props = defineProps({
  title: {
    type: String,
    default: '用户详情'
  },
  subtitle: {
    type: String,
    default: '查看用户详细信息及分配的任务'
  },
  userInfoTitle: {
    type: String,
    default: '用户信息'
  },
  projectListTitle: {
    type: String,
    default: '负责的项目列表'
  },
  taskListTitle: {
    type: String,
    default: '负责的任务列表'
  },
  showProjectList: {
    type: Boolean,
    default: true
  },
  showProjectActions: {
    type: Boolean,
    default: true
  },
  projectActionButtonText: {
    type: String,
    default: '查看子任务'
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  taskColumns: {
    type: Array,
    default: () => [
      { prop: 'taskName', label: '任务名称', minWidth: 200, align: 'center' },
      { prop: 'projectName', label: '所属项目', width: 150, align: 'center' },
      { prop: 'wbsNo', label: 'WBS编码', width: 120, align: 'center' },
      { prop: 'owner', label: '任务负责人', width: 120, align: 'center' },
      { prop: 'planStart', label: '计划开始时间', width: 150, align: 'center' },
      { prop: 'planEnd', label: '计划结束时间', width: 150, align: 'center' },
      { prop: 'actual_start_date', label: '实际开始时间', width: 150, align: 'center' },
      { prop: 'actual_end_date', label: '实际结束时间', width: 150, align: 'center' },
      { prop: 'progress', label: '任务进度', width: 120, align: 'center', type: 'progress' },
      { prop: 'status', label: '任务状态', width: 120, align: 'center', type: 'tag', getTagType: (status) => getStatusTagType(status) }
    ]
  },
  userFields: {
    type: Object,
    default: () => ({
      nameLabel: '姓名',
      positionLabel: '职位',
      departmentLabel: '部门',
      contactLabel: '联系方式',
      countLabel: '负责项目数',
      rateLabel: '完成率'
    })
  },
  apiFunctions: {
    type: Object,
    required: true
  }
})

// 当前时间状态
const currentTime = ref('')
const loading = ref(false)

// 用户信息状态
const userInfo = ref(null)

// 项目和任务数据状态
const projects = ref([])
const tasks = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)

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

// 获取用户详情
const fetchUserDetails = async () => {
  loading.value = true
  try {
    const userName = route.params.user
    if (!userName) {
      console.error('未找到用户名')
      return
    }
    
    // 获取项目详情
    const projectsResponse = await props.apiFunctions.projects()
    if (projectsResponse) {
      // 根据用户名筛选项目
      const filteredProjects = projectsResponse.filter(project => 
        project.project_manager === userName || 
        project.task_owner === userName
      )
      projects.value = filteredProjects
    }
    
    // 获取任务列表
    // 并行获取任务数据和总数
    const [tasksResponse, countResponse] = await Promise.all([
      props.apiFunctions.tasks(userName, {
        page: currentPage.value,
        limit: pageSize.value
      }),
      props.apiFunctions.tasksCount?.(userName) || Promise.resolve(null)
    ])
    
    if (tasksResponse) {
      let tasksData = []
      let totalCount = 0
      
      if (Array.isArray(tasksResponse)) {
        tasksData = tasksResponse
        // 使用获取到的总数，或者fallback到数组长度
        totalCount = countResponse !== null ? countResponse : tasksResponse.length
      } else {
        // 如果是对象，通常包含数据和总数
        tasksData = tasksResponse.data || tasksResponse.items || []
        totalCount = tasksResponse.total || tasksResponse.count || tasksData.length
      }
      
      // 转换任务数据格式以匹配表格期望的字段名
      const formattedTasks = tasksData.map(task => ({
        ...task,
        taskName: task.task_name,
        projectName: task.project_name,
        wbsNo: task.wbs_code,
        owner: task.task_owner,
        planStart: task.planned_start_date,
        planEnd: task.planned_end_date,
        status: task.task_status
      }))
      
      tasks.value = formattedTasks
      totalItems.value = totalCount
      
      // 设置用户信息（从第一个任务中获取）
      if (formattedTasks.length > 0) {
        const firstTask = formattedTasks[0]
        userInfo.value = {
          name: firstTask.owner || userName,
          position: props.userFields.positionLabel || '项目成员',
          department: props.userFields.departmentLabel || '相关部门',
          contact: props.userFields.contactLabel || '邮箱或电话',
          projectCount: filteredProjects.length,
          completionRate: calculateCompletionRate(formattedTasks)
        }
      }
    }
    
    emit('data-loaded', { projects: projects.value, tasks: tasks.value })
  } catch (error) {
    console.error('获取用户详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算完成率
const calculateCompletionRate = (tasks) => {
  if (!tasks || tasks.length === 0) return 0
  const completed = tasks.filter(task => 
    task.status === '已完成' || task.status === '已验收' || task.status === '完成'
  ).length
  return Math.round((completed / tasks.length) * 100)
}

// 获取项目状态标签类型
const getProjectStatusTagType = (status) => {
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
    case '已结项':
      return 'success'
    default:
      return 'info'
  }
}

// 获取分类标签类型
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
    case '已验收':
    case 'accepted':
      return 'success'
    default:
      return 'info'
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchUserDetails()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchUserDetails()
}

// 项目操作处理
const onProjectAction = (project) => {
  emit('project-action', project)
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 初始化数据
onMounted(async () => {
  // 更新当前时间
  updateTime()
  // 每秒更新一次时间
  setInterval(updateTime, 1000)

  // 获取用户详情
  await fetchUserDetails()
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