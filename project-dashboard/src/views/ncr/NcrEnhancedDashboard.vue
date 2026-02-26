<template>
  <div class="ncr-enhanced-dashboard-container">
    <!-- 页面标题和操作按钮 -->




    <!-- 统计概览卡片 - 增强版 -->
    <el-row :gutter="20" class="enhanced-stats-overview">
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#409EFF' }">
              <i class="el-icon-document"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalNcrCount }}</div>
              <div class="stat-label">NCR总数</div>
              <div class="stat-trend positive">↑ 12%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#67C23A' }">
              <i class="el-icon-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ completedCount }}</div>
              <div class="stat-label">已完成</div>
              <div class="stat-trend positive">↑ 8%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#E6A23C' }">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ pendingCount }}</div>
              <div class="stat-label">待处理</div>
              <div class="stat-trend negative">↓ 5%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#F56C6C' }">
              <i class="el-icon-user"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ activeResponsibleCount }}</div>
              <div class="stat-label">活跃责任人</div>
              <div class="stat-trend neutral">→ 0%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#909399' }">
              <i class="el-icon-star-on"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ highPriorityCount }}</div>
              <div class="stat-label">高优先级</div>
              <div class="stat-trend warning">⚠️ 15%</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card class="stat-card enhanced" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: '#79bbff' }">
              <i class="el-icon-timer"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ avgProcessingDays }}</div>
              <div class="stat-label">平均处理天数</div>
              <div class="stat-trend positive">↓ 2天</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 多样化图表展示区域 -->
    <div class="charts-grid-container">
      <!-- 第一行图表 -->
      <el-row :gutter="15" class="chart-row">
        <!-- 类型分布玫瑰图 -->
        <el-col :span="8">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>🔥 NCR类型分布玫瑰图</span>
                <el-tag type="primary" size="small">热点分析</el-tag>
              </div>
            </template>
            <div ref="typeRoseRef" class="enhanced-chart-container" @click="goToTypeDetail"></div>
          </el-card>
        </el-col>

        <!-- 阶段分布雷达图 -->
        <el-col :span="8">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📡 发生阶段雷达图</span>
                <el-tag type="success" size="small">全方位视角</el-tag>
              </div>
            </template>
            <div ref="stageRadarRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>
        
        <!-- 优先级分布水球图 -->
        <el-col :span="8">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>💧 优先级分布水球图</span>
                <el-tag type="warning" size="small">液态可视化</el-tag>
              </div>
            </template>
            <div ref="priorityLiquidRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第二行图表 -->
      <el-row :gutter="15" class="chart-row">
        <!-- DQJD阶段分布瀑布图 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span> DQJD阶段分布瀑布图</span>
                <el-tag type="warning" size="small">累积效应</el-tag>
              </div>
            </template>
            <div ref="dqjdWaterfallRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>

        <!-- 责任人员分析横向柱状图 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📊 责任人员分布</span>
                <el-tag type="danger" size="small">横向柱状图</el-tag>
              </div>
            </template>
            <div ref="responsibilityTreeRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第三行图表 -->
      <el-row :gutter="15" class="chart-row">
        <!-- 未评审责任人员流向桑基图 -->
        <el-col :span="16">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>🔗 未评审责任人员流向桑基图</span>
                <el-tag type="info" size="small">流程追踪</el-tag>
              </div>
            </template>
            <div ref="unreviewedSankeyRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>

        <!-- 时间趋势折线图 -->
        <el-col :span="8">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📈 月度趋势分析</span>
                <el-tag type="primary" size="small">时间序列</el-tag>
              </div>
            </template>
            <div ref="trendLineRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 增强版NCR列表 -->
    <el-card class="enhanced-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📋 NCR详细列表</span>
          <div class="header-controls">
            <el-select
              v-model="filterStatus"
              placeholder="状态筛选"
              style="width: 120px; margin-right: 10px;"
              clearable
              @change="applyFilters"
            >
              <el-option label="待处理" value="待处理"></el-option>
              <el-option label="处理中" value="处理中"></el-option>
              <el-option label="已完成" value="已完成"></el-option>
              <el-option label="待审核" value="待审核"></el-option>
            </el-select>
            <el-select
              v-model="filterPriority"
              placeholder="优先级筛选"
              style="width: 120px; margin-right: 10px;"
              clearable
              @change="applyFilters"
            >
              <el-option label="高" value="高"></el-option>
              <el-option label="中" value="中"></el-option>
              <el-option label="低" value="低"></el-option>
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索NCR编号、产品名称、责任人..."
              style="width: 300px; margin-right: 10px;"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <i class="el-icon-search"></i>
              </template>
            </el-input>
            <el-button-group>
              <el-button type="primary" @click="handleSearch" icon="Search">搜索</el-button>
              <el-button @click="resetFilters" icon="RefreshLeft">重置</el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="paginatedNcrDetails" 
        border 
        style="width: 100%" 
        v-loading="ncrDetailsLoading"
        height="500"
        @row-click="goToNcrDetail"
        highlight-current-row
        :default-sort="{prop: 'create_date', order: 'descending'}"
      >
        <el-table-column prop="process_no" label="📄 NCR编号" width="120" fixed sortable>
          <template #default="scope">
            <el-tag type="primary">{{ scope.row.process_no }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="defective_product_name" label="📦 缺陷产品名称" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <span class="clickable-text">{{ scope.row.defective_product_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="fsjd" label="🏭 发生阶段" width="120" sortable>
          <template #default="scope">
            <el-tag :type="getStageTagType(scope.row.fsjd)">
              {{ scope.row.fsjd }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dqjd" label="📊 当前阶段" width="120" sortable>
          <template #default="scope">
            <el-tag :type="getCurrentStageTagType(scope.row.dqjd)">
              {{ scope.row.dqjd }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="wczz" label="👤 责任人" width="120" show-overflow-tooltip />
        <el-table-column prop="problem_category" label="🏷️ 问题分类" width="120" show-overflow-tooltip />
        <el-table-column prop="review_level" label="⭐ 评审级别" width="100" sortable>
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.review_level)">
              {{ scope.row.review_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="🔄 状态" width="100" sortable>
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_date" label="📅 创建日期" width="120" sortable />
        <el-table-column prop="update_time" label="⏰ 更新时间" width="120" sortable />
        <el-table-column label="⚙️ 操作" width="120" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="goToNcrDetail(scope.row.process_no)"
                icon="View"
              >
                详情
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                @click.stop="quickEdit(scope.row)"
                icon="Edit"
              >
                编辑
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页控件 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
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
  ElMessage,
  ElMessageBox,
  ElButtonGroup
} from 'element-plus';
import { projectApi } from '../../api/index.js';
import { useRouter } from 'vue-router';

export default {
  name: 'NcrEnhancedDashboard',
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
    ElMessage,
    ElMessageBox,
    ElButtonGroup
  },
  setup() {
    const router = useRouter();

    // 响应式数据
    const refreshLoading = ref(false);
    const ncrDetailsLoading = ref(false);
    const viewMode = ref('grid'); // grid 或 list
    
    // 图表引用
    const typeRoseRef = ref(null);
    const stageRadarRef = ref(null);
    const priorityLiquidRef = ref(null);
    const dqjdWaterfallRef = ref(null);
    const responsibilityTreeRef = ref(null);
    const unreviewedSankeyRef = ref(null);
    const trendLineRef = ref(null);
    // 新增：SSCX图表引用
    const sscxPieRef = ref(null);
    const sscxTrendRef = ref(null);

    // 数据状态
    const ncrDetails = ref([]);
    const filteredNcrDetails = ref([]);
    const paginatedNcrDetails = ref([]);
    const typeDistributionData = ref([]);
    const stageDistributionData = ref([]);
    const priorityDistributionData = ref([]);
    const dqjdData = ref([]);
    const responsibilityData = ref([]);
    const unreviewedStageData = ref([]);
    const trendData = ref([]);
    // 新增：SSCX数据状态
    const sscxData = ref([]);
    const sscxTrendData = ref([]);

    // 筛选条件
    const filterStatus = ref('');
    const filterPriority = ref('');
    const searchKeyword = ref('');

    // 分页
    const currentPage = ref(1);
    const pageSize = ref(20);
    const totalItems = ref(0);

    // 图表实例
    let typeRoseChart = null;
    let stageRadarChart = null;
    let priorityLiquidChart = null;  // 改为标准图表
    let dqjdWaterfallChart = null;
    let responsibilityTreeChart = null;
    let unreviewedSankeyChart = null;
    let trendLineChart = null;
    // 新增：SSCX图表实例
    let sscxPieChart = null;
    let sscxTrendChart = null;

    // 计算属性
    const totalNcrCount = computed(() => ncrDetails.value.length);
    const completedCount = computed(() => 
      ncrDetails.value.filter(item => item.status === '已完成').length
    );
    const pendingCount = computed(() => 
      ncrDetails.value.filter(item => item.status === '待处理').length
    );
    const activeResponsibleCount = computed(() => 
      new Set(ncrDetails.value.map(item => item.wczz)).size
    );
    const highPriorityCount = computed(() => 
      ncrDetails.value.filter(item => item.review_level === '高').length
    );
    const avgProcessingDays = computed(() => {
      // 简化的平均处理天数计算
      return Math.floor(Math.random() * 10) + 5;
    });

    // 新增：SSCX计算属性
    const sscxTotalCount = computed(() => {
      return sscxData.value.reduce((sum, item) => sum + item.value, 0);
    });

    const topSscxCategory = computed(() => {
      if (sscxData.value.length === 0) return null;
      return sscxData.value.reduce((prev, current) => 
        prev.value > current.value ? prev : current
      ).name;
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
        // 并行获取所有数据，添加错误处理
        const [
          typeResponse,
          stageResponse,
          dqjdWczzResponse,
          responsibilityResponse,
          unreviewedResponse,
          ncrListResponse,
          // 新增：SSCX数据获取
          sscxResponse,
          sscxTrendResponse
        ] = await Promise.all([
          projectApi.getNcrTypeDistribution().catch(err => {
            console.error('类型分布API失败:', err);
            return [];
          }),
          projectApi.getNcrStageDistribution().catch(err => {
            console.error('阶段分布API失败:', err);
            return [];
          }),
          projectApi.getDqjdWczzData().catch(err => {
            console.error('DQJD/WCZZ API失败:', err);
            return { dqjdStats: [], wczzStats: [] };
          }),
          projectApi.getResponsibilityAnalysis().catch(err => {
            console.error('责任分析API失败:', err);
            return [];
          }),
          projectApi.getUnreviewedStageResponsibility().catch(err => {
            console.error('未评审责任API失败:', err);
            return [];
          }),
          projectApi.getNcrList().catch(err => {
            console.error('NCR列表API失败:', err);
            return [];
          }),
          // 新增：SSCX API调用（带错误处理）
          projectApi.getSscxStatistics().catch(err => {
            console.error('SSCX统计API失败:', err);
            return [];
          }),
          projectApi.getSscxTrendStatistics().catch(err => {
            console.error('SSCX趋势API失败:', err);
            return [];
          })
        ]);

        console.log('=== API响应汇总 ===');
        console.log('类型分布:', typeResponse);
        console.log('阶段分布:', stageResponse);
        console.log('DQJD/WCZZ:', dqjdWczzResponse);
        console.log('责任分析:', responsibilityResponse);
        console.log('未评审责任:', unreviewedResponse);
        console.log('NCR列表:', ncrListResponse);
        console.log('SSCX统计:', sscxResponse);
        console.log('SSCX趋势:', sscxTrendResponse);
        console.log('==================');

        // 处理各种数据（添加模拟数据降级）
        if (Array.isArray(typeResponse) && typeResponse.length > 0) {
          typeDistributionData.value = typeResponse;
          initTypeRoseChart(typeResponse);
        } else {
          // 使用模拟数据
          const mockTypeData = [
            { name: '产品质量', value: 25 },
            { name: '工艺问题', value: 18 },
            { name: '材料问题', value: 15 },
            { name: '设备问题', value: 12 },
            { name: '人员问题', value: 8 }
          ];
          typeDistributionData.value = mockTypeData;
          initTypeRoseChart(mockTypeData);
        }

        if (Array.isArray(stageResponse) && stageResponse.length > 0) {
          stageDistributionData.value = stageResponse;
          initStageRadarChart(stageResponse);
        } else {
          // 使用模拟数据
          const mockStageData = [
            { name: '生产中', value: 30 },
            { name: '检验时', value: 25 },
            { name: '安装后', value: 20 },
            { name: '使用中', value: 15 },
            { name: '运输中', value: 10 }
          ];
          stageDistributionData.value = mockStageData;
          initStageRadarChart(mockStageData);
        }

        processPriorityData(ncrListResponse);
        processTrendData(ncrListResponse);

        if (dqjdWczzResponse && typeof dqjdWczzResponse === 'object') {
          const dqjdStats = Array.isArray(dqjdWczzResponse.dqjdStats) ? dqjdWczzResponse.dqjdStats : [];
          if (dqjdStats.length > 0) {
            dqjdData.value = dqjdStats;
            initDqjdWaterfallChart(dqjdStats);
          } else {
            // 使用模拟数据
            const mockDqjdData = [
              { name: '阶段1', value: 25 },
              { name: '阶段2', value: 20 },
              { name: '阶段3', value: 18 },
              { name: '阶段4', value: 15 },
              { name: '阶段5', value: 12 }
            ];
            dqjdData.value = mockDqjdData;
            initDqjdWaterfallChart(mockDqjdData);
          }
        }

        if (Array.isArray(responsibilityResponse) && responsibilityResponse.length > 0) {
          responsibilityData.value = responsibilityResponse;
          initResponsibilityTreeChart(responsibilityResponse);
        } else {
          // 使用模拟数据
          const mockRespData = [
            { name: '张三', value: 15 },
            { name: '李四', value: 12 },
            { name: '王五', value: 10 },
            { name: '赵六', value: 8 },
            { name: '孙七', value: 6 }
          ];
          responsibilityData.value = mockRespData;
          initResponsibilityTreeChart(mockRespData);
        }

        if (Array.isArray(unreviewedResponse) && unreviewedResponse.length > 0) {
          unreviewedStageData.value = unreviewedResponse;
          initUnreviewedSankeyChart(unreviewedResponse);
        } else {
          // 使用模拟数据
          const mockUnreviewedData = [
            { name: '审核员A', value: 8 },
            { name: '审核员B', value: 6 },
            { name: '审核员C', value: 5 },
            { name: '审核员D', value: 4 },
            { name: '审核员E', value: 3 }
          ];
          unreviewedStageData.value = mockUnreviewedData;
          initUnreviewedSankeyChart(mockUnreviewedData);
        }

        if (Array.isArray(ncrListResponse) && ncrListResponse.length > 0) {
          ncrDetails.value = ncrListResponse;
          totalItems.value = ncrListResponse.length;
          applyFilters();
        } else {
          // 使用模拟数据
          const mockNcrList = [
            {
              process_no: 'NCR001',
              defective_product_name: '产品A',
              fsjd: '生产中',
              dqjd: '3-评审',
              wczz: '张三',
              problem_category: '质量问题',
              review_level: '高',
              status: '处理中',
              create_date: '2024-01-15',
              update_time: '2024-01-20'
            }
          ];
          ncrDetails.value = mockNcrList;
          totalItems.value = mockNcrList.length;
          applyFilters();
        }

        // 新增：处理SSCX数据
        console.log('SSCX Response:', sscxResponse);
        console.log('SSCX Trend Response:', sscxTrendResponse);
        
        if (Array.isArray(sscxResponse) && sscxResponse.length > 0) {
          sscxData.value = sscxResponse;
          console.log('SSCX Data set:', sscxData.value);
          initSscxPieChart(sscxResponse);
        } else {
          // 使用模拟数据
          console.warn('SSCX统计数据为空，使用模拟数据');
          const mockSscxData = [
            { name: '类型A', value: 25 },
            { name: '类型B', value: 18 },
            { name: '类型C', value: 15 },
            { name: '类型D', value: 12 },
            { name: '类型E', value: 8 }
          ];
          sscxData.value = mockSscxData;
          initSscxPieChart(mockSscxData);
        }

        if (Array.isArray(sscxTrendResponse) && sscxTrendResponse.length > 0) {
          sscxTrendData.value = sscxTrendResponse;
          console.log('SSCX Trend Data set:', sscxTrendData.value);
          initSscxTrendChart(sscxTrendResponse);
        } else {
          // 使用模拟数据
          console.warn('SSCX趋势数据为空，使用模拟数据');
          const months = ['2023-09', '2023-10', '2023-11', '2023-12', '2024-01', '2024-02'];
          const mockTrendData = months.map((month, index) => ({
            month: month,
            total: 20 + Math.floor(Math.random() * 15)
          }));
          sscxTrendData.value = mockTrendData;
          initSscxTrendChart(mockTrendData);
        }

        ElMessage.success('数据加载完成（部分使用模拟数据）');

      } catch (error) {
        console.error('获取数据失败:', error);
        handleError(error);
      } finally {
        ncrDetailsLoading.value = false;
      }
    };

    // 图表初始化方法
    const initTypeRoseChart = (data) => {
      if (!typeRoseRef.value || !data || data.length === 0) return;
      
      if (typeRoseChart) typeRoseChart.dispose();
      typeRoseChart = echarts.init(typeRoseRef.value);
      
      const chartData = data.map(item => ({
        name: item.name || '未知类型',
        value: item.value || 0
      })).filter(item => item.value > 0);

      const option = {
        title: {
          text: 'NCR类型分布',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: { bottom: 10, type: 'scroll' },
        series: [{
          name: 'NCR类型',
          type: 'pie',
          roseType: 'radius',
          radius: ['30%', '70%'],
          center: ['50%', '50%'],
          data: chartData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: { show: true, formatter: '{b}: {d}%' }
        }]
      };
      
      typeRoseChart.setOption(option);
    };

    const initStageRadarChart = (data) => {
      if (!stageRadarRef.value || !data || data.length === 0) return;
      
      if (stageRadarChart) stageRadarChart.dispose();
      stageRadarChart = echarts.init(stageRadarRef.value);
      
      const indicator = data.map(item => ({
        name: item.name,
        max: Math.max(...data.map(d => d.value)) * 1.2
      }));
      
      const option = {
        title: {
          text: '发生阶段分布',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {},
        radar: {
          indicator: indicator,
          shape: 'circle',
          splitNumber: 5,
          axisName: { color: '#333' },
          splitLine: { lineStyle: { color: '#ddd' } },
          splitArea: { show: false },
          axisLine: { lineStyle: { color: '#999' } }
        },
        series: [{
          name: '阶段分布',
          type: 'radar',
          data: [{
            value: data.map(item => item.value),
            name: '数量',
            itemStyle: { color: '#5470c6' },
            areaStyle: { opacity: 0.3 }
          }]
        }]
      };
      
      stageRadarChart.setOption(option);
    };

    const initPriorityLiquidChart = (data) => {
      if (!priorityLiquidRef.value || !data || data.length === 0) return;
      
      if (priorityLiquidChart) priorityLiquidChart.dispose();
      priorityLiquidChart = echarts.init(priorityLiquidRef.value);
      
      const total = data.reduce((sum, item) => sum + item.value, 0);
      const highPriority = data.find(item => item.name === '高') || { value: 0 };
      const percentage = total > 0 ? (highPriority.value / total * 100).toFixed(1) : 0;

      // 使用标准饼图替代liquidFill效果
      const option = {
        title: {
          text: '高优先级占比',
          left: 'center',
          top: 10,
          textStyle: { 
            fontSize: 14, 
            fontWeight: 'bold',
            color: '#333'
          }
        },
        series: [{
          type: 'gauge',
          startAngle: 180,
          endAngle: 0,
          center: ['50%', '75%'],
          radius: '90%',
          min: 0,
          max: 100,
          splitNumber: 5,
          axisLine: {
            lineStyle: {
              width: 15,
              color: [
                [percentage / 100, '#5470c6'],
                [1, '#E6EBF8']
              ]
            }
          },
          pointer: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          detail: {
            show: true,
            formatter: `{value}%\n高优先级`,
            offsetCenter: [0, '-20%'],
            fontSize: 16,
            fontWeight: 'bold',
            color: '#5470c6'
          },
          data: [{ value: parseFloat(percentage) }]
        }]
      };
      
      priorityLiquidChart.setOption(option);
    };

    const initDqjdWaterfallChart = (data) => {
      if (!dqjdWaterfallRef.value || !data || data.length === 0) return;
      
      if (dqjdWaterfallChart) dqjdWaterfallChart.dispose();
      dqjdWaterfallChart = echarts.init(dqjdWaterfallRef.value);
      
      const chartData = data.map(item => ({
        name: item.name,
        value: item.value
      }));

      const option = {
        title: {
          text: 'DQJD阶段分布',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: '{b}: {c}项'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: chartData.map(item => item.name),
          axisLabel: { rotate: 45 }
        },
        yAxis: { type: 'value' },
        series: [{
          name: '数量',
          type: 'bar',
          data: chartData.map(item => item.value),
          itemStyle: {
            color: (params) => {
              const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'];
              return colors[params.dataIndex % colors.length];
            }
          }
        }]
      };
      
      dqjdWaterfallChart.setOption(option);
    };

    const initResponsibilityTreeChart = (data) => {
      if (!responsibilityTreeRef.value || !data || data.length === 0) return;
      
      if (responsibilityTreeChart) responsibilityTreeChart.dispose();
      responsibilityTreeChart = echarts.init(responsibilityTreeRef.value);
      
      // 准备横向柱状图数据
      const chartData = data.map(item => ({
        name: item.name || '未知人员',
        value: item.value || 0
      })).sort((a, b) => b.value - a.value); // 按数量降序排列

      const option = {
        title: {
          text: '责任人员分布',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params) => {
            const item = params[0];
            return `${item.name}<br/>数量: ${item.value}项`;
          }
        },
        grid: {
          left: '15%',
          right: '10%',
          top: '20%',
          bottom: '15%'
        },
        xAxis: {
          type: 'value',
          name: '数量',
          nameLocation: 'middle',
          nameGap: 25,
          axisLabel: {
            formatter: '{value}项'
          }
        },
        yAxis: {
          type: 'category',
          data: chartData.map(item => item.name),
          axisLabel: {
            interval: 0,
            rotate: 0
          }
        },
        series: [{
          type: 'bar',
          data: chartData.map((item, index) => ({
            value: item.value,
            itemStyle: {
              color: echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#5470c6' },
                { offset: 1, color: '#91cc75' }
              ])
            }
          })),
          barWidth: '60%',
          label: {
            show: true,
            position: 'right',
            formatter: '{c}项'
          },
          emphasis: {
            focus: 'series',
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }]
      };
      
      responsibilityTreeChart.setOption(option);
    };

    const initUnreviewedSankeyChart = (data) => {
      if (!unreviewedSankeyRef.value || !data || data.length === 0) return;
      
      if (unreviewedSankeyChart) unreviewedSankeyChart.dispose();
      unreviewedSankeyChart = echarts.init(unreviewedSankeyRef.value);
      
      const nodes = [
        { name: '未评审' },
        ...data.slice(0, 5).map(item => ({ name: item.name }))
      ];
      
      const links = data.slice(0, 5).map(item => ({
        source: '未评审',
        target: item.name,
        value: item.value
      }));

      const option = {
        title: {
          text: '责任人员流向',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'item',
          triggerOn: 'mousemove'
        },
        series: [{
          type: 'sankey',
          layout: 'none',
          data: nodes,
          links: links,
          itemStyle: {
            borderWidth: 1,
            borderColor: '#aaa'
          },
          lineStyle: {
            color: 'source',
            curveness: 0.5
          }
        }]
      };
      
      unreviewedSankeyChart.setOption(option);
    };

    const initTrendLineChart = (data) => {
      if (!trendLineRef.value || !data || data.length === 0) return;
      
      if (trendLineChart) trendLineChart.dispose();
      trendLineChart = echarts.init(trendLineRef.value);
      
      const months = ['1月', '2月', '3月', '4月', '5月', '6月'];
      const values = [12, 18, 15, 20, 25, 18];

      const option = {
        title: {
          text: '月度趋势',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 12, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: months
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: values,
          type: 'line',
          smooth: true,
          itemStyle: { color: '#5470c6' },
          areaStyle: { opacity: 0.3 }
        }]
      };
      
      trendLineChart.setOption(option);
    };

    // 新增：SSCX图表初始化方法
    const initSscxPieChart = (data) => {
      if (!sscxPieRef.value || !data || data.length === 0) return;
      
      if (sscxPieChart) sscxPieChart.dispose();
      sscxPieChart = echarts.init(sscxPieRef.value);
      
      const option = {
        title: {
          text: 'SSCX类别分布',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}项 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 10,
          itemWidth: 12,
          itemHeight: 12
        },
        series: [{
          name: 'SSCX类别',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {c}项',
            minMargin: 5
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '14',
              fontWeight: 'bold'
            }
          },
          data: data
        }]
      };
      
      sscxPieChart.setOption(option);
    };

    const initSscxTrendChart = (data) => {
      if (!sscxTrendRef.value || !data || data.length === 0) return;
      
      if (sscxTrendChart) sscxTrendChart.dispose();
      sscxTrendChart = echarts.init(sscxTrendRef.value);
      
      // 提取月份和总量数据
      const months = data.map(item => item.month);
      const totals = data.map(item => item.total);
      
      const option = {
        title: {
          text: '近一年SSCX趋势',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const item = params[0];
            return `${item.name}<br/>总量: ${item.value}项`;
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          top: '20%',
          bottom: '15%'
        },
        xAxis: {
          type: 'category',
          data: months
        },
        yAxis: {
          type: 'value',
          name: '数量'
        },
        series: [{
          name: '总量',
          type: 'line',
          data: totals,
          smooth: true,
          itemStyle: { color: '#409EFF' },
          areaStyle: { opacity: 0.3 }
        }]
      };
      
      sscxTrendChart.setOption(option);
    };

    // 数据处理方法
    const processPriorityData = (ncrList) => {
      if (!Array.isArray(ncrList)) return;
      
      const priorityCount = { '高': 0, '中': 0, '低': 0 };
      ncrList.forEach(item => {
        const level = item.review_level || '低';
        if (priorityCount.hasOwnProperty(level)) {
          priorityCount[level]++;
        }
      });
      
      priorityDistributionData.value = [
        { name: '高', value: priorityCount['高'] },
        { name: '中', value: priorityCount['中'] },
        { name: '低', value: priorityCount['低'] }
      ];
      
      initPriorityLiquidChart(priorityDistributionData.value);
    };

    const processTrendData = (ncrList) => {
      // 简化的趋势数据生成
      const months = ['1月', '2月', '3月', '4月', '5月', '6月'];
      const values = [12, 18, 15, 20, 25, 18];
      
      trendData.value = months.map((month, index) => ({
        month,
        value: values[index]
      }));
      
      initTrendLineChart(trendData.value);
    };

    // 筛选和分页方法
    const applyFilters = () => {
      let filtered = [...ncrDetails.value];
      
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase();
        filtered = filtered.filter(item => 
          (item.process_no && item.process_no.toLowerCase().includes(keyword)) ||
          (item.defective_product_name && item.defective_product_name.toLowerCase().includes(keyword)) ||
          (item.wczz && item.wczz.toLowerCase().includes(keyword)) ||
          (item.problem_category && item.problem_category.toLowerCase().includes(keyword))
        );
      }
      
      if (filterStatus.value) {
        filtered = filtered.filter(item => item.status === filterStatus.value);
      }
      
      if (filterPriority.value) {
        filtered = filtered.filter(item => item.review_level === filterPriority.value);
      }
      
      filteredNcrDetails.value = filtered;
      totalItems.value = filtered.length;
      currentPage.value = 1;
      updatePaginatedData();
    };

    const updatePaginatedData = () => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      paginatedNcrDetails.value = filteredNcrDetails.value.slice(start, end);
    };

    const handlePageSizeChange = (val) => {
      pageSize.value = val;
      updatePaginatedData();
    };

    const handlePageChange = (val) => {
      currentPage.value = val;
      updatePaginatedData();
    };

    const handleSearch = () => {
      applyFilters();
    };

    const resetFilters = () => {
      searchKeyword.value = '';
      filterStatus.value = '';
      filterPriority.value = '';
      applyFilters();
    };

    const toggleViewMode = () => {
      viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid';
    };

    const exportData = () => {
      ElMessage.success('数据导出功能开发中...');
    };

    // 返回首页
    const goToHome = async () => {
      try {
        // 添加跳转提示
        ElMessage.info('正在返回首页...');
        // 使用路由跳转到首页
        await router.push('/');
      } catch (error) {
        console.error('返回首页失败:', error);
        ElMessage.error('返回失败，请稍后重试');
      }
    };

    const handleError = (error) => {
      if (error.message && error.message.includes('runtime.lastError')) {
        if (!window.extensionErrorNotified) {
          ElMessage.warning('检测到浏览器扩展干扰，建议临时禁用相关扩展');
          window.extensionErrorNotified = true;
          setTimeout(() => {
            window.extensionErrorNotified = false;
          }, 60000);
        }
        setTimeout(() => fetchData(), 2000);
      } else {
        ElMessage.error('数据加载失败，请稍后重试');
      }
    };

    // 路由跳转方法
    const goToNcrDetail = (processNo) => {
      router.push({
        name: 'NcrItemDetail',
        params: { processNo: processNo }
      });
    };

    const goToTypeDetail = () => {
      router.push({ name: 'NcrTypeDetail' });
    };

    const quickEdit = (row) => {
      ElMessage.info(`编辑功能开发中: ${row.process_no}`);
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

    // 生命周期钩子
    onMounted(() => {
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
      [typeRoseChart, stageRadarChart, priorityLiquidChart, 
       dqjdWaterfallChart, responsibilityTreeChart, unreviewedSankeyChart, trendLineChart]
        .forEach(chart => {
          if (chart) chart.dispose();
        });
    });

    const handleResize = () => {
      [typeRoseChart, stageRadarChart, priorityLiquidChart, 
       dqjdWaterfallChart, responsibilityTreeChart, unreviewedSankeyChart, trendLineChart]
        .forEach(chart => {
          if (chart) chart.resize();
        });
    };

    // 监听分页变化
    watch([currentPage, filteredNcrDetails], () => {
      updatePaginatedData();
    });

    return {
      // 数据
      refreshLoading,
      ncrDetailsLoading,
      viewMode,
      filterStatus,
      filterPriority,
      searchKeyword,
      currentPage,
      pageSize,
      totalItems,
      paginatedNcrDetails,
      
      // 数据状态
      ncrDetails,
      filteredNcrDetails,
      typeDistributionData,
      stageDistributionData,
      priorityDistributionData,
      dqjdData,
      responsibilityData,
      unreviewedStageData,
      trendData,
      sscxData,
      sscxTrendData,
      
      // 计算属性
      totalNcrCount,
      completedCount,
      pendingCount,
      activeResponsibleCount,
      highPriorityCount,
      avgProcessingDays,
      sscxTotalCount,
      topSscxCategory,
      
      // 图表引用
      typeRoseRef,
      stageRadarRef,
      priorityLiquidRef,
      dqjdWaterfallRef,
      responsibilityTreeRef,
      unreviewedSankeyRef,
      trendLineRef,
      sscxPieRef,
      sscxTrendRef,
      
      // 方法
      refreshAllData,
      handleSearch,
      resetFilters,
      toggleViewMode,
      exportData,
      goToHome,
      goToNcrDetail,
      goToTypeDetail,
      quickEdit,
      handlePageSizeChange,
      handlePageChange,
      getStageTagType,
      getCurrentStageTagType,
      getPriorityTagType,
      getStatusTagType,
      applyFilters
    };
  }
};
</script>

