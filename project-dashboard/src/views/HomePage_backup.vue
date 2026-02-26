<template>
  <el-container style="min-height: 100vh; padding-top: 120px;">
    <!-- 项目总览标题�?-->
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: linear-gradient(135deg, #409EFF 0%, #4d9eff 100%); padding: 30px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);"> 
      <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="text-align: center;">
          <h1 v-if="currentView !== 'ncr'" style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">工艺技术部 | 新产品项目总览</h1>
          <h1 v-else style="margin: 0; font-size: 32px; color: white; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">NCR管理</h1>
          <p v-if="currentView !== 'ncr'" style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">结构件事业部</p>
          <p v-else style="margin-top: 10px; color: rgba(255, 255, 255, 0.9); font-size: 16px;">NCR流程管理</p>
        </div>
        <div style="color: white; font-size: 18px; position: absolute; right: 0;">
          <div>{{ currentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 顶部导航 -->
    <el-header style="background: #fff; border-bottom: 1px solid #eee; padding: 0 20px; flex-shrink: 0; max-width: 1200px; margin: 0 auto; width: 100%;">
      <el-menu :default-active="activeMenu" mode="horizontal" background-color="#fff" text-color="#333" active-text-color="#409EFF" @select="handleMenuSelect">
        <el-menu-item index="1">项目总览</el-menu-item>
        <el-menu-item index="2">NCR管理</el-menu-item>
      </el-menu>
    </el-header>

    <el-main style="padding: 20px 0; display: flex; justify-content: center;">
      <div style="max-width: 1200px; width: 100%; padding: 0 20px;">
        <!-- 项目分类统计 -->
          <el-card shadow="hover" margin-bottom="20px" style="margin-top: 20px;">
            <div slot="header" class="card-header">项目分类统计</div>
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('total')" class="clickable-card">
                  <div class="card-title">项目总数</div>
                  <div class="card-value" style="color: #f56c6c;">{{ projectCategoryStats.total_projects || 0 }}�</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('not_started')" class="clickable-card">
                  <div class="card-title">未开始项�</div>
                  <div class="card-value" style="color: #E6A23C;">{{ projectCategoryStats.not_started_projects || 0 }}�</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('ongoing')" class="clickable-card">
                  <div class="card-title">进行中项�</div>
                  <div class="card-value" style="color: #409EFF;">{{ projectCategoryStats.ongoing_projects || 0 }}�</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" @click="goToProjectDetail('completed')" class="clickable-card">
                  <div class="card-title">已结项项�</div>
                  <div class="card-value" style="color: #67C23A;">{{ projectCategoryStats.completed_projects || 0 }}�</div>
                </el-card>
              </el-col>
            </el-row>
          </el-card>

          <!-- 图表区域 -->
          <el-row :gutter="20" margin-bottom="20px">
            <!-- 项目状态分布（扇形图） -->
            <el-col :span="8">
              <el-card shadow="hover" class="clickable-card">
                <div slot="header" class="card-header">项目状态分�</div>
                <div ref="typePieRef" class="chart-container"></div>
              </el-card>
            </el-col>

            <!-- 任务负责人统计（表格形式�?-->
            <el-col :span="8">
              <el-card shadow="hover">
                <div slot="header" class="card-header">异常子任务负责人统计</div>
                <el-table 
                  :data="abnormalTaskOwnerStats" 
                  border 
                  style="width: 100%" 
                  height="260"
                  :fit="true"
                  v-loading="abnormalOwnerStatsLoading"
                >
                  <el-table-column prop="owner_name" label="负责人姓名" align="center" header-align="center" width="120">
                    <template #default="scope">
                      <span 
                        @click="goToOwnerTaskDetail(scope.row.owner_name)"
                        style="color: #409EFF; cursor: pointer; text-decoration: underline; display: block; width: 100%;"
                      >
                        {{ scope.row.owner_name }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="first_abnormal_count" label="首个异常节点" align="center" header-align="center" width="120">
                    <template #default="scope">
                      <el-tag type="danger" style="text-align: center">{{ scope.row.first_abnormal_count || 0 }} �?/el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="delayed_progress_count" label="进度推迟" align="center" header-align="center" width="120">
                    <template #default="scope">
                      <el-tag type="warning" style="text-align: center">{{ scope.row.delayed_progress_count || 0 }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="total_count" label="总计" align="center" header-align="center" width="80">
                    <template #default="scope">
                      <strong>{{ scope.row.total_count || 0 }}</strong>
                    </template>
                  </el-table-column>
                  <el-table-column prop="progress_count" label="完成" align="center" header-align="center" width="80">
                    <template #default="scope">
                      <strong>{{ scope.row.progress_count || 0 }}</strong>
                    </template>
                  </el-table-column>
                  <el-table-column prop="delayed_progress_count" label="延迟" align="center" header-align="center" width="80">
                    <template #default="scope">
                      <el-tag type="warning" style="text-align: center">{{ scope.row.delayed_progress_count || 0 }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="total_count" label="总计" align="center" header-align="center" width="80">
                    <template #default="scope">
                      <strong>{{ scope.row.total_count || 0 }}</strong>
                    </template>
                    <template #default="scope">
                      <el-tag type="warning" style="text-align: center">{{ scope.row.delayed_progress_count || 0 }} �?/el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="total_count" label="总计" align="center" header-align="center" width="80">

                    <template #default="scope">
                      <strong>{{ scope.row.total_count || 0 }} �?/strong>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>

            <!-- 项目经理负载（横向柱状图�?-->
            <el-col :span="8">
              <el-card shadow="hover" class="clickable-card">
                <div slot="header" class="card-header">项目经理负载</div>
                <div ref="loadBarRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 任务进度统计 -->
          <el-row :gutter="20" margin-bottom="20px">
            <el-col :span="6">
              <el-card shadow="hover" @click="goToMilestoneTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #74b9ff, #0984e3); color: white;">
                <div class="card-title" style="color: white;">里程碑任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.milestoneTasks }}�</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToCompletedMilestoneTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #00b894, #00a085); color: white;">
                <div class="card-title" style="color: white;">已验收里程碑任务�</div>
                <div class="card-value" style="color: white;">{{ taskStats.completedMilestones }}�</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToSubTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #fdcb6e, #e17055); color: white;">
                <div class="card-title" style="color: white;">子任务任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.subTasks }}�</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card shadow="hover" @click="goToAcceptedTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white;">
                <div class="card-title" style="color: white;">已验收任务数</div>
                <div class="card-value" style="color: white;">{{ taskStats.completedTasks }}�</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 项目任务甘特�?-->
          <el-card shadow="hover" margin-bottom="20px">
            <div slot="header" class="card-header">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="flex: 1; text-align: right; font-size: 18px; margin-right: 200px;">{{ selectedProjectName || '项目任务甘特�? }}</span>
                <el-select v-model="selectedProjectId" placeholder="请选择项目" style="width: 200px;" @change="updateGanttChart">
                  <el-option
                    v-for="item in projectOptions"
                    :key="item.project_id"
                    :label="item.project_name"
                    :value="item.project_id"
                  >
                  </el-option>
                </el-select>
              </div>
            </div>
            <div ref="ganttRef" class="gantt-container"></div>
          </el-card>

          <!-- 任务进度明细�?-->
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 18px; flex: 1; text-align: center;">项目进度明细�?/span>
                <div>
                  <el-button type="primary" size="small" @click="showExportDialog">导出</el-button>
                  <el-button type="success" size="small" @click="showImportDialog">导入</el-button>
                </div>
              </div>
            </div>
            <el-table 
              :data="projectDetails" 
              border 
              style="width: 100%" 
              v-loading="projectDetailsLoading" 
              header-align="center"
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="55" align="center" />
              <el-table-column type="index" label="序号" width="60" align="center" header-align="center" />
              <!-- 隐藏项目编号�?-->
              <el-table-column prop="project_id" label="项目编号" width="100" align="center" header-align="center" v-show="false" />
              <el-table-column 
                prop="project_name" 
                label="项目名称" 
                min-width="200"
                align="center"
                header-align="center"
              >
                <template #default="scope">
                  <span 
                    @click="goToProjectSubtasks(scope.row.project_id, scope.row.project_name)"
                    style="color: #409EFF; cursor: pointer; text-decoration: underline;"
                  >
                    {{ scope.row.project_name }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="project_manager" label="项目经理" width="120" align="center" header-align="center" />
              <el-table-column prop="planned_start_date" label="计划开始时�? width="150" align="center" header-align="center" />
              <el-table-column prop="planned_end_date" label="计划结束时间" width="150" align="center" header-align="center" />
              <el-table-column prop="actual_start_date" label="实际开始时�? width="150" align="center" header-align="center" />
              <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
              <el-table-column prop="project_status" label="项目状�? width="120" align="center" header-align="center" />
              <el-table-column prop="category" label="项目分类" width="120" align="center" header-align="center">
                <template #default="scope">
                  <el-tag :type="getCategoryTagType(scope.row.category)">
                    {{ scope.row.category }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" align="center" header-align="center" />
              <el-table-column label="操作" width="120" align="center" header-align="center">
                <template #default="scope">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="showDeleteDialog(scope.row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 导出选择对话�?-->
          <el-dialog v-model="exportDialogVisible" title="导出项目数据" width="500px">
            <div>
              <p>选择导出方式�?/p>
              <el-radio-group v-model="exportType" style="margin-bottom: 20px;">
                <el-radio label="selected">导出选中项目</el-radio>
                <el-radio label="all">导出全部项目</el-radio>
              </el-radio-group>
              <div v-if="exportType === 'selected'">
                <p>已选中 {{ multipleSelection.length }} 个项�?/p>
                <el-alert
                  v-if="multipleSelection.length === 0"
                  title="请先勾选要导出的项�?
                  type="warning"
                  show-icon
                  :closable="false"
                />
              </div>
            </div>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="exportDialogVisible = false">取消</el-button>
                <el-button 
                  type="primary" 
                  @click="confirmExport" 
                  :disabled="exportType === 'selected' && multipleSelection.length === 0"
                >
                  确认导出
                </el-button>
              </span>
            </template>
          </el-dialog>

          <!-- 导入对话�?-->
          <el-dialog v-model="importDialogVisible" title="导入项目数据" width="500px">
            <div>
              <p>请选择要导入的文件�?/p>
              <el-upload
                class="upload-demo"
                drag
                :action="''"
                :http-request="handleFileUpload"
                :auto-upload="false"
                :show-file-list="true"
                accept=".xlsx,.xls,.csv"
                ref="uploadRef"
                :on-change="onFileChange"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
                <template #tip>
                  <div class="el-upload__tip">支持 .xlsx, .xls, .csv 格式的文�</div>
                </template>
              </el-upload>
            </div>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="importDialogVisible = false">取消</el-button>
                <el-button 
                  type="primary" 
                  @click="submitUpload" 
                  :disabled="!selectedFile || !selectedFile.raw"
                >
                  确认导入
                </el-button>
              </span>
            </template>
          </el-dialog>

          <!-- 编辑项目信息对话�?-->
          <el-dialog v-model="editProjectDialogVisible" title="编辑项目信息" width="500px">
            <el-form :model="projectEditForm" label-width="100px">
              <el-form-item label="项目名称" required>
                <el-input v-model="projectEditForm.project_name" placeholder="请输入项目名�?></el-input>
              </el-form-item>
              <el-form-item label="项目经理">
                <el-input v-model="projectEditForm.project_manager" placeholder="请输入项目经理姓�?></el-input>
              </el-form-item>
            </el-form>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="editProjectDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmEditProject">确认修改</el-button>
              </span>
            </template>
          </el-dialog>

          <!-- 删除确认对话�?-->
          <el-dialog v-model="deleteDialogVisible" title="删除项目确认" width="500px">
            <div v-if="projectsToDelete.length > 0">
              <p>确定要删除以�?{{ projectsToDelete.length }} 个项目吗�?/p>
              <el-table :data="projectsToDelete" border style="width: 100%; margin: 15px 0;" max-height="200">
                <el-table-column prop="project_name" label="项目名称" />
                <el-table-column prop="project_manager" label="项目经理" />
              </el-table>
              <el-alert
                title="注意：删除项目将同时删除该项目的所有相关任务数据，此操作不可恢复！"
                type="warning"
                show-icon
                :closable="false"
              />
            </div>
            <div v-else-if="projectToDelete">
              <p>确定要删除项�?<strong>{{ projectToDelete.project_name }}</strong> 吗？</p>
              <p>项目经理�?strong>{{ projectToDelete.project_manager }}</strong></p>
              <el-alert
                title="注意：删除项目将同时删除该项目的所有相关任务数据，此操作不可恢复！"
                type="warning"
                show-icon
                :closable="false"
                style="margin-top: 15px;"
              />
            </div>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="deleteDialogVisible = false">取消</el-button>
                <el-button 
                  type="danger" 
                  @click="confirmDelete" 
                  :loading="deleteLoading"
                >
                  确认删除
                </el-button>
              </span>
            </template>
          </el-dialog>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import * as echarts from 'echarts'
import { ElContainer, ElHeader, ElMain, ElRow, ElCol, ElCard, ElMenu, ElMenuItem, ElTable, ElTableColumn, ElTag, ElProgress, ElMessage, ElLoading, ElMessageBox, vLoading, ElButton, ElDialog, ElRadio, ElRadioGroup, ElAlert, ElUpload } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { useRouter } from 'vue-router'
import { projectApi } from '../api/index.js'  // 导入API
import 'element-plus/dist/index.css'

const router = useRouter()

// 为了在模板中使用图标，我们需要将其作为组件返�?const setup = () => {
  return {
    UploadFilled,
  }
}

// 当前显示的视�?('project' �?'ncr')
const currentView = ref('project')

// 当前时间状�?const currentTime = ref('')

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

// 导航激活项
const activeMenu = ref('1')

// 加载状�?const tableLoading = ref(false)

// 数据状�?const projectStats = reactive({
  totalProjects: 0,
  notStartedProjects: 0,
  runningProjects: 0,
  completedProjects: 0
})

const taskStats = reactive({
  milestoneTasks: 0,
  completedMilestones: 0,
  subTasks: 0,
  completedTasks: 0
})

// 项目详细数据状�?const projectDetails = ref([])
const projectDetailsLoading = ref(false)
const projectCategoryStats = ref({
  total_projects: 0,
  not_started_projects: 0,
  ongoing_projects: 0,
  completed_projects: 0
})

// 任务表格数据
const taskTableData = ref([])

// 异常节点负责人统计相�?const abnormalTaskOwnerStats = ref([])
const abnormalOwnerStatsLoading = ref(false)

// 项目选择相关
const selectedProjectId = ref('')
const selectedProjectName = ref('项目任务甘特�?)
const projectOptions = ref([])

// 导入导出相关
const exportDialogVisible = ref(false)
const importDialogVisible = ref(false)
const exportType = ref('selected') // 'selected' �?'all'
const multipleSelection = ref([]) // 选中的项�?const selectedFile = ref(null)
const uploadRef = ref(null)
const uploadLoading = ref(false) // 导入加载状�?
// 删除相关
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const projectToDelete = ref(null) // 单个删除的项�?
// 修改项目相关状�?const modifyDialogVisible = ref(false)
const modifyLoading = ref(false)
const projectToModify = ref(null) // 要修改的项目
const modifyFormRef = ref()
const modifyFormData = ref({
  project_name: '',
  project_manager: '',
  start_date: '',
  end_date: '',
  status: '',
  progress: '',
  budget: '',
  actual_cost: '',
  remarks: '',
  modifier_name: '',
  remarks_for_modification: ''
})
const projectsToDelete = ref([]) // 批量删除的项�?
// 在setup函数中返回uploadRef，以便在模板中使�?
// 任务状态对应的标签类型
const statusTagType = {
  '未开�?: 'warning',
  '进行�?: 'info',
  '已完�?: 'success',
  '已验�?: 'primary',
  '已验�?: 'primary'
}

// ECharts实例引用
const typePieRef = ref(null)
const sourceBarRef = ref(null)
const loadBarRef = ref(null)
const ganttRef = ref(null)

// 图表实例对象
let typePieChart = null
let sourceBarChart = null
let loadBarChart = null
let ganttChart = null

// 获取统计数据
const fetchStats = async () => {
  try {
    // 获取项目统计数据
    const statsRes = await projectApi.getProjectStats();
    if (statsRes) {
      projectStats.totalProjects = statsRes.total_projects || 0;
      projectStats.notStartedProjects = statsRes.unstarted_projects || 0;
      projectStats.runningProjects = statsRes.ongoing_projects || 0;
      projectStats.completedProjects = statsRes.completed_projects || 0;
    }
    
    // 获取任务统计数据
    const taskStatsRes = await projectApi.getTaskStats();
    if (taskStatsRes) {
      taskStats.milestoneTasks = taskStatsRes.total_milestones || 0;
      taskStats.completedMilestones = taskStatsRes.completed_milestones || 0;
      taskStats.subTasks = taskStatsRes.total_subtasks || 0;
      taskStats.completedTasks = taskStatsRes.completed_tasks || 0;
    }
    
    // 获取任务表格数据
    const taskListRes = await projectApi.getTaskList({ page: 1, limit: 10 });
    taskTableData.value = taskListRes?.data || [];
  } catch (error) {
    console.error('获取统计数据失败:', error);
    ElMessage.error('获取统计数据失败');
  }
}

// 获取项目分类统计数据
const fetchProjectCategoryStats = async () => {
  try {
    const statsRes = await projectApi.getProjectCategoryStats()
    if (statsRes) {
      projectCategoryStats.value = statsRes
    }
  } catch (error) {
    console.error('获取项目分类统计数据失败:', error)
    ElMessage.error('获取项目分类统计数据失败')
  }
}

// 获取项目详细分类数据
const fetchProjectDetails = async () => {
  projectDetailsLoading.value = true
  try {
    const detailRes = await projectApi.getProjectsDetail()
    if (detailRes) {
      projectDetails.value = detailRes
    }
  } catch (error) {
    console.error('获取项目详细分类数据失败:', error)
    ElMessage.error('获取项目详细分类数据失败')
  } finally {
    projectDetailsLoading.value = false
  }
}

// 获取项目列表
const fetchProjectsList = async () => {
  try {
    const response = await projectApi.getProjectsList()
    if (response) {
      projectOptions.value = response
      // 如果有项目，默认选中第一个项�?      if (response.length > 0) {
        selectedProjectId.value = response[0].project_id
        selectedProjectName.value = `${response[0].project_name} - 任务甘特图`
        // 更新甘特图以显示第一个项目的数据
        setTimeout(() => {
          initGantt()
        }, 100)
      }
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 更新甘特�?const updateGanttChart = async () => {
  // 根据选中的项目更新标�?  if (selectedProjectId.value) {
    const selectedProject = projectOptions.value.find(p => p.project_id === selectedProjectId.value)
    if (selectedProject) {
      selectedProjectName.value = `${selectedProject.project_name} - 任务甘特图`
    }
  } else {
    selectedProjectName.value = '项目任务甘特�?
  }
  
  // 重新初始化甘特图
  await initGantt()
}

// 获取项目分类标签类型
const getCategoryTagType = (category) => {
  switch (category) {
    case '未开�?:
      return 'warning'
    case '进行�?:
      return 'info'
    case '已结�?:
      return 'success'
    default:
      return 'info'
  }
}

// 跳转到项目详情页�?const goToProjectDetail = (status) => {
  console.log('跳转到项目详情页面，状�?', status);
  // 使用路由跳转到项目状态详情页面，传递状态参�?  router.push({ 
    name: 'ProjectStatusDetail', 
    params: { status: status }
  });
}

// 跳转到任务详情页�?const goToTaskDetail = (taskType) => {
  // 使用路由跳转到任务详情页�?  router.push({ name: 'TaskDetail', query: { type: taskType } })
}

// 跳转到项目子任务详情页面
const goToProjectSubtasks = (projectId, projectName) => {
  // 使用路由跳转到项目子任务详情页面
  router.push({ 
    name: 'ProjectSubtasksDetail', 
    params: { projectId: projectId },
    query: { projectName: encodeURIComponent(projectName || '') }
  })
}

// 跳转到异常子任务负责人详情页�?const goToOwnerTaskDetail = (ownerName) => {
  console.log('点击负责人跳�?', ownerName);
  console.log('当前统计数据:', abnormalTaskOwnerStats.value);
  
  // 查找该负责人的统计信�?  const ownerStat = abnormalTaskOwnerStats.value.find(stat => stat.owner_name === ownerName);
  console.log('找到的统计信�?', ownerStat);
  
  try {
    // 使用完整的路径跳转作为备选方�?    const statsParam = ownerStat ? encodeURIComponent(JSON.stringify(ownerStat)) : '';
    const fullPath = `/abnormal-owner-detail/${encodeURIComponent(ownerName)}?stats=${statsParam}`;
    
    console.log('完整跳转路径:', fullPath);
    window.location.href = fullPath;
    
    // 如果上面的方法不行，再尝试路由跳�?    // router.push({ 
    //   name: 'AbnormalOwnerDetail', 
    //   params: { 
    //     owner: ownerName
    //   },
    //   query: {
    //     stats: ownerStat ? JSON.stringify(ownerStat) : '{}'
    //   }
    // });
    console.log('跳转成功');
  } catch (error) {
    console.error('跳转失败:', error);
  }
}

