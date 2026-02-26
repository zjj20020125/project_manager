<template>
  <el-container style="height: 100vh;">
    <!-- 顶部标题栏 -->
    <el-header style="background-color: #409EFF; color: white; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;">
      <div style="display: flex; align-items: center;">
        <h2 style="margin: 0; font-size: 24px;">项目管理系统</h2>
        <span style="margin-left: 20px; font-size: 14px; opacity: 0.9;">{{ currentTime }}</span>
      </div>
      <div style="display: flex; align-items: center; gap: 20px;">
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          background-color="#409EFF"
          text-color="white"
          active-text-color="#ffd04b"
          @select="handleMenuSelect"
          style="border: none;"
        >
          <el-menu-item index="1">项目管理</el-menu-item>
          <el-menu-item index="2">NCR管理</el-menu-item>
        </el-menu>
        <el-button @click="goToNcrManagement" type="primary" style="background-color: #67C23A;">NCR管理</el-button>
      </div>
    </el-header>

    <el-main style="padding: 20px; background-color: #f5f5f5;">
      <!-- 项目统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card shadow="hover" @click="goToProjectStatusDetail('total')" class="clickable-card" style="background: linear-gradient(135deg, #409EFF, #79bbff); color: white;">
            <div class="card-title" style="color: white;">项目总数</div>
            <div class="card-value" style="color: white;">{{ projectStats.totalProjects }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToProjectStatusDetail('not_started')" class="clickable-card" style="background: linear-gradient(135deg, #E6A23C, #f3d19e); color: white;">
            <div class="card-title" style="color: white;">未开始项目</div>
            <div class="card-value" style="color: white;">{{ projectStats.notStartedProjects }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToProjectStatusDetail('ongoing')" class="clickable-card" style="background: linear-gradient(135deg, #67C23A, #b3e19d); color: white;">
            <div class="card-title" style="color: white;">进行中项目</div>
            <div class="card-value" style="color: white;">{{ projectStats.runningProjects }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToProjectStatusDetail('completed')" class="clickable-card" style="background: linear-gradient(135deg, #909399, #c8c9cc); color: white;">
            <div class="card-title" style="color: white;">已结项项目</div>
            <div class="card-value" style="color: white;">{{ projectStats.completedProjects }}个</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 任务统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card shadow="hover" @click="goToMilestoneTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #F56C6C, #fab6b6); color: white;">
            <div class="card-title" style="color: white;">里程碑任务数</div>
            <div class="card-value" style="color: white;">{{ taskStats.milestoneTasks }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToCompletedMilestoneDetail" class="clickable-card" style="background: linear-gradient(135deg, #E6A23C, #f3d19e); color: white;">
            <div class="card-title" style="color: white;">已完成里程碑数</div>
            <div class="card-value" style="color: white;">{{ taskStats.completedMilestones }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToSubTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #409EFF, #a0cfff); color: white;">
            <div class="card-title" style="color: white;">子任务数</div>
            <div class="card-value" style="color: white;">{{ taskStats.subTasks }}个</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" @click="goToAcceptedTaskDetail" class="clickable-card" style="background: linear-gradient(135deg, #6c5ce7, #a29bfe); color: white;">
            <div class="card-title" style="color: white;">已验收任务数</div>
            <div class="card-value" style="color: white;">{{ taskStats.completedTasks }}个</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 项目任务甘特图 -->
      <el-card shadow="hover" margin-bottom="20px">
        <div slot="header" class="card-header">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="flex: 1; text-align: right; font-size: 18px; margin-right: 200px;">{{ selectedProjectName || '项目任务甘特图' }}</span>
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

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 项目类型分布饼图 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span>项目类型分布统计</span>
            </div>
            <div ref="typePieRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 项目来源统计柱状图 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span>项目来源统计</span>
            </div>
            <div ref="sourceBarRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 项目经理负载统计 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span>项目经理负载统计</span>
            </div>
            <div ref="loadBarRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 异常节点负责人统计 -->
        <el-col :span="12">
          <el-card shadow="hover">
            <div slot="header" class="card-header">
              <span>异常节点负责人统计</span>
            </div>
            <el-table 
              :data="abnormalTaskOwnerStats" 
              border 
              style="width: 100%" 
              v-loading="abnormalOwnerStatsLoading"
              height="300"
            >
              <el-table-column prop="owner" label="负责人" width="120" align="center" header-align="center" />
              <el-table-column prop="first_abnormal_count" label="首个异常节点数" width="150" align="center" header-align="center" />
              <el-table-column prop="delayed_progress_count" label="进度推迟数" width="120" align="center" header-align="center" />
              <el-table-column prop="total_count" label="合计" width="80" align="center" header-align="center" />
              <el-table-column label="操作" width="100" align="center" header-align="center">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewOwnerDetail(scope.row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <!-- 项目进度明细 -->
      <el-card shadow="hover" style="margin-top: 20px;">
        <div slot="header" class="card-header">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; flex: 1; text-align: center;">项目进度明细</span>
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
          <el-table-column prop="project_id" label="项目编号" width="100" align="center" header-align="center" />
          <el-table-column prop="project_name" label="项目名称" min-width="200" align="center" header-align="center" show-overflow-tooltip />
          <el-table-column prop="project_manager" label="项目经理" width="120" align="center" header-align="center" />
          <el-table-column prop="start_date" label="计划开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="end_date" label="计划结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_start_date" label="实际开始时间" width="150" align="center" header-align="center" />
          <el-table-column prop="actual_end_date" label="实际结束时间" width="150" align="center" header-align="center" />
          <el-table-column prop="progress" label="项目进度" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-progress :percentage="Number(scope.row.progress || 0)" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="项目状态" width="120" align="center" header-align="center">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center" header-align="center" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="viewProjectSubtasks(scope.row)">查看子任务</el-button>
              <el-button type="warning" size="small" @click="modifyProject(scope.row)">修改</el-button>
              <el-button type="danger" size="small" @click="deleteProject(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 导出对话框 -->
      <el-dialog v-model="exportDialogVisible" title="导出项目数据" width="400px">
        <el-radio-group v-model="exportType">
          <el-radio label="selected">导出选中项目</el-radio>
          <el-radio label="all">导出所有项目</el-radio>
        </el-radio-group>
        <template #footer>
          <el-button @click="exportDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleExport">确定</el-button>
        </template>
      </el-dialog>

      <!-- 导入对话框 -->
      <el-dialog v-model="importDialogVisible" title="导入项目数据" width="500px">
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="[]"
          accept=".xlsx,.xls"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传xlsx/xls文件，且不超过10MB
            </div>
          </template>
        </el-upload>
        <template #footer>
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleImport" :loading="uploadLoading">确定导入</el-button>
        </template>
      </el-dialog>

      <!-- 删除确认对话框 -->
      <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px">
        <p>确定要删除项目 "{{ projectToDelete?.project_name }}" 吗？</p>
        <template #footer>
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">确定删除</el-button>
        </template>
      </el-dialog>

      <!-- 修改项目对话框 -->
      <el-dialog v-model="modifyDialogVisible" title="修改项目信息" width="600px">
        <el-form 
          ref="modifyFormRef" 
          :model="modifyFormData" 
          label-width="120px"
          :rules="modifyRules"
        >
          <el-form-item label="项目名称" prop="project_name">
            <el-input v-model="modifyFormData.project_name" />
          </el-form-item>
          <el-form-item label="项目经理" prop="project_manager">
            <el-input v-model="modifyFormData.project_manager" />
          </el-form-item>
          <el-form-item label="计划开始时间" prop="start_date">
            <el-date-picker
              v-model="modifyFormData.start_date"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="计划结束时间" prop="end_date">
            <el-date-picker
              v-model="modifyFormData.end_date"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="项目状态" prop="status">
            <el-select v-model="modifyFormData.status" placeholder="请选择状态">
              <el-option label="未开始" value="未开始" />
              <el-option label="进行中" value="进行中" />
              <el-option label="已完成" value="已完成" />
              <el-option label="已结项" value="已结项" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目进度" prop="progress">
            <el-slider v-model="modifyFormData.progress" :max="100" show-input />
          </el-form-item>
          <el-form-item label="预算(万元)" prop="budget">
            <el-input-number v-model="modifyFormData.budget" :min="0" controls-position="right" />
          </el-form-item>
          <el-form-item label="实际成本(万元)" prop="actual_cost">
            <el-input-number v-model="modifyFormData.actual_cost" :min="0" controls-position="right" />
          </el-form-item>
          <el-form-item label="备注" prop="remarks">
            <el-input v-model="modifyFormData.remarks" type="textarea" />
          </el-form-item>
          <el-form-item label="修改人" prop="modifier_name">
            <el-input v-model="modifyFormData.modifier_name" />
          </el-form-item>
          <el-form-item label="修改说明" prop="remarks_for_modification">
            <el-input v-model="modifyFormData.remarks_for_modification" type="textarea" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="modifyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmModify" :loading="modifyLoading">确定修改</el-button>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import * as echarts from 'echarts'
import { ElContainer, ElHeader, ElMain, ElRow, ElCol, ElCard, ElMenu, ElMenuItem, ElTable, ElTableColumn, ElTag, ElProgress, ElMessage, ElLoading, ElMessageBox, vLoading, ElButton, ElDialog, ElRadio, ElRadioGroup, ElAlert, ElUpload, ElForm, ElFormItem, ElInput, ElDatePicker, ElSelect, ElOption, ElSlider, ElInputNumber } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { useRouter } from 'vue-router'
import { projectApi } from '../api/index.js'
import 'element-plus/dist/index.css'

const router = useRouter()

// 当前显示的视图
const currentView = ref('project')

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

// 导航激活项
const activeMenu = ref('1')

// 加载状态
const tableLoading = ref(false)

// 数据状态
const projectStats = reactive({
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

// 项目详细数据状态
const projectDetails = ref([])
const projectDetailsLoading = ref(false)
const projectCategoryStats = ref({
  total_projects: 0,
  not_started_projects: 0,
  ongoing_projects: 0,
  completed_projects: 0
})

// 任务表格数据
const taskTableData = ref([])

// 异常节点负责人统计相关
const abnormalTaskOwnerStats = ref([])
const abnormalOwnerStatsLoading = ref(false)

// 项目选择相关
const selectedProjectId = ref('')
const selectedProjectName = ref('项目任务甘特图')
const projectOptions = ref([])

// 导入导出相关
const exportDialogVisible = ref(false)
const importDialogVisible = ref(false)
const exportType = ref('selected')
const multipleSelection = ref([])
const selectedFile = ref(null)
const uploadRef = ref(null)
const uploadLoading = ref(false)

// 删除相关
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const projectToDelete = ref(null)

// 修改项目相关状态
const modifyDialogVisible = ref(false)
const modifyLoading = ref(false)
const projectToModify = ref(null)
const modifyFormRef = ref()
const modifyFormData = ref({
  project_name: '',
  project_manager: '',
  start_date: '',
  end_date: '',
  status: '',
  progress: 0,
  budget: 0,
  actual_cost: 0,
  remarks: '',
  modifier_name: '',
  remarks_for_modification: ''
})

// 任务状态对应的标签类型
const statusTagType = {
  '未开始': 'warning',
  '进行中': 'info',
  '已完成': 'success',
  '已验收': 'primary',
  '已结项': 'success'
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

// 修改表单验证规则
const modifyRules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  project_manager: [{ required: true, message: '请输入项目经理', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择计划开始时间', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择计划结束时间', trigger: 'change' }],
  status: [{ required: true, message: '请选择项目状态', trigger: 'change' }],
  progress: [{ required: true, message: '请设置项目进度', trigger: 'change' }],
  modifier_name: [{ required: true, message: '请输入修改人姓名', trigger: 'blur' }]
}

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

// 获取项目列表用于下拉选择
const fetchProjectsList = async () => {
  try {
    const projectsRes = await projectApi.getProjectsList()
    if (projectsRes) {
      projectOptions.value = projectsRes
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 初始化项目类型分布饼图
const initTypePie = async () => {
  try {
    const data = await projectApi.getChartData();
    const typeData = data?.type_pie || [];
    
    if (!typePieRef.value) {
      console.error('Type pie chart container not found');
      return;
    }
    
    if (typePieChart) {
      typePieChart.dispose();
    }
    
    typePieChart = echarts.init(typePieRef.value);
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 10,
        data: typeData.map(item => item.name)
      },
      series: [
        {
          name: '项目类型',
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['60%', '50%'],
          data: typeData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
    
    typePieChart.setOption(option);
    
    // 添加点击事件监听
    typePieChart.on('click', function(params) {
      console.log('饼图点击事件:', params);
      // 根据点击的项目类型跳转到相应的详情页面
      const typeName = params.name;
      router.push({ 
        name: 'ProjectStatusDetail', 
        query: { type: typeName } 
      });
    });
  } catch (error) {
    console.error('初始化项目类型分布饼图失败:', error);
  }
}

// 初始化项目来源统计柱状图
const initSourceBar = async () => {
  try {
    const data = await projectApi.getChartData();
    const sourceData = data?.source_bar || [];
    
    if (!sourceBarRef.value) {
      console.error('Source bar chart container not found');
      return;
    }
    
    if (sourceBarChart) {
      sourceBarChart.dispose();
    }
    
    sourceBarChart = echarts.init(sourceBarRef.value);
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: [
        {
          type: 'category',
          data: sourceData.map(item => item.name),
          axisTick: { alignWithLabel: true }
        }
      ],
      yAxis: [{ type: 'value' }],
      series: [
        {
          name: '项目数',
          type: 'bar',
          barWidth: '60%',
          data: sourceData.map(item => item.value),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }
      ]
    };
    
    sourceBarChart.setOption(option);
    
    // 添加点击事件监听
    sourceBarChart.on('click', function(params) {
      console.log('柱状图点击事件:', params);
      // 根据点击的项目来源跳转到相应的详情页面
      const sourceName = params.name;
      router.push({ 
        name: 'ProjectStatusDetail', 
        query: { source: sourceName } 
      });
    });
  } catch (error) {
    console.error('初始化项目来源统计柱状图失败:', error);
  }
}

// 初始化项目经理负载统计
const initLoadBar = async () => {
  try {
    const data = await projectApi.getChartData();
    const loadData = data?.load_bar || [];
    
    // 提取项目经理名称和对应的项目数
    const managers = loadData.map(item => item.name);
    const projectCounts = loadData.map(item => item.value);
    
    // 为不同的项目经理设置不同的颜色
    const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
    const coloredLoads = projectCounts.map((count, index) => ({
      value: count,
      itemStyle: { color: colors[index % colors.length] }
    }));
    
    if (!loadBarRef.value) {
      console.error('Load bar chart container not found');
      return;
    }
    
    if (loadBarChart) {
      loadBarChart.dispose();
    }
    
    loadBarChart = echarts.init(loadBarRef.value);
    
    const option = {
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' },
        formatter: (params) => {
          const managerName = params[0].name;
          return `${managerName}<br/>负责项目数: ${params[0].value}`;
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
          name: '项目数',
          type: 'bar',
          data: coloredLoads,
          barWidth: '40%'
        }
      ]
    };
    
    loadBarChart.setOption(option);
    
    // 添加点击事件监听
    loadBarChart.on('click', function(params) {
      console.log('项目经理负载图点击事件:', params);
      // 跳转到项目经理详情页面
      goToProjectManagerDetail(params.name);
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
    console.error('获取异常节点负责人统计失败:', error);
    ElMessage.error('获取异常节点负责人统计失败');
  } finally {
    abnormalOwnerStatsLoading.value = false;
  }
}

// 初始化甘特图
const initGantt = async () => {
  try {
    console.log('=== 开始初始化甘特图 ===');
    
    // 获取任务进度甘特图数据
    const projectName = selectedProjectId.value ? 
      projectOptions.value.find(p => p.project_id === selectedProjectId.value)?.project_name : null;
    
    console.log('请求的项目名称:', projectName);
    
    // 等待API数据获取完成
    console.log('开始调用API...');
    const startTime = Date.now();
    const ganttData = await projectApi.getTaskGanttData(projectName);
    const endTime = Date.now();
    console.log(`API调用耗时: ${endTime - startTime}ms`);
    console.log('API返回的原始数据:', ganttData);
    console.log('数据类型:', typeof ganttData);
    console.log('数据长度:', Array.isArray(ganttData) ? ganttData.length : 'Not an array');
    
    // 确保DOM元素存在
    if (!ganttRef.value) {
      console.error('Gantt chart container not found');
      return;
    }
    
    // 销毁之前的图表实例（如果存在）
    if (ganttChart) {
      // 移除resize监听器
      if (ganttChart._resizeHandler) {
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
      console.log('没有数据，显示空图表');
      return;
    }
    
    console.log('原始甘特图数据:', ganttData);
    
    // 准备数据 - 按照甘特图需求格式化数据
    const validTasks = [];
    
    ganttData.forEach((item, index) => {
      const startDateStr = item.planned_start_date;
      const endDateStr = item.planned_end_date;
      
      // 尝试解析日期字符串
      let startDate, endDate;
      
      if (startDateStr) {
        startDate = new Date(startDateStr);
      }
      if (endDateStr) {
        endDate = new Date(endDateStr);
      }
      
      // 如果其中一个日期为空或无效，尝试用另一个日期代替
      if (!startDate && endDate) {
        startDate = endDate;
      } else if (startDate && !endDate) {
        endDate = startDate;
      } else if (!startDate && !endDate) {
        // 即使没有日期信息，也要添加任务到列表中，但不显示时间区间
        console.info(`任务没有日期信息，将在甘特图中占位: ${item.task_name}`);
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false,
          startDate: null,
          endDate: null,
          duration: 0
        });
        return;
      }
      
      // 检查日期是否有效
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        console.warn(`无效的日期格式: ${item.task_name}, 开始: ${startDateStr}, 结束: ${endDateStr}`);
        validTasks.push({
          index: index,
          taskName: item.task_name,
          projectName: item.project_name,
          hasValidDates: false,
          startDate: null,
          endDate: null,
          duration: 0
        });
        return;
      }
      
      // 确保结束日期不早于开始日期
      if (endDate < startDate) {
        console.warn(`日期顺序错误，已调整: ${item.task_name}, 从 ${startDateStr} 到 ${endDateStr}`);
        [startDate, endDate] = [endDate, startDate];
      }
      
      validTasks.push({
        index: index,
        taskName: item.task_name,
        projectName: item.project_name,
        hasValidDates: true,
        startDate: startDate,
        endDate: endDate,
        duration: (endDate - startDate) / (1000 * 60 * 60 * 24)
      });
    });
    
    console.log('处理后的有效任务:', validTasks);
    
    // 如果处理后的数据为空，显示提示
    if (validTasks.length === 0) {
      ganttChart.setOption({
        title: {
          text: '没有有效数据可以显示',
          left: 'center',
          top: 'center'
        }
      });
      return;
    }
    
    // 为每个任务计算起始和结束时间的数值
    const taskNames = validTasks.map(task => task.taskName);
    
    // 计算X轴范围
    const validTasksWithDates = validTasks.filter(task => task.hasValidDates);
    
    let earliestStartDate, latestEndDate;
    
    if (validTasksWithDates.length > 0) {
      earliestStartDate = new Date(Math.min(...validTasksWithDates.map(task => task.startDate.getTime())));
      latestEndDate = new Date(Math.max(...validTasksWithDates.map(task => task.endDate.getTime())));
    } else {
      earliestStartDate = new Date();
      latestEndDate = new Date();
      earliestStartDate.setDate(earliestStartDate.getDate() - 7);
      latestEndDate.setDate(latestEndDate.getDate() + 7);
    }
    
    const adjustedMinTime = earliestStartDate.getTime();
    const adjustedMaxTime = latestEndDate.getTime();
    const timeRange = adjustedMaxTime - adjustedMinTime;
    const marginTime = timeRange * 0.1;
    
    const finalMinTime = adjustedMinTime - marginTime;
    const finalMaxTime = adjustedMaxTime + marginTime;
    
    console.log('最早开始时间:', earliestStartDate);
    console.log('最晚结束时间:', latestEndDate);
    console.log('X轴范围设置为:', {
      min: new Date(finalMinTime),
      max: new Date(finalMaxTime)
    });
    
    const allDatesInSameYear = earliestStartDate.getFullYear() === latestEndDate.getFullYear();
    console.log('所有日期是否在同一年:', allDatesInSameYear);
    
    // 构建图表选项
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: function(params) {
          const task = validTasks[params.dataIndex];
          if (task) {
            return `
              <div>项目：${task.projectName}</div>
              <div>任务：${task.taskName}</div>
              <div>开始时间：${task.startDate ? task.startDate.toLocaleDateString() : '无'}</div>
              <div>结束时间：${task.endDate ? task.endDate.toLocaleDateString() : '无'}</div>
              <div>持续时间：${Math.round(task.duration)} 天</div>
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
              return `${month}-${day}`;
            } else {
              return `${year}-${month}-${day}`;
            }
          }
        },
        splitLine: { show: true }
      },
      yAxis: {
        type: 'category',
        data: taskNames,
        axisLabel: { 
          interval: 0, 
          fontSize: 12
        },
        inverse: true,
        splitLine: { show: true }
      },
      series: [{
        name: '任务时间范围',
        type: 'custom',
        renderItem: function(params, api) {
          const task = validTasks[params.dataIndex];
          if (!task) return;
          
          if (!task.hasValidDates || !task.startDate || !task.endDate) {
            const y = api.coord([0, params.dataIndex])[1];
            const height = api.size([0, 1])[1] * 0.6;
            
            return {
              type: 'rect',
              shape: {
                x: api.coord([Date.now(), params.dataIndex])[0],
                y: y - height / 2,
                width: 1,
                height: height
              },
              style: api.style({
                fill: '#cccccc'
              })
            };
          }
          
          const xStart = api.coord([task.startDate.getTime(), params.dataIndex])[0];
          const xEnd = api.coord([task.endDate.getTime(), params.dataIndex])[0];
          const y = api.coord([0, params.dataIndex])[1];
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
        data: validTasks.map(task => task.hasValidDates ? 1 : 0)
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
}

// 菜单选择处理
const handleMenuSelect = (index) => {
  activeMenu.value = index;
  if (index === '2') {
    router.push('/v1/ncr-dashboard');
  }
}

// 跳转到NCR管理
const goToNcrManagement = () => {
  router.push('/v1/ncr-dashboard');
}

// 跳转到项目状态详情
const goToProjectStatusDetail = (status) => {
  router.push({ 
    name: 'ProjectStatusDetail', 
    query: { status: status } 
  });
}

// 跳转到里程碑任务详情
const goToMilestoneTaskDetail = () => {
  router.push('/milestone-task-detail');
}

// 跳转到已完成里程碑详情
const goToCompletedMilestoneDetail = () => {
  router.push('/completed-milestone-detail');
}

// 跳转到子任务详情
const goToSubTaskDetail = () => {
  router.push('/sub-task-detail');
}

// 跳转到已验收任务详情
const goToAcceptedTaskDetail = () => {
  router.push('/accepted-task-detail');
}

// 跳转到项目经理详情
const goToProjectManagerDetail = (managerName) => {
  router.push({ 
    name: 'ProjectManagerDetail', 
    params: { manager: encodeURIComponent(managerName) } 
  });
}

// 查看负责人详情
const viewOwnerDetail = (row) => {
  router.push({ 
    name: 'AbnormalOwnerDetail', 
    query: { 
      owner: encodeURIComponent(row.owner),
      stats: encodeURIComponent(JSON.stringify({
        first_abnormal_count: row.first_abnormal_count,
        delayed_progress_count: row.delayed_progress_count,
        total_count: row.total_count
      }))
    } 
  });
}

// 查看项目子任务
const viewProjectSubtasks = (project) => {
  const projectId = project.project_id;
  const projectName = project.project_name;
  
  router.push({ 
    name: 'ProjectSubtasksDetail', 
    params: { projectId: projectId },
    query: { projectName: encodeURIComponent(projectName || '') }
  });
}

// 更新甘特图
const updateGanttChart = () => {
  const selectedProject = projectOptions.value.find(p => p.project_id === selectedProjectId.value);
  selectedProjectName.value = selectedProject ? selectedProject.project_name : '项目任务甘特图';
  initGantt();
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  return statusTagType[status] || 'info';
}

// 项目选择变化处理
const handleSelectionChange = (val) => {
  multipleSelection.value = val;
}

// 显示导出对话框
const showExportDialog = () => {
  exportDialogVisible.value = true;
  exportType.value = 'selected';
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true;
}

// 处理文件变化
const handleFileChange = (file) => {
  selectedFile.value = file.raw;
}

// 处理导出
const handleExport = async () => {
  try {
    let projectIds = [];
    
    if (exportType.value === 'selected') {
      if (multipleSelection.value.length === 0) {
        ElMessage.warning('请先选择要导出的项目');
        return;
      }
      projectIds = multipleSelection.value.map(item => item.project_id);
    } else {
      // 导出所有项目
      projectIds = projectDetails.value.map(item => item.project_id);
    }
    
    const blob = await projectApi.exportProjects(projectIds);
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `项目数据_${new Date().toISOString().slice(0, 10)}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    ElMessage.success('导出成功');
    exportDialogVisible.value = false;
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败');
  }
}

// 处理导入
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件');
    return;
  }
  
  uploadLoading.value = true;
  
  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    
    await projectApi.importProjects(formData);
    
    ElMessage.success('导入成功');
    importDialogVisible.value = false;
    
    // 重新加载数据
    await fetchProjectDetails();
  } catch (error) {
    console.error('导入失败:', error);
    ElMessage.error('导入失败');
  } finally {
    uploadLoading.value = false;
  }
}

// 删除项目
const deleteProject = (project) => {
  projectToDelete.value = project;
  deleteDialogVisible.value = true;
}

// 确认删除
const confirmDelete = async () => {
  if (!projectToDelete.value) return;
  
  deleteLoading.value = true;
  
  try {
    await projectApi.deleteProject(projectToDelete.value.project_id);
    ElMessage.success('删除成功');
    deleteDialogVisible.value = false;
    projectToDelete.value = null;
    
    // 重新加载数据
    await fetchProjectDetails();
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败');
  } finally {
    deleteLoading.value = false;
  }
}

// 修改项目
const modifyProject = (project) => {
  projectToModify.value = project;
  modifyFormData.value = {
    project_name: project.project_name || '',
    project_manager: project.project_manager || '',
    start_date: project.start_date || '',
    end_date: project.end_date || '',
    status: project.status || '',
    progress: Number(project.progress) || 0,
    budget: Number(project.budget) || 0,
    actual_cost: Number(project.actual_cost) || 0,
    remarks: project.remarks || '',
    modifier_name: '',
    remarks_for_modification: ''
  };
  modifyDialogVisible.value = true;
}

// 确认修改
const confirmModify = async () => {
  if (!projectToModify.value) return;
  
  // 验证表单
  const valid = await modifyFormRef.value.validate().catch(() => false);
  if (!valid) {
    ElMessage.warning('请填写所有必填项');
    return;
  }
  
  modifyLoading.value = true;
  
  try {
    await projectApi.updateProject(projectToModify.value.project_id, modifyFormData.value);
    ElMessage.success('修改成功');
    modifyDialogVisible.value = false;
    projectToModify.value = null;
    
    // 重新加载数据
    await fetchProjectDetails();
  } catch (error) {
    console.error('修改失败:', error);
    ElMessage.error('修改失败');
  } finally {
    modifyLoading.value = false;
  }
}

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
  // 每秒更新一次时间
  setInterval(updateTime, 1000);
  
  try {
    // 并行获取所有数据
    await Promise.all([
      fetchStats(),
      fetchProjectCategoryStats(),
      fetchProjectDetails(),
      fetchProjectsList(),
      initAbnormalTaskOwnerStats()
    ]);
    
    // 使用setTimeout确保DOM完全渲染后再初始化图表
    setTimeout(() => {
      initTypePie();
      initSourceBar();
      initLoadBar();
    }, 100);
    
    // 甘特图单独延迟初始化
    setTimeout(() => {
      console.log('开始初始化甘特图...');
      initGantt();
    }, 300);
  } catch (error) {
    console.error('初始化页面数据失败:', error);
    ElMessage.error('页面初始化失败，请刷新重试');
  }
  
  window.addEventListener('resize', resizeCharts)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts);
  
  // 清理图表实例
  if (typePieChart) {
    typePieChart.dispose();
  }
  if (sourceBarChart) {
    sourceBarChart.dispose();
  }
  if (loadBarChart) {
    loadBarChart.dispose();
  }
  if (ganttChart) {
    if (ganttChart._resizeHandler) {
      window.removeEventListener('resize', ganttChart._resizeHandler);
    }
    ganttChart.dispose();
  }
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
  height: 500px;
  min-height: 400px;
  overflow: auto;
}
.clickable-card {
  cursor: pointer;
  transition: all 0.3s ease;
}
.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
@media (max-width: 768px) {
  .gantt-container {
    height: 400px;
    min-height: 300px;
  }
}
@media (max-width: 480px) {
  .gantt-container {
    height: 300px;
    min-height: 250px;
  }
}
</style>