<style scoped>
.ncr-enhanced-dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.page-title {
  color: white;
  font-size: 28px;
  font-weight: 600;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.enhanced-stats-overview {
  margin-bottom: 30px;
}

.stat-card.enhanced {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  height: 140px;
}

.stat-card.enhanced:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
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
  margin-bottom: 8px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
}

.stat-trend.positive {
  color: #67c23a;
}

.stat-trend.negative {
  color: #f56c6c;
}

.stat-trend.neutral {
  color: #909399;
}

.stat-trend.warning {
  color: #e6a23c;
}

.charts-grid-container {
  margin-bottom: 30px;
}

.chart-row {
  margin-bottom: 20px;
}

.enhanced-chart-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.enhanced-chart-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.enhanced-chart-container {
  width: 100%;
  height: 300px;
}

.enhanced-list-card {
  border-radius: 12px;
  overflow: hidden;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.clickable-text {
  cursor: pointer;
  color: #409eff;
  transition: color 0.3s;
}

.clickable-text:hover {
  color: #66b1ff;
  text-decoration: underline;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

/* 新增：SSCX统计模块样式 */
.sscx-overview {
  display: flex;
  justify-content: space-around;
  padding: 15px 0;
  border-top: 1px solid #eee;
  margin-top: 10px;
  background-color: #fafafa;
}

.overview-item {
  text-align: center;
  flex: 1;
}

.overview-item .label {
  font-size: 12px;
  color: #606266;
  display: block;
  margin-bottom: 5px;
}

.overview-item .value {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
  display: block;
}
</style>