// 跳转到项目状态详情页�?const goToProjectStatusDetail = (status = null) => {
  console.log('跳转到项目状态详情页面，状�?', status);
  // 使用路由跳转到项目状态详情页面，传递状态参�?  const routeParams = {
    name: 'ProjectStatusDetail'
  };
  
  if (status) {
    routeParams.params = { status: status };
  } else {
    // 如果没有指定状态，默认跳转到总览
    routeParams.params = { status: 'total' };
  }
  
  router.push(routeParams);
}

// 跳转到项目状态的子任务详情页�?const goToProjectStatusSubtasks = (status) => {
  console.log('跳转到项目状态子任务详情页面，状�?', status);
  try {
    // 使用路由跳转到项目状态的子任务详情页面，传递状态参�?    router.push({ 
      name: 'ProjectStatusSubtasksDetail', 
      params: { status: status }
    });
    console.log('子任务详情页面跳转成�?);
  } catch (error) {
    console.error('子任务详情页面跳转失�?', error);
  }
}

// 跳转到项目经理详情页�?const goToProjectManagerDetail = (managerName) => {
  // 使用路由跳转到项目经理详情页�?  router.push({ 
    name: 'ProjectManagerDetail', 
    params: { manager: encodeURIComponent(managerName || '') }
  })
}

