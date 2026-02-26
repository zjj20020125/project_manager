<template>
  <div class="ncr-dashboard-container">
    <!-- 页面标题和刷新按钮 -->
    <div class="dashboard-header">
      <h1 class="page-title">NCR管理仪表盘</h1>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="refreshAllData" 
          :loading="refreshLoading"
          icon="Refresh"
        >
          刷新数据
        </el-button>
        <el-button 
          type="success" 
          @click="exportData"
          icon="Download"
        >
          导出报表
        </el-button>
      </div>
    </div>

    <!-- 统计概览卡片 -->
    <el-row :gutter="20" class="stats-overview">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#409EFF' }">
              <i class="el-icon-document"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalNcrCount }}</div>
              <div class="stat-label">NCR总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#67C23A' }">
              <i class="el-icon-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#E6A23C' }">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ pendingCount }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#F56C6C' }">
              <i class="el-icon-user"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ activeResponsibleCount }}</div>
              <div class="stat-label">活跃责任人</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要图表区域 -->
    <el-row :gutter="20" class="main-charts">
      <!-- 类型分布饼图 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>NCR类型分布统计</span>
              <el-tag type="primary" size="small">点击查看详情</el-tag>
            </div>
          </template>
          <div ref="typePieRef" class="chart-container" @click="goToTypeDetail"></div>
        </el-card>
      </el-col>

      <!-- 阶段分布饼图 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>NCR发生阶段分布</span>
              <el-tag type="success" size="small">实时数据</el-tag>
            </div>
          </template>
          <div ref="stagePieRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- DQJD和责任分析区域 -->
    <el-row :gutter="20" class="analysis-section">
      <!-- DQJD阶段分布 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>DQJD阶段分布统计</span>
              <el-tag type="warning" size="small">排除已完成</el-tag>
            </div>
          </template>
          <div ref="dqjdBarRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 责任人员分析 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>评审阶段责任人员分布（前5名）</span>
              <el-tag type="danger" size="small">Top 5</el-tag>
            </div>
          </template>
          <div ref="responsibilityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 未评审状态和WCZZ列表 -->
    <el-row :gutter="20" class="secondary-section">
      <!-- 未评审责任人员分布 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>未评审阶段责任人员分布（前15名）</span>
              <el-tag type="info" size="small">实时更新</el-tag>
            </div>
          </template>
          <div ref="unreviewedStagePieRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- WCZZ责任人员列表 -->
      <el-col :span="12">
        <el-card shadow="hover" class="list-card">
          <template #header>
            <div class="card-header">
              <span>WCZZ责任人员统计</span>
              <el-tag type="primary" size="small">{{ wczzListData.length }}人</el-tag>
            </div>
          </template>
          <div class="scroll-list-container">
            <div 
              class="scroll-list-content" 
              :class="{ 'auto-scroll': wczzListData.length > 8 }"
              ref="wczzListRef"
            >
              <div 
                class="list-item" 
                v-for="(item, index) in wczzListData" 
                :key="index"
                @click="filterByResponsible(item.name)"
              >
                <div class="list-item-content">
                  <span class="name">{{ item.name }}</span>
                  <el-progress 
                    :percentage="(item.value / maxWczzValue) * 100" 
                    :stroke-width="8"
                    :show-text="false"
                    class="progress-bar"
                  />
                </div>
                <span class="count">
                  <el-tag type="danger">{{ item.value }}项</el-tag>
                </span>
              </div>
              <!-- 重复列表实现无缝滚动 -->
              <div 
                class="list-item" 
                v-for="(item, index) in wczzListData" 
                :key="`duplicate-${index}`"
                @click="filterByResponsible(item.name)"
              >
                <div class="list-item-content">
                  <span class="name">{{ item.name }}</span>
                  <el-progress 
                    :percentage="(item.value / maxWczzValue) * 100" 
                    :stroke-width="8"
                    :show-text="false"
                    class="progress-bar"
                  />
                </div>
                <span class="count">
                  <el-tag type="danger">{{ item.value }}项</el-tag>
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- NCR详细数据表格 -->
    <el-card shadow="hover" class="detail-table-card">
      <template #header>
        <div class="card-header">
          <span>NCR详细情况展示</span>
          <div class="table-controls">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索NCR编号、产品名称..."
              style="width: 200px; margin-right: 10px;"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <i class="el-icon-search"></i>
              </template>
            </el-input>
            <el-select
              v-model="selectedStage"
              placeholder="筛选阶段"
              style="width: 120px; margin-right: 10px;"
              clearable
              @change="handleFilterChange"
            >
              <el-option
                v-for="stage in stageOptions"
                :key="stage.value"
                :label="stage.label"
                :value="stage.value"
              />
            </el-select>
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="totalItems"
              layout="prev, pager, next, jumper"
              @current-change="handlePageChange"
              small
            />
          </div>
        </div>
      </template>
      <el-table 
        :data="filteredNcrDetails" 
        border 
        style="width: 100%" 
        v-loading="ncrDetailsLoading"
        height="400"
        @row-click="goToNcrDetail"
        highlight-current-row
      >
        <el-table-column prop="process_no" label="NCR编号" width="120" fixed sortable />
        <el-table-column prop="defective_product_name" label="缺陷产品名称" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <span class="clickable-text">{{ scope.row.defective_product_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fsjd" label="发生阶段" width="120" sortable>
          <template #default="scope">
            <el-tag :type="getStageTagType(scope.row.fsjd)">
              {{ scope.row.fsjd }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dqjd" label="当前阶段" width="120" sortable>
          <template #default="scope">
            <el-tag :type="getCurrentStageTagType(scope.row.dqjd)">
              {{ scope.row.dqjd }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="wczz" label="责任人" width="120" show-overflow-tooltip />
        <el-table-column prop="problem_category" label="问题分类" width="120" show-overflow-tooltip />
        <el-table-column prop="review_level" label="评审级别" width="100" sortable>
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.review_level)">
              {{ scope.row.review_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" sortable>
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_date" label="创建日期" width="120" sortable />
        <el-table-column prop="update_time" label="更新时间" width="120" sortable />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="goToNcrDetail(scope.row.process_no)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import * as echarts from 'echarts';
import { 
  ElCard, 
  ElRow, 
  ElCol, 
  ElButton, 
  ElTable, 
  ElTableColumn, 
  ElTag, 
  ElInput, 
  ElSelect, 
  ElOption, 
  ElPagination, 
  ElProgress,
  ElMessage,
  ElMessageBox
} from 'element-plus';
import { projectApi } from '../../api/index.js';
import { useRouter } from 'vue-router';

export default {
  name: 'NcrDashboard',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElButton,
    ElTable,
    ElTableColumn,
    ElTag,
    ElInput,
    ElSelect,
    ElOption,
    ElPagination,
    ElProgress,
    ElMessage,
    ElMessageBox
  },
  setup() {
    const router = useRouter();

    // 响应式数据
    const refreshLoading = ref(false);
    const ncrDetailsLoading = ref(false);
    
    // 图表引用
    const typePieRef = ref(null);
    const stagePieRef = ref(null);
    const dqjdBarRef = ref(null);
    const responsibilityChartRef = ref(null);
    const unreviewedStagePieRef = ref(null);
    const wczzListRef = ref(null);

    // 数据状态
    const ncrDetails = ref([]);
    const filteredNcrDetails = ref([]);
    const typeDistributionData = ref([]);
    const stageDistributionData = ref([]);
    const dqjdData = ref([]);
    const responsibilityData = ref([]);
    const unreviewedStageData = ref([]);
    const wczzListData = ref([]);

    // 分页和筛选
    const currentPage = ref(1);
    const pageSize = ref(20);
    const totalItems = ref(0);
    const searchKeyword = ref('');
    const selectedStage = ref('');

    // 阶段选项
    const stageOptions = ref([
      { label: '生产中', value: '生产中' },
      { label: '检验时', value: '检验时' },
      { label: '安装后', value: '安装后' },
      { label: '使用中', value: '使用中' },
      { label: '运输中', value: '运输中' }
    ]);

    // 图表实例
    let typePieChart = null;
    let stagePieChart = null;
    let dqjdBarChart = null;
    let responsibilityChart = null;
    let unreviewedStagePieChart = null;

    // 计算属性
    const totalNcrCount = computed(() => ncrDetails.value.length);
    const completedCount = computed(() => 
      ncrDetails.value.filter(item => item.status === '已完成').length
    );
    const pendingCount = computed(() => 
      ncrDetails.value.filter(item => item.status === '待处理').length
    );
    const activeResponsibleCount = computed(() => wczzListData.value.length);
    const maxWczzValue = computed(() => {
      if (wczzListData.value.length === 0) return 1;
      return Math.max(...wczzListData.value.map(item => item.value));
    });

    // 方法定义
    const refreshAllData = async () => {
      refreshLoading.value = true;
      try {
        await fetchData();
      } finally {
        refreshLoading.value = false;
      }
    };

    const fetchData = async () => {
      ncrDetailsLoading.value = true;
      try {
        // 并行获取所有数据
        const [
          typeDistResponse,
          stageDistResponse,
          dqjdWczzResponse,
          responsibilityResponse,
          unreviewedResponse,
          ncrListResponse
        ] = await Promise.all([
          projectApi.getNcrTypeDistribution(),
          projectApi.getNcrStageDistribution(),
          projectApi.getDqjdWczzData(),
          projectApi.getResponsibilityAnalysis(),
          projectApi.getUnreviewedStageResponsibility(),
          projectApi.getNcrList({ page: currentPage.value, limit: pageSize.value })
        ]);

        console.log('API响应数据:', {
          typeDistResponse,
          stageDistResponse,
          dqjdWczzResponse,
          responsibilityResponse,
          unreviewedResponse,
          ncrListResponse
        });

        // 处理类型分布数据
        if (Array.isArray(typeDistResponse)) {
          typeDistributionData.value = typeDistResponse;
          initTypePieChart(typeDistResponse);
          console.log('类型分布数据:', typeDistResponse);
        }

        // 处理阶段分布数据
        if (Array.isArray(stageDistResponse)) {
          stageDistributionData.value = stageDistResponse;
          initStagePieChart(stageDistResponse);
          console.log('阶段分布数据:', stageDistResponse);
        }

        // 处理DQJD和WCZZ数据
        if (dqjdWczzResponse && typeof dqjdWczzResponse === 'object') {
          dqjdData.value = Array.isArray(dqjdWczzResponse.dqjdStats) ? dqjdWczzResponse.dqjdStats : [];
          wczzListData.value = Array.isArray(dqjdWczzResponse.wczzStats) ? dqjdWczzResponse.wczzStats : [];
          initDqjdChart(dqjdData.value);
          console.log('DQJD数据:', dqjdData.value);
          console.log('WCZZ数据:', wczzListData.value);
        }

        // 处理责任人员数据
        if (Array.isArray(responsibilityResponse)) {
          responsibilityData.value = responsibilityResponse;
          initResponsibilityChart(responsibilityResponse);
          console.log('责任人员数据:', responsibilityResponse);
        }

        // 处理未评审数据
        if (Array.isArray(unreviewedResponse)) {
          unreviewedStageData.value = unreviewedResponse;
          initUnreviewedStageChart(unreviewedResponse);
          console.log('未评审数据:', unreviewedResponse);
        }

        // 处理NCR列表数据
        if (Array.isArray(ncrListResponse)) {
          ncrDetails.value = ncrListResponse;
          totalItems.value = ncrListResponse.length;
          applyFilters();
          console.log('NCR列表数据:', ncrListResponse);
        }

      } catch (error) {
        console.error('获取NCR数据失败:', error);
        ncrDetailsLoading.value = false;
        
        // 根据错误类型显示不同的提示信息
        if (error.message && (error.message.includes('A listener indicated an asynchronous response') || 
                              error.message.includes('message channel closed') ||
                              error.message.includes('Unchecked runtime.lastError'))) {
          // 对于浏览器扩展干扰错误，只在第一次显示提示
          if (!window.extensionErrorNotified) {
            ElMessage.warning({
              message: '检测到浏览器扩展可能干扰了页面功能，建议临时禁用广告拦截器或隐私保护扩展',
              duration: 5000,
              showClose: true
            });
            window.extensionErrorNotified = true;
            // 1分钟后重置标记，允许再次提示
            setTimeout(() => {
              window.extensionErrorNotified = false;
            }, 60000);
          }
          // 自动重试
          setTimeout(() => {
            fetchData();
          }, 2000);
        } else if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
          ElMessageBox.confirm(
            '网络连接不稳定，是否重新加载数据？',
            '网络错误',
            {
              confirmButtonText: '重新加载',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            fetchData();
          }).catch(() => {
            ElMessage.info('已取消重新加载');
          });
        } else {
          ElMessage.error('数据加载失败，请检查网络连接或稍后重试');
        }
      } finally {
        ncrDetailsLoading.value = false;
      }
    };

    // 图表初始化方法
    const initTypePieChart = (data) => {
      if (!typePieRef.value || !data || data.length === 0) {
        console.warn('类型分布图表数据为空或容器不存在');
        return;
      }
      
      if (typePieChart) {
        typePieChart.dispose();
      }
      
      typePieChart = echarts.init(typePieRef.value);
      
      // 处理数据，确保格式正确
      const chartData = data.map(item => ({
        name: item.name || item.type || '未知',
        value: item.value || item.count || 0
      })).filter(item => item.value > 0);
      
      const option = {
        title: {
          text: 'NCR类型分布',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          type: 'scroll'
        },
        series: [{
          name: 'NCR类型分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          }
        }]
      };
      
      typePieChart.setOption(option);
      console.log('类型分布图表初始化完成，数据:', chartData);
    };

    const initStagePieChart = (data) => {
      if (!stagePieRef.value || !data || data.length === 0) {
        console.warn('阶段分布图表数据为空或容器不存在');
        return;
      }
      
      if (stagePieChart) {
        stagePieChart.dispose();
      }
      
      stagePieChart = echarts.init(stagePieRef.value);
      
      // 处理数据，确保格式正确
      const chartData = data.map(item => ({
        name: item.name || item.stage || '未知阶段',
        value: item.value || item.count || 0
      })).filter(item => item.value > 0);
      
      const option = {
        title: {
          text: 'NCR发生阶段分布',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          type: 'scroll'
        },
        series: [{
          name: '发生阶段分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          }
        }]
      };
      
      stagePieChart.setOption(option);
      console.log('阶段分布图表初始化完成，数据:', chartData);
    };

    const initDqjdChart = (data) => {
      if (!dqjdBarRef.value || !data || data.length === 0) {
        console.warn('DQJD图表数据为空或容器不存在');
        return;
      }
      
      if (dqjdBarChart) {
        dqjdBarChart.dispose();
      }
      
      dqjdBarChart = echarts.init(dqjdBarRef.value);
      
      // 处理数据，确保格式正确
      const chartData = data.map(item => ({
        name: item.name || item.dqjd || '未知阶段',
        value: item.value || item.count || 0
      })).filter(item => item.value > 0);
      
      const option = {
        title: {
          text: 'DQJD阶段分布',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: '{b}: {c}项'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '20%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: chartData.map(item => item.name),
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: { 
          type: 'value',
          name: '数量'
        },
        series: [{
          name: '数量',
          type: 'bar',
          data: chartData.map(item => item.value),
          itemStyle: {
            color: '#409EFF'
          },
          barWidth: '60%'
        }]
      };
      
      dqjdBarChart.setOption(option);
      console.log('DQJD图表初始化完成，数据:', chartData);
    };

    const initResponsibilityChart = (data) => {
      if (!responsibilityChartRef.value || !data || data.length === 0) {
        console.warn('责任人员图表数据为空或容器不存在');
        return;
      }
      
      if (responsibilityChart) {
        responsibilityChart.dispose();
      }
      
      responsibilityChart = echarts.init(responsibilityChartRef.value);
      
      // 处理数据，确保格式正确
      const chartData = data.map(item => ({
        name: item.name || '未知人员',
        value: item.value || item.count || 0
      })).filter(item => item.value > 0);
      
      const option = {
        title: {
          text: '评审阶段责任人员分布(Top 5)',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}项 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          type: 'scroll'
        },
        series: [{
          name: '责任人员分布',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          }
        }]
      };
      
      responsibilityChart.setOption(option);
      console.log('责任人员图表初始化完成，数据:', chartData);
    };

    const initUnreviewedStageChart = (data) => {
      if (!unreviewedStagePieRef.value || !data || data.length === 0) {
        console.warn('未评审阶段图表数据为空或容器不存在');
        return;
      }
      
      if (unreviewedStagePieChart) {
        unreviewedStagePieChart.dispose();
      }
      
      unreviewedStagePieChart = echarts.init(unreviewedStagePieRef.value);
      
      // 处理数据，确保格式正确
      const chartData = data.map(item => ({
        name: item.name || '未知人员',
        value: item.value || item.count || 0
      })).filter(item => item.value > 0);
      
      const option = {
        title: {
          text: '未评审阶段责任人员分布(前15名)',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}项 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          type: 'scroll'
        },
        series: [{
          name: '未评审责任人员',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            show: true,
            formatter: '{b}: {d}%'
          }
        }]
      };
      
      unreviewedStagePieChart.setOption(option);
      console.log('未评审阶段图表初始化完成，数据:', chartData);
    };

    // 筛选和搜索方法
    const applyFilters = () => {
      let result = [...ncrDetails.value];
      
      // 关键词搜索
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase();
        result = result.filter(item =>
          item.process_no?.toLowerCase().includes(keyword) ||
          item.defective_product_name?.toLowerCase().includes(keyword) ||
          item.problem_category?.toLowerCase().includes(keyword)
        );
      }
      
      // 阶段筛选
      if (selectedStage.value) {
        result = result.filter(item => item.fsjd === selectedStage.value);
      }
      
      filteredNcrDetails.value = result;
      totalItems.value = result.length;
    };

    const handleSearch = () => {
      currentPage.value = 1;
      applyFilters();
    };

    const handleFilterChange = () => {
      currentPage.value = 1;
      applyFilters();
    };

    const handlePageChange = (page) => {
      currentPage.value = page;
      fetchData();
    };

    // 跳转方法
    const goToTypeDetail = () => {
      router.push({ name: 'NcrTypeDetail' });
    };

    const goToNcrDetail = (processNo) => {
      if (typeof processNo === 'object') {
        processNo = processNo.process_no;
      }
      router.push({
        name: 'NcrItemDetail',
        params: { processNo }
      });
    };

    const filterByResponsible = (responsibleName) => {
      searchKeyword.value = responsibleName;
      handleSearch();
    };

    // 标签类型方法
    const getStageTagType = (stage) => {
      const stageMap = {
        '生产中': 'primary',
        '检验时': 'success',
        '安装后': 'warning',
        '使用中': 'danger',
        '运输中': 'info'
      };
      return stageMap[stage] || 'info';
    };

    const getCurrentStageTagType = (stage) => {
      const stageMap = {
        '3-评审': 'primary',
        '4-处理': 'warning',
        '9-完成': 'success'
      };
      return stageMap[stage] || 'info';
    };

    const getPriorityTagType = (priority) => {
      const priorityMap = {
        '高': 'danger',
        '中': 'warning',
        '低': 'success'
      };
      return priorityMap[priority] || 'info';
    };

    const getStatusTagType = (status) => {
      const statusMap = {
        '已完成': 'success',
        '待处理': 'warning',
        '处理中': 'primary',
        '待审核': 'danger'
      };
      return statusMap[status] || 'info';
    };

    // 窗口大小调整处理
    const handleResize = () => {
      [typePieChart, stagePieChart, dqjdBarChart, responsibilityChart, unreviewedStagePieChart]
        .forEach(chart => {
          if (chart) {
            chart.resize();
          }
        });
    };

    // 生命周期钩子
    onMounted(() => {
      setTimeout(() => {
        fetchData();
        window.addEventListener('resize', handleResize);
        
        // 添加页面可见性API监听，当页面重新获得焦点时检查数据更新
        document.addEventListener('visibilitychange', () => {
          if (!document.hidden && !refreshLoading.value && !ncrDetailsLoading.value) {
            console.log('页面重新获得焦点，检查数据更新...');
            // 可以在这里添加数据新鲜度检查逻辑
          }
        });
        
        // 添加网络状态监听
        window.addEventListener('online', () => {
          console.log('网络连接恢复');
          if (ncrDetails.value.length === 0) {
            ElMessage.info('网络已恢复，正在重新加载数据...');
            fetchData();
          }
        });
        
        window.addEventListener('offline', () => {
          console.log('网络连接断开');
          ElMessage.warning('网络连接已断开，请检查网络设置');
        });
      }, 100);
    });

    onUnmounted(() => {
      [typePieChart, stagePieChart, dqjdBarChart, responsibilityChart, unreviewedStagePieChart]
        .forEach(chart => {
          if (chart) {
            chart.dispose();
          }
        });
      window.removeEventListener('resize', handleResize);
    });

    // 监听器
    watch([searchKeyword, selectedStage], () => {
      applyFilters();
    });

    return {
      // 响应式数据
      refreshLoading,
      ncrDetailsLoading,
      typePieRef,
      stagePieRef,
      dqjdBarRef,
      responsibilityChartRef,
      unreviewedStagePieRef,
      wczzListRef,
      ncrDetails,
      filteredNcrDetails,
      wczzListData,
      maxWczzValue,
      currentPage,
      pageSize,
      totalItems,
      searchKeyword,
      selectedStage,
      stageOptions,
      
      // 计算属性
      totalNcrCount,
      completedCount,
      pendingCount,
      activeResponsibleCount,
      
      // 方法
      refreshAllData,
      handleSearch,
      handleFilterChange,
      handlePageChange,
      goToTypeDetail,
      goToNcrDetail,
      filterByResponsible,
      getStageTagType,
      getCurrentStageTagType,
      getPriorityTagType,
      getStatusTagType
    };
  }
};
</script>

<style scoped>
.ncr-dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.stats-overview {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: white;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.main-charts, .analysis-section, .secondary-section {
  margin-bottom: 20px;
}

.chart-card, .list-card, .detail-table-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.table-controls {
  display: flex;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 300px;
  cursor: pointer;
}

.scroll-list-container {
  height: 300px;
  overflow: hidden;
  position: relative;
}

.scroll-list-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.scroll-list-content.auto-scroll {
  animation: autoScroll 40s linear infinite;
}

.scroll-list-content.auto-scroll:hover {
  animation-play-state: paused;
}

@keyframes autoScroll {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.list-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
  transform: translateX(5px);
}

.list-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
}

.count .el-tag {
  font-weight: 600;
}

.clickable-text {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.clickable-text:hover {
  color: #66b1ff;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>