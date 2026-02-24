<template>
  <div class="abnormal-task-detail">
    <el-page-header @back="goBack" :content="`${ownerName} - 异常任务详情`">
    </el-page-header>
    
    <el-card class="detail-card">
      <template #header>
        <div class="card-header">
          <span>异常任务分类详情</span>
          <el-button 
            type="primary" 
            size="small" 
            @click="refreshData"
            :loading="loading"
          >
            刷新数据
          </el-button>
        </div>
      </template>
      
      <!-- 统计概览 -->
      <div class="stats-overview">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-label">首个异常节点</div>
              <div class="stat-value first-abnormal">{{ firstAbnormalCount }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-label">进度推迟</div>
              <div class="stat-value delayed-progress">{{ delayedProgressCount }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-label">异常任务总计</div>
              <div class="stat-value total">{{ totalCount }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <!-- 任务列表 -->
      <div class="task-list-section">
        <h3>详细任务列表</h3>
        <el-table 
          :data="taskList" 
          border 
          style="width: 100%" 
          v-loading="loading"
          :row-class-name="tableRowClassName"
        >
          <el-table-column prop="projectName" label="项目名称" min-width="120" fixed="left">
          </el-table-column>
          <el-table-column prop="taskName" label="任务名称" min-width="150">
          </el-table-column>
          <el-table-column prop="wbsNo" label="WBS编码" width="100">
          </el-table-column>
          <el-table-column prop="abnormal_type" label="异常类型" width="120" align="center">
            <template #default="scope">
              <el-tag 
                :type="scope.row.abnormal_type_en === 'first_abnormal' ? 'danger' : 'warning'"
                effect="dark"
              >
                {{ scope.row.abnormal_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="planStart" label="计划开始" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.planStart) }}
            </template>
          </el-table-column>
          <el-table-column prop="planEnd" label="计划结束" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.planEnd) }}
            </template>
          </el-table-column>
          <el-table-column prop="actual_start_date" label="实际开始" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.actual_start_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="actual_end_date" label="实际结束" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.actual_end_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="80" align="center">
            <template #default="scope">
              <el-progress 
                :percentage="Math.round(scope.row.progress)" 
                :stroke-width="10"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template #default="scope">
              {{ formatDateTime(scope.row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { projectApi } from '../api';

const route = useRoute();
const router = useRouter();

// 响应式数据
const ownerName = ref('');
const taskList = ref([]);
const loading = ref(false);

// 计算属性
const firstAbnormalCount = computed(() => {
  return taskList.value.filter(task => task.abnormal_type_en === 'first_abnormal').length;
});

const delayedProgressCount = computed(() => {
  return taskList.value.filter(task => task.abnormal_type_en === 'delayed_progress').length;
});

const totalCount = computed(() => {
  return taskList.value.length;
});

// 方法
const goBack = () => {
  router.back();
};

const refreshData = async () => {
  await loadTaskDetail();
};

const loadTaskDetail = async () => {
  try {
    loading.value = true;
    const response = await projectApi.getAbnormalTaskDetailByOwner(ownerName.value);
    
    if (Array.isArray(response)) {
      taskList.value = response;
      console.log(`加载到 ${response.length} 个异常任务`);
    } else {
      taskList.value = [];
      console.warn('API返回的数据格式不正确');
    }
  } catch (error) {
    console.error('加载异常任务详情失败:', error);
    ElMessage.error('加载数据失败，请稍后重试');
    taskList.value = [];
  } finally {
    loading.value = false;
  }
};

const tableRowClassName = ({ row }) => {
  if (row.abnormal_type_en === 'first_abnormal') {
    return 'first-abnormal-row';
  } else if (row.abnormal_type_en === 'delayed_progress') {
    return 'delayed-progress-row';
  }
  return '';
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
  } catch (error) {
    return dateString;
  }
};

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-';
  try {
    const date = new Date(dateTimeString);
    return date.toLocaleString('zh-CN');
  } catch (error) {
    return dateTimeString;
  }
};

// 生命周期
onMounted(() => {
  ownerName.value = route.params.ownerName || '';
  if (ownerName.value) {
    loadTaskDetail();
  } else {
    ElMessage.error('未指定负责人信息');
    router.back();
  }
});
</script>

<style scoped>
.abnormal-task-detail {
  padding: 20px;
}

.detail-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-overview {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-value.first-abnormal {
  color: #f56c6c;
}

.stat-value.delayed-progress {
  color: #e6a23c;
}

.stat-value.total {
  color: #409eff;
}

.task-list-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

/* 表格行样式 */
:deep(.first-abnormal-row) {
  background-color: #fef0f0;
}

:deep(.delayed-progress-row) {
  background-color: #fdf6ec;
}

:deep(.first-abnormal-row:hover) {
  background-color: #fde2e2 !important;
}

:deep(.delayed-progress-row:hover) {
  background-color: #fce6ce !important;
}
</style>