// 跳转到里程碑任务详情页面
const goToMilestoneTaskDetail = () => {
  // 使用路由跳转到里程碑任务详情页面
  router.push({ name: 'MilestoneTaskDetail' })
}

// 跳转到已验收里程碑任务详情页�?const goToCompletedMilestoneTaskDetail = () => {
  // 使用路由跳转到已验收里程碑任务详情页�?  router.push({ name: 'CompletedMilestoneTaskDetail' })
}

// 跳转到子任务详情页面
const goToSubTaskDetail = () => {
  // 使用路由跳转到子任务详情页面
  router.push({ name: 'SubTaskDetail' })
}

// 跳转到已验收任务详情页面
const goToAcceptedTaskDetail = () => {
  // 使用路由跳转到已验收任务详情页面
  router.push({ name: 'AcceptedTaskDetail' })
}

// 切换到NCR管理页面
const goToNcr = () => {
  currentView.value = 'ncr';
  activeMenu.value = '2';
}

// 导航到NCR流程�?const goToNcrFlowChart = () => {
  window.location.reload();
}

// 重新初始化图�?const reInitCharts = () => {
  setTimeout(() => {
    initTypePie();
    initSourceBar();
    initLoadBar();
    initGantt();
  }, 100);
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  if (index === '2') {
    // 跳转到新的NCR仪表盘页�?    router.push('/ncr-dashboard');
  } else {
    currentView.value = 'project';
    activeMenu.value = '1';
    // 重新初始化图表以确保它们正确显示
    reInitCharts();
  }
}

// 获取状态文�?const getStatusText = (status) => {
  switch (status) {
    case 'total':
      return '全部';
    case 'not_started':
      return '未开�?;
    case 'ongoing':
      return '进行�?;
    case 'completed':
      return '已结�?;
    default:
      return '';
  }
}

// 调试甘特图数�?const debugGanttData = async () => {
  try {
    const projectName = selectedProjectId.value ? 
      projectOptions.value.find(p => p.project_id === selectedProjectId.value)?.project_name : null;
    
    const ganttData = await projectApi.getTaskGanttData(projectName);
    console.log('甘特图原始数�?', ganttData);
    
    // 检查是否有有效的日期数�?    if (ganttData && ganttData.length > 0) {
      ganttData.forEach((item, index) => {
        console.log(`任务 ${index + 1}:`, {
          task_name: item.task_name,
          project_name: item.project_name,
          planned_start_date: item.planned_start_date,
          planned_end_date: item.planned_end_date,
          start_valid: Boolean(item.planned_start_date),
          end_valid: Boolean(item.planned_end_date)
        });
      });
    } else {
      console.log('没有获取到甘特图数据');
    }
  } catch (error) {
    console.error('调试甘特图数据失�?', error);
  }
}

// 项目选择变化处理
const handleSelectionChange = (val) => {
  multipleSelection.value = val;
};

// 显示导出对话�?const showExportDialog = () => {
  exportDialogVisible.value = true;
  exportType.value = 'selected';
};

// 显示导入对话�?const showImportDialog = () => {
  importDialogVisible.value = true;
};

// 确认导出
const confirmExport = async () => {
  try {
    let projectIds = [];
    
    if (exportType.value === 'all') {
      // 导出所有项�?      projectIds = [];
    } else {
      // 导出选中项目
      if (multipleSelection.value.length === 0) {
        ElMessage.warning('请先选择要导出的项目');
        return;
      }
      projectIds = multipleSelection.value.map(item => item.project_id);
    }
    
    // 调用后端API导出数据
    const response = await projectApi.exportProjects(projectIds);
    
    // 检查响应类�?    if (response instanceof Blob) {
      // 直接处理Blob响应
      const url = window.URL.createObjectURL(response);
      const link = document.createElement('a');
      const fileName = `项目数据_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`;
      
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      
      // 清理临时元素
      link.remove();
      window.URL.revokeObjectURL(url);
    } else {
      // 如果响应不是Blob，可能是错误响应
      throw new Error('导出失败：服务器返回了意外的响应格式');
    }
    
    ElMessage.success('导出成功');
    exportDialogVisible.value = false;
  } catch (error) {
    console.error('导出失败:', error);
    console.error('错误详情:', error.message);
    
    // 尝试获取更详细的错误信息
    if (error.response) {
      // 服务器返回了错误状态码
      ElMessage.error(`导出失败: ${error.response.status} - ${error.response.statusText || '未知错误'}`);
    } else if (error.message) {
      ElMessage.error(`导出失败: ${error.message}`);
    } else {
      ElMessage.error('导出失败，请检查网络连接或联系管理�?);
    }
  }
};

// 显示删除对话框（单个项目�?const showDeleteDialog = (project) => {
  projectToDelete.value = project;
  projectsToDelete.value = [];
  deleteDialogVisible.value = true;
};

// 显示批量删除对话�?const showBatchDeleteDialog = () => {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请先选择要删除的项目');
    return;
  }
  
  projectToDelete.value = null;
  projectsToDelete.value = [...multipleSelection.value];
  deleteDialogVisible.value = true;
};

// 确认删除
const confirmDelete = async () => {
  deleteLoading.value = true;
  try {
    let result;
    
    if (projectsToDelete.value.length > 0) {
      // 批量删除
      const projectIds = projectsToDelete.value.map(p => p.project_id);
      result = await projectApi.batchDeleteProjects(projectIds);
      ElMessage.success(`成功删除 ${result.deleted_projects} 个项目，共删�?${result.deleted_tasks_total} 条任务数据`);
    } else if (projectToDelete.value) {
      // 单个删除
      result = await projectApi.deleteProject(projectToDelete.value.project_id);
      ElMessage.success(`项目 '${result.project_name}' 删除成功，共删除 ${result.deleted_tasks_count} 条任务数据`);
    }
    
    // 关闭对话�?    deleteDialogVisible.value = false;
    
    // 重置删除相关状�?    projectToDelete.value = null;
    projectsToDelete.value = [];
    multipleSelection.value = [];
    
    // 重新获取项目数据以更新列�?    await fetchProjectDetails();
    await fetchProjectCategoryStats();
    
  } catch (error) {
    console.error('删除项目失败:', error);
    if (error.response) {
      ElMessage.error(`删除失败: ${error.response.status} - ${error.response.data?.detail || '未知错误'}`);
    } else if (error.message) {
      ElMessage.error(`删除失败: ${error.message}`);
    } else {
      ElMessage.error('删除失败，请检查网络连接或联系管理�?);
    }
  } finally {
    deleteLoading.value = false;
  }
};

// 显示修改对话�?const showModifyDialog = (row) => {
  projectToModify.value = row;
  // 初始化表单数�?  modifyFormData.value = {
    project_name: row.project_name || '',
    project_manager: row.project_manager || '',
    start_date: row.planned_start_date || '',
    end_date: row.planned_end_date || '',
    status: row.project_status || '',
    progress: row.progress !== undefined ? parseFloat(row.progress) : 0,
    budget: row.budget !== undefined ? parseFloat(row.budget) : 0,
    actual_cost: row.actual_cost !== undefined ? parseFloat(row.actual_cost) : 0,
    remarks: row.remarks || '',
    modifier_name: '',
    remarks_for_modification: ''
  };
  modifyDialogVisible.value = true;
};

// 处理修改关闭
const handleModifyClose = () => {
  modifyDialogVisible.value = false;
  projectToModify.value = null;
  if (modifyFormRef.value) {
    modifyFormRef.value.resetFields();
  }
};

// 确认修改
const confirmModify = async () => {
  if (!modifyFormRef.value) return;
  
  try {
    await modifyFormRef.value.validate();
    modifyLoading.value = true;
    
    // 准备修改数据
    const modifyData = {
      ...modifyFormData.value,
      modifier_ip: '127.0.0.1' // 这里可以获取真实的IP地址
    };
    
    // 调用API修改项目
    const response = await projectApi.updateProject(projectToModify.value.project_id, modifyData);
    
    if (response.success) {
      ElMessage.success('项目修改成功');
      modifyDialogVisible.value = false;
      // 重新加载项目数据
      await fetchProjectDetails();
    } else {
      ElMessage.error(response.message || '修改失败');
    }
  } catch (error) {
    console.error('修改项目失败:', error);
    ElMessage.error('修改项目失败: ' + (error.message || '未知错误'));
  } finally {
    modifyLoading.value = false;
  }
};

// 提交上传
const submitUpload = async () => {
  console.log('开始提交上传，selectedFile:', selectedFile.value);
  
  if (selectedFile.value && selectedFile.value.raw) {
    uploadLoading.value = true;
    try {
      console.log('调用handleFileUpload，文件信�?', {
        name: selectedFile.value.name,
        size: selectedFile.value.size,
        type: selectedFile.value.type
      });
      
      // 直接调用处理文件上传函数，使用文件的原始对象
      await handleFileUpload({ file: selectedFile.value.raw });
    } catch (error) {
      console.error('submitUpload过程中发生错�?', error);
      ElMessage.error('上传过程中发生错�? ' + error.message);
    } finally {
      uploadLoading.value = false;
    }
  } else {
    ElMessage.warning('请先选择要导入的文件');
    console.log('没有选中的文�?', selectedFile.value);
  }
};

// 文件选择变化处理
const onFileChange = (file, fileList) => {
  console.log('文件选择变化:', file, fileList);
  selectedFile.value = file;
  
  // 验证文件
  if (file && file.raw) {
    const fileExt = file.name.split('.').pop().toLowerCase();
    if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
      ElMessage.error('仅支�?.xlsx, .xls, .csv 格式的文�?);
      selectedFile.value = null;
      // 清空文件列表
      if (uploadRef.value) {
        uploadRef.value.clearFiles();
      }
      return;
    }
    
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      ElMessage.error('文件大小不能超过50MB');
      selectedFile.value = null;
      if (uploadRef.value) {
        uploadRef.value.clearFiles();
      }
      return;
    }
    
    ElMessage.success(`已选择文件: ${file.name}`);
  }
};

// 处理文件上传
const handleFileUpload = async (options) => {
  const file = options.file;
  let loading = null;
  
  try {
    // 验证文件类型
    const fileExt = file.name.split('.').pop().toLowerCase();
    if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
      ElMessage.error('仅支�?.xlsx, .xls, .csv 格式的文�?);
      return;
    }
    
    // 验证文件大小（限制为50MB�?    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      ElMessage.error('文件大小不能超过50MB');
      return;
    }
    
    // 显示上传进度
    loading = ElLoading.service({
      lock: true,
      text: '文件上传中，请稍�?..',
      background: 'rgba(0, 0, 0, 0.7)'
    });
    
    try {
      // 添加超时控制
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('请求超时')), 30000); // 30秒超�?      });
      
      // 将文件上传到后端
      const formData = new FormData();
      formData.append('file', file);
      formData.append('overwrite', 'false'); // 明确添加overwrite参数
      
      console.log('准备上传文件:', {
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type
      });
      
      // 使用Promise.race实现超时控制
      const response = await Promise.race([
        projectApi.importProjects(formData),
        timeoutPromise
      ]);
      
      // 关闭加载提示
      if (loading) {
        loading.close();
      }
      
      // 检查是否需要用户确认覆�?      if (response && response.needs_confirmation) {
        try {
          // 询问用户是否覆盖现有数据
          const overwriteConfirm = await ElMessageBox.confirm(
            `项目已存�?${response.existing_count} 条任务数据，是否覆盖现有数据？`,
            '数据重复',
            {
              confirmButtonText: '覆盖',
              cancelButtonText: '取消',
              type: 'warning',
              distinguishCancelAndClose: true
            }
          );
          
          if (overwriteConfirm === 'confirm') {
            // 用户选择覆盖，重新调用API并启用覆盖选项
            const overwriteLoading = ElLoading.service({
              lock: true,
              text: '正在覆盖数据...',
              background: 'rgba(0, 0, 0, 0.7)'
            });
            
            try {
              const overwriteFormData = new FormData();
              overwriteFormData.append('file', file);
              overwriteFormData.append('overwrite', 'true'); // 启用覆盖
              
              const overwriteResponse = await projectApi.importProjects(overwriteFormData);
              overwriteLoading.close();
              ElMessage.success(`${file.name} 导入成功�?{overwriteResponse.message}`);
            } catch (overwriteError) {
              overwriteLoading.close();
              throw overwriteError;
            }
          } else {
            ElMessage.info('导入已取�?);
            return;
          }
        } catch (confirmError) {
          // 用户取消或关闭对话框
          if (confirmError === 'cancel' || confirmError === 'close') {
            ElMessage.info('导入已取�?);
            return;
          }
          throw confirmError;
        }
      } else {
        // 正常导入成功
        ElMessage.success(`${file.name} 导入成功�?{response.message}`);
      }
      
      // 关闭对话�?      importDialogVisible.value = false;
      
      // 重置文件选择
      selectedFile.value = null;
      
      // 重新获取项目数据以显示更�?      await fetchProjectDetails();
      
    } catch (apiError) {
      // 关闭加载提示
      if (loading) {
        loading.close();
      }
      
      console.error('导入文件失败:', apiError);
      console.error('错误详情:', {
        message: apiError.message,
        response: apiError.response,
        request: apiError.request,
        config: apiError.config
      });
      
      // 提供更详细的错误信息
      let errorMessage = '导入文件失败';
      
      if (apiError.message === '请求超时') {
        errorMessage = '请求超时，请检查网络连接或稍后重试';
      } else if (apiError.response) {
        // 服务器返回了错误响应
        console.log('服务器响应状�?', apiError.response.status);
        console.log('服务器响应数�?', apiError.response.data);
        
        if (apiError.response.data) {
          if (apiError.response.data.detail) {
            errorMessage = `导入失败: ${apiError.response.data.detail}`;
          } else if (apiError.response.data.message) {
            errorMessage = `导入失败: ${apiError.response.data.message}`;
          } else {
            errorMessage = `服务器错�?(${apiError.response.status})`;
          }
        } else {
          errorMessage = `HTTP错误 ${apiError.response.status}: ${apiError.response.statusText}`;
        }
      } else if (apiError.request) {
        // 请求已发出但没有收到响应
        errorMessage = '网络连接失败，请检查网络连�?;
      } else {
        // 请求配置出错
        errorMessage = `请求配置错误: ${apiError.message}`;
      }
      
      ElMessage.error(errorMessage);
    }
  } catch (error) {
    console.error('文件上传失败:', error);
    // 关闭加载提示
    if (loading) {
      loading.close();
    }
    ElMessage.error('文件上传过程中发生错�?);
  }
};

// 验证项目数据格式
const validateProjectData = (data) => {
  if (!Array.isArray(data) || data.length === 0) {
    return false;
  }
  
  // 定义必需的字�?  const requiredFields = ['project_name', 'project_manager'];
  
  for (const row of data) {
    for (const field of requiredFields) {
      if (!(field in row)) {
        return false;
      }
    }
  }
  
  return true;
};

// 监听窗口 resize，自适应图表
const resizeCharts = () => {
  typePieChart?.resize()
  sourceBarChart?.resize()
  loadBarChart?.resize()
  ganttChart?.resize()
}

// 挂载时初始化图表
onMounted(async () => {
  // 更新当前时间
  updateTime();
  // 每秒更新一次时�?  setInterval(updateTime, 1000);
  
  try {
    // 并行获取所有数�?    await Promise.all([
      fetchStats(),
      fetchProjectCategoryStats(),
      fetchProjectDetails(),
      fetchProjectsList(),
      initAbnormalTaskOwnerStats()  // 添加异常节点负责人统计初始化
    ]);
    
    // 使用setTimeout确保DOM完全渲染后再初始化图�?    setTimeout(() => {
      initTypePie();
      initSourceBar();
      initLoadBar();
      initGantt();
    }, 100);
  } catch (error) {
    console.error('初始化页面数据失�?', error);
    ElMessage.error('页面初始化失败，请刷新重�?);
  }
  
  window.addEventListener('resize', resizeCharts)
})

// 卸载时销毁图�?onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (typePieChart) {
    typePieChart.dispose()
    typePieChart = null
  }
  if (sourceBarChart) {
    sourceBarChart.dispose()
    sourceBarChart = null
  }
  if (loadBarChart) {
    loadBarChart.dispose()
    loadBarChart = null
  }
  if (ganttChart) {
    // 移除resize监听�?    if (ganttChart._resizeHandler) {
      window.removeEventListener('resize', ganttChart._resizeHandler);
      ganttChart._resizeHandler = null;
    }
    ganttChart.dispose()
    ganttChart = null
  }
})

// 初始化项目类型饼�?const initTypePie = async () => {
  try {
    // 获取项目状态分布数�?    const pieData = await projectApi.getProjectStatusStats();
    
    // 销毁之前的图表实例（如果存在）
    if (typePieChart) {
      typePieChart.dispose();
      typePieChart = null;
    }
    
    // 确保DOM元素存在
    if (!typePieRef.value) {
      console.error('Type pie chart container not found');
      return;
    }
    
    typePieChart = echarts.init(typePieRef.value)
    
    // 根据状态名称设置颜�?- 遵循项目规范：异常状态使用红�?    const getColorForStatus = (statusName, index) => {
      // 首先检查是否为异常状态，异常状态必须使用红�?      if (statusName.includes('异常')) {
        return '#f56c6c'; // 红色 - 符合项目规范
      }
      
      // 对于非异常状态，使用对比明显的颜色避免相邻数据颜色相�?      const distinctColors = [
        '#4ECDC4', // 青绿�?        '#45B7D1', // 蓝色
        '#96CEB4', // 绿色
        '#FFEAA7', // 浅黄�?        '#DDA0DD', // 梅花�?        '#98D8C8', // 薄荷�?        '#F7DC6F', // 浅黄�?        '#BB8FCE', // 浅紫�?        '#85C1E9', // 浅蓝�?        '#5470c6', // 蓝色
        '#91cc75', // 绿色
        '#fac858', // 黄色
        '#73c0de', // 浅蓝�?        '#3ba272', // 深绿�?        '#fc8452'  // 橙色
      ];
      
      // 根据索引循环使用颜色，确保不同状态使用不同颜�?      // 由于异常状态已经占用红色，所以需要调整索�?      const adjustedIndex = statusName.includes('异常') ? 0 : index;
      return distinctColors[adjustedIndex % distinctColors.length];
    };
    
    // 为数据项添加颜色
    const coloredPieData = pieData.map((item, index) => ({
      ...item,
      itemStyle: {
        color: getColorForStatus(item.name, index)
      }
    }));
    
    const option = {
      tooltip: { trigger: 'item' },
      grid: { left: '3%', right: '4%', bottom: '15%', top: '10%' },
      legend: {
        bottom: 10,
        left: 'center',
        itemWidth: 12,
        itemHeight: 12
      },
      series: [
        {
          name: '项目状�?,
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '40%'],
          data: coloredPieData,
          label: { show: false },
          labelLine: { show: false },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    typePieChart.setOption(option)
    
    // 添加点击事件监听
    typePieChart.on('click', async function(params) {
      console.log('扇形图点击事�?', params)
      // 根据点击的扇形图部分传递相应的状态参�?      let status = params.name; // 直接使用扇形图显示的名称
      console.log('点击的状�?', status)
      console.log('准备跳转到ProjectStatusSubtasksDetail页面')
      
      try {
        // 调用新的API接口获取project_tasks表中匹配status的数�?        const projectTasksData = await projectApi.getProjectTasksByStatus(status);
        console.log('从project_tasks表获取的数据:', projectTasksData);
        
        // 将获取到的数据存储到localStorage中，供项目详情页面使�?        localStorage.setItem('projectTasksData', JSON.stringify(projectTasksData));
        localStorage.setItem('clickedStatus', status);
        
        // 根据显示的名称转换为对应的状态参数用于路由跳�?        let statusParam = '';
        switch(status) {
          case '未开�?:
            statusParam = '未开�?;
            break;
          case '进行�?:
            statusParam = '进行�?;
            break;
          case '已完�?:
          case '已验�?:
            statusParam = '已完�?;
            break;
          default:
            statusParam = status; // 保持原始状态名�?        }
        
        console.log('转换后的状态参�?', statusParam);
        // 跳转到项目状态子任务详情页面，传递状态参�?        console.log('执行路由跳转...');
        router.push({ 
          name: 'ProjectStatusSubtasksDetail', 
          params: { status: statusParam } 
        }).then(() => {
          console.log('路由跳转成功');
        }).catch((error) => {
          console.error('路由跳转失败:', error);
        });
      } catch (error) {
        console.error('获取project_tasks数据失败:', error);
        ElMessage.error('获取项目任务数据失败');
      }
    });
  } catch (error) {
    console.error('初始化项目类型饼图失�?', error);
  }
}

// 初始化项目来源柱状图
const initSourceBar = async () => {
  try {
    // 确保DOM元素存在
    if (!sourceBarRef.value) {
      console.error('Source bar chart container not found');
      return;
    }

    // 销毁之前的图表实例（如果存在）
    if (sourceBarChart) {
      sourceBarChart.dispose();
      sourceBarChart = null;
    }

    // 获取图表数据
    const chartData = await projectApi.getChartData();
    const barData = chartData.source_bar || [];
    
    // 解析数据
    const categories = barData.map(item => item.name);
    const values = barData.map(item => item.value);
    
    sourceBarChart = echarts.init(sourceBarRef.value)
    const option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '15%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: {
        type: 'category',
        data: categories
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '项目数量',
          type: 'bar',
          data: values,
          barWidth: '40%',
          itemStyle: { color: '#409EFF' }
        }
      ]
    }
    sourceBarChart.setOption(option)
  } catch (error) {
    console.error('初始化项目来源柱状图失败:', error);
  }
}

// 获取项目经理负载�?const initLoadBar = async () => {
  try {
    // 获取图表数据
    const chartData = await projectApi.getChartData();
    const barData = chartData.load_bar || [];
    
    // 解析数据
    const managers = barData.map(item => item.name);
    const loads = barData.map(item => item.value);
    
    // 为每个经理定义不同的颜色 - 使用更多对比明显的颜�?    const managerColors = [
      '#4ECDC4', // 青绿�?      '#45B7D1', // 蓝色
      '#96CEB4', // 绿色
      '#FFEAA7', // 浅黄�?      '#DDA0DD', // 梅花�?      '#98D8C8', // 薄荷�?      '#F7DC6F', // 浅黄�?      '#BB8FCE', // 浅紫�?      '#85C1E9', // 浅蓝�?      '#5470c6', // 蓝色
      '#91cc75', // 绿色
      '#fac858', // 黄色
      '#73c0de', // 浅蓝�?      '#3ba272', // 深绿�?      '#fc8452', // 橙色
      '#9a60b4', // 紫色
      '#ea7ccc'  // 粉色
    ];
    
    // 为每个经理分配颜�?    const coloredLoads = loads.map((value, index) => ({
      value: value,
      itemStyle: {
        color: managerColors[index % managerColors.length]
      }
    }));
    
    // 销毁之前的图表实例（如果存在）
    if (loadBarChart) {
      loadBarChart.dispose();
      loadBarChart = null;
    }
    
    // 确保DOM元素存在
    if (!loadBarRef.value) {
      console.error('Load bar chart container not found');
      return;
    }
    
    loadBarChart = echarts.init(loadBarRef.value)
    const option = {
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const managerName = params[0].name;
          return `${managerName}<br/>负责任务�? ${params[0].value}`;
        }
      },
      grid: { left: '15%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: managers
      },
      series: [
        {
          name: '项目�?,
          type: 'bar',
          data: coloredLoads,
          barWidth: '40%'
        }
      ]
    }
    loadBarChart.setOption(option)
    
    // 添加点击事件监听
    loadBarChart.on('click', function(params) {
      console.log('项目经理负载图点击事�?', params)
      // 跳转到项目经理详情页�?      goToProjectManagerDetail(params.name);
    });
  } catch (error) {
    console.error('初始化项目经理负载图失败:', error);
  }
}

// 初始化异常节点负责人统计表格
const initAbnormalTaskOwnerStats = async () => {
  abnormalOwnerStatsLoading.value = true;
  try {
    console.log('开始获取异常节点负责人统计...');
    const stats = await projectApi.getAbnormalTaskOwnerStats();
    console.log('异常节点负责人统计API返回数据:', stats);
    abnormalTaskOwnerStats.value = stats;
    console.log('设置后的abnormalTaskOwnerStats:', abnormalTaskOwnerStats.value);
  } catch (error) {
    console.error('获取异常节点负责人统计失�?', error);
    ElMessage.error('获取异常节点负责人统计失�?);
  } finally {
    abnormalOwnerStatsLoading.value = false;
  }
}

// 初始化甘特图
const initGantt = async () => {
  try {
    // 获取任务进度甘特图数�?    const projectName = selectedProjectId.value ? 
      projectOptions.value.find(p => p.project_id === selectedProjectId.value)?.project_name : null;
    
    // 等待API数据获取完成
    const ganttData = await projectApi.getTaskGanttData(projectName);
    
    // 确保DOM元素存在
    if (!ganttRef.value) {
      console.error('Gantt chart container not found');
      return;
    }
    
    // 销毁之前的图表实例（如果存在）
    if (ganttChart) {
      // 移除resize监听�?      if (ganttChart._resizeHandler) {
        window.removeEventListener('resize', ganttChart._resizeHandler);
        ganttChart._resizeHandler = null;
      }
      ganttChart.dispose();
      ganttChart = null;
    }
    
    try {
      ganttChart = echarts.init(ganttRef.value);
      console.log('甘特图初始化成功');
    } catch (initError) {
      console.error('甘特图初始化失败:', initError);
      return;
    }
    
    // 如果没有数据，显示空图表
    if (!ganttData || ganttData.length === 0) {
      ganttChart.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center'
        }
      });
      return;
    }
    
    console.log('原始甘特图数�?', ganttData); // 调试信息
    
    // 准备数据 - 按照甘特图需求格式化数据
    const validTasks = [];
    
    ganttData.forEach((item, index) => {
      const startDateStr = item.planned_start_date;
      const endDateStr = item.planned_end_date;
      
      // 尝试解析日期字符�?      let startDate, endDate;
      
      if (startDateStr) {
        startDate = new Date(startDateStr);
      }
      if (endDateStr) {
        endDate = new Date(endDateStr);
      }
      
      // 如果其中一个日期为空或无效，尝试用另一个日期代�?      if (!startDate && endDate) {
        startDate = endDate;
      } else if (startDate && !endDate) {
        endDate = startDate;
      } else if (!startDate && !endDate) {
        // 即使没有日期信息，也要添加任务到列表中，但不显示时间区间
        console.info(`任务没有日期信息，将在甘特图中占�? ${item.task_name}`);
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false, // 标记为没有有效日�?          startDate: null,
          endDate: null,
          duration: 0
        });
        return; // 继续下一个任�?      }
      
      // 检查日期是否有�?      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        console.warn(`无效的日期格�? ${item.task_name}, 开�? ${startDateStr}, 结束: ${endDateStr}`);
        // 即使日期无效，也要添加任务到列表中，但不显示时间区间
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false, // 标记为没有有效日�?          startDate: null,
          endDate: null,
          duration: 0
        });
        return; // 继续下一个任�?      }
      
      // 确保结束日期不早于开始日期，如果不符合则交换
      if (endDate < startDate) {
        console.warn(`日期顺序错误，已调整: ${item.task_name}, �?${startDateStr} �?${endDateStr}`);
        [startDate, endDate] = [endDate, startDate]; // 交换日期
      }
      
      validTasks.push({
        index: index,
        taskName: item.task_name,
        projectName: item.project_name,
        hasValidDates: true, // 标记为有有效日期
        startDate: startDate,
        endDate: endDate,
        duration: (endDate - startDate) / (1000 * 60 * 60 * 24), // 以天为单�?      });
    });
    
    console.log('处理后的有效任务:', validTasks); // 调试信息
    
    // 如果处理后的数据为空，显示提�?    if (validTasks.length === 0) {
      ganttChart.setOption({
        title: {
          text: '没有有效数据可以显示',
          left: 'center',
          top: 'center'
        }
      });
      return;
    }
    
    // 为每个任务计算起始和结束时间的数值（用于ECharts显示�?    const taskNames = validTasks.map(task => task.taskName);
    
    // 计算X轴范围，使用最早开始时间和最晚结束时间（仅针对有有效日期的任务）
    const validTasksWithDates = validTasks.filter(task => task.hasValidDates);
    
    let earliestStartDate, latestEndDate;
    
    if (validTasksWithDates.length > 0) {
      earliestStartDate = new Date(Math.min(...validTasksWithDates.map(task => task.startDate.getTime())));
      latestEndDate = new Date(Math.max(...validTasksWithDates.map(task => task.endDate.getTime())));
    } else {
      // 如果没有任务有有效日期，使用当前日期范围
      earliestStartDate = new Date();
      latestEndDate = new Date();
      earliestStartDate.setDate(earliestStartDate.getDate() - 7); // 一周前
      latestEndDate.setDate(latestEndDate.getDate() + 7); // 一周后
    }
    
    // 设置X轴的最小值为最早开始时间，最大值为最晚结束时�?    const adjustedMinTime = earliestStartDate.getTime();
    const adjustedMaxTime = latestEndDate.getTime();
    
    // 添加边距（比如增�?0%的时间范围）
    const timeRange = adjustedMaxTime - adjustedMinTime;
    const marginTime = timeRange * 0.1; // 10%的边�?    
    const finalMinTime = adjustedMinTime - marginTime;
    const finalMaxTime = adjustedMaxTime + marginTime;
    
    // 额外的调试信息：显示最早开始时间和最晚结束时�?    console.log('最早开始时�?', earliestStartDate);
    console.log('最晚结束时�?', latestEndDate);
    console.log('X轴范围设置为:', {
      min: new Date(finalMinTime),
      max: new Date(finalMaxTime)
    });
    
    // 检查是否所有日期都在同一年内
    const allDatesInSameYear = earliestStartDate.getFullYear() === latestEndDate.getFullYear();
    console.log('所有日期是否在同一�?', allDatesInSameYear);
    
    // 构建图表选项 - 使用时间轴来精确表示任务时间范围
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: function(params) {
          const task = validTasks[params.dataIndex];
          if (task) {
            return `
              <div>项目�?{task.projectName}</div>
              <div>任务�?{task.taskName}</div>
              <div>开始时间：${task.startDate.toLocaleDateString()}</div>
              <div>结束时间�?{task.endDate.toLocaleDateString()}</div>
              <div>持续时间�?{Math.round(task.duration)} �</div>
            `;
          }
          return '';
        }
      },
      grid: { 
        left: '15%', 
        right: '8%', 
        bottom: '15%', 
        top: '10%',
        containLabel: true 
      },
      xAxis: {
        type: 'time',
        min: finalMinTime,
        max: finalMaxTime,
        axisLabel: { 
          formatter: (val) => {
            const date = new Date(val);
            const year = date.getFullYear();
            const month = String(date.getMonth()+1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            if (allDatesInSameYear) {
              // 如果所有日期都在同一年，只显示月�?              return `${month}-${day}`;
            } else {
              // 如果跨越多个年份，显示年月日
              return `${year}-${month}-${day}`;
            }
          }
        },
        splitLine: { show: true }
      },
      yAxis: {
        type: 'category',
        data: taskNames, // 根据规范，只显示任务名称
        axisLabel: { 
          interval: 0, 
          fontSize: 12 // 适当增大字体大小以提高可读�?        },
        inverse: true,  // 反转Y轴，使最新的任务在上�?        splitLine: { show: true }
      },
      series: [{
        name: '任务时间范围',
        type: 'custom',
        renderItem: function(params, api) {
          const task = validTasks[params.dataIndex];
          if (!task) return;
          
          // 如果任务没有有效日期，则只显示一个点而不显示时间区间
          if (!task.hasValidDates || !task.startDate || !task.endDate) {
            // 获取y轴坐�?            const y = api.coord([0, params.dataIndex])[1];
            const height = api.size([0, 1])[1] * 0.6;
            
            // 返回一个小矩形作为占位�?            return {
              type: 'rect',
              shape: {
                x: api.coord([Date.now(), params.dataIndex])[0], // 使用当前时间作为占位
                y: y - height / 2,
                width: 1, // 很窄的矩�?                height: height
              },
              style: api.style({
                fill: '#cccccc' // 灰色表示无日期信�?              })
            };
          }
          
          // 获取开始和结束时间的x坐标
          const xStart = api.coord([task.startDate.getTime(), params.dataIndex])[0];
          const xEnd = api.coord([task.endDate.getTime(), params.dataIndex])[0];
          
          // 获取y轴坐�?          const y = api.coord([0, params.dataIndex])[1];
          const height = api.size([0, 1])[1] * 0.6;
          
          const width = xEnd - xStart;
          
          return {
            type: 'rect',
            shape: {
              x: xStart,
              y: y - height / 2,
              width: width,
              height: height
            },
            style: api.style({
              fill: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#409EFF' },
                { offset: 1, color: '#1E88E5' }
              ])
            })
          };
        },
        data: validTasks.map(task => task.hasValidDates ? 1 : 0) // 有日期的�?，没有日期的�?作为占位
      }]
    };
    
    ganttChart.setOption(option);
    
    // 为图表添加resize监听
    if (!ganttChart._resizeHandler) {
      ganttChart._resizeHandler = () => {
        ganttChart.resize();
      };
      window.addEventListener('resize', ganttChart._resizeHandler);
    }
    
    console.log('甘特图已渲染完成');
  } catch (error) {
    console.error('初始化甘特图失败:', error);
    
    // 如果有图表实例，显示错误信息
    if (ganttChart) {
      ganttChart.setOption({
        title: {
          text: '图表加载失败',
          left: 'center',
          top: 'center'
        }
      });
    }
  }
};
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
  height: 260px; /* 增加高度以避免重�?*/
}
.gantt-container {
  width: 100%;
  height: 600px;
  min-height: 400px; /* 确保最小高�?*/
  overflow: auto; /* 添加滚动条以防内容超�?*/
}
/* 添加媒体查询以适配不同屏幕尺寸 */
@media (max-width: 768px) {
  .gantt-container {
    height: 400px; /* 在小屏幕上降低高�?*/
    min-height: 300px;
  }
}
@media (max-width: 480px) {
  .gantt-container {
    height: 300px; /* 在更小的屏幕上进一步降低高�?*/
    min-height: 250px;
  }
}
/* 添加可点击卡片样�?*/
.clickable-card {
  cursor: pointer;
  transition: all 0.3s ease;
}
.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
/* 任务负责人统计表格样�?*/
.el-table .el-table__cell {
  text-align: center;
  vertical-align: middle;
  display: table-cell;
}
.el-table .cell {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  height: 100%;
}
.el-table td {
  padding: 0;
  height: 40px;
}
.el-table th {
  padding: 8px 0;
  height: 40px;
}
.el-table--border, .el-table--group {
  border: 1px solid #dfe2e6;
}
.el-table--border::after, .el-table--group::after, .el-table::before {
  background-color: #dfe2e6;
}
.el-table__body-wrapper, .el-table__header-wrapper {
  overflow: hidden;
}
.el-table {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
  </div>
</el-main>
</el-container>
