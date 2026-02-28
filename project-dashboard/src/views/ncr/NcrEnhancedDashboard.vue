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
    </div>

    <!-- 新增：SSCX核心统计图表区域 -->
    <div class="charts-grid-container">
      <el-row :gutter="20" class="chart-row">
        <!-- SSCX项目分类滚动表格 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📊 SSCX项目分类统计</span>
                <el-tag type="primary" size="small">Top 15 排名</el-tag>
              </div>
            </template>
            <div class="sscx-table-container">
              <el-table 
                :data="sscxTableData" 
                height="320"
                stripe
                style="width: 100%"
                :default-sort="{prop: 'value', order: 'descending'}"
              >
                <el-table-column prop="rank" label="排名" width="60" sortable>
                  <template #default="scope">
                    <el-tag 
                      :type="getRankTagType(scope.row.rank)" 
                      size="small"
                      effect="dark"
                    >
                      {{ scope.row.rank }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="项目名称" min-width="200" show-overflow-tooltip>
                  <template #default="scope">
                    <span class="project-name">{{ scope.row.name }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="项目数量" width="100" sortable>
                  <template #default="scope">
                    <span class="count-number">{{ scope.row.value }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="percentage" label="占比" width="80" sortable>
                  <template #default="scope">
                    <el-progress 
                      :percentage="scope.row.percentage" 
                      :stroke-width="8"
                      :show-text="false"
                      :color="getProgressColor(scope.row.percentage)"
                    />
                    <span class="percentage-text">{{ scope.row.percentage }}%</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>

        <!-- SSCX月度趋势折线图 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📈 SSCX月度趋势分析</span>
                <el-tag type="success" size="small">时间序列</el-tag>
              </div>
            </template>
            <div ref="sscxTrendRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 新增：SSCX数据接口图表区域 -->
    <div class="charts-grid-container">
      <el-row :gutter="20" class="chart-row">
        <!-- SSCX问题分类热力图 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>📊 SSCX问题分类热力图</span>
                <el-tag type="warning" size="small">分类分析</el-tag>
              </div>
            </template>
            <div ref="sscxProblemHeatmapRef" class="enhanced-chart-container"></div>
          </el-card>
        </el-col>

        <!-- SSCX处理时效散点图 -->
        <el-col :span="12">
          <el-card shadow="hover" class="enhanced-chart-card">
            <template #header>
              <div class="card-header">
                <span>⏱️ SSCX处理时效散点图</span>
                <el-tag type="danger" size="small">时效分析</el-tag>
              </div>
            </template>
            <div ref="sscxProcessingScatterRef" class="enhanced-chart-container"></div>
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
import {
  convertSscxStatisticsData,
  convertSscxTrendData,
  getSscxDataSummary,
  getSscxChartConfig
} from '../../utils/sscxDataProcessor.js';

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
    const sscxTrendRef = ref(null);
    // 新增：SSCX数据接口图表引用
    const sscxProblemHeatmapRef = ref(null);
    const sscxProcessingScatterRef = ref(null);

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
    // 新增：SSCX接口数据状态
    const sscxInterfaceData = ref([]);
    const sscxProcessingData = ref([]);

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
    let sscxTrendChart = null;
    // 新增：SSCX数据接口图表实例
    let sscxProblemHeatmapChart = null;
    let sscxProcessingScatterChart = null;

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

    // 新增：SSCX表格数据
    const sscxTableData = ref([]);
    
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
          // SSCX核心接口数据获取
          sscxResponse,
          sscxTrendResponse,
          sscxYearlyResponse
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
          // SSCX核心接口调用（带错误处理）
          projectApi.getSscxStatistics().catch(err => {
            console.error('SSCX统计API失败:', err);
            return [];
          }),
          projectApi.getSscxTrendStatistics().catch(err => {
            console.error('SSCX趋势API失败:', err);
            return [];
          }),
          // 新增：SSCX年度统计接口（前15名）
          projectApi.getSscxYearlyStats().catch(err => {
            console.error('SSCX年度统计API失败:', err);
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

        // 新增：处理SSCX数据（优先使用年度统计数据）
        console.log('🔄 开始处理SSCX数据...');
        console.log('原始SSCX统计响应类型:', typeof sscxResponse, '值:', sscxResponse);
        console.log('原始SSCX趋势响应类型:', typeof sscxTrendResponse, '值:', sscxTrendResponse);
        console.log('SSCX年度统计响应类型:', typeof sscxYearlyResponse, '值:', sscxYearlyResponse);
        
        // 优先使用新的年度统计数据接口
        try {
          if (Array.isArray(sscxYearlyResponse) && sscxYearlyResponse.length > 0) {
            console.log('📊 使用SSCX年度统计数据，项目数:', sscxYearlyResponse.length);
            
            // 直接使用年度统计数据（已经是前15名）
            const convertedSscxData = sscxYearlyResponse.slice(0, 15);
            
            sscxData.value = convertedSscxData;
            console.log('✅ SSCX年度统计数据处理完成:', {
              项目数: convertedSscxData.length,
              前5个项目: convertedSscxData.slice(0, 5)
            });
            
            // 初始化SSCX表格数据
            if (convertedSscxData.length > 0) {
              updateSscxTableData(convertedSscxData);
              ElMessage.success(`SSCX年度统计表格加载成功 (${convertedSscxData.length}个项目)`);
            } else {
              throw new Error('年度统计数据为空');
            }
          } else if (sscxResponse && typeof sscxResponse === 'object' && Object.keys(sscxResponse).length > 0) {
            console.log('📊 回退到原始SSCX统计数据，项目数:', Object.keys(sscxResponse).length);
            
            // 使用数据转换工具处理统计数据
            const convertedSscxData = convertSscxStatisticsData(sscxResponse, {
              sortBy: 'value',
              sortOrder: 'desc',
              limit: 15, // 只显示前15个项目
              excludeZero: true,
              minValue: 1
            });
            
            sscxData.value = convertedSscxData;
            console.log('✅ SSCX统计数据转换完成:', {
              原始项目数: Object.keys(sscxResponse).length,
              转换后项目数: convertedSscxData.length,
              前5个项目: convertedSscxData.slice(0, 5)
            });
            
            // 获取数据摘要
            const summary = getSscxDataSummary(sscxResponse);
            console.log('📊 SSCX统计摘要:', summary);
            
            // 初始化SSCX表格数据
            if (convertedSscxData.length > 0) {
              updateSscxTableData(convertedSscxData);
              ElMessage.success(`SSCX统计表格加载成功 (${convertedSscxData.length}个项目)`);
            } else {
              throw new Error('转换后数据为空');
            }
          } else {
            throw new Error('原始数据为空或格式无效');
          }
        } catch (error) {
          console.warn('⚠️ SSCX统计数据处理失败:', error.message, '使用模拟数据');
          // 更丰富和真实的模拟数据
          const mockSscxData = [
            { name: 'CRH6F牵引变压器风机项目', value: 45, itemStyle: { color: '#5470c6' } },
            { name: '广州地铁18号线工程', value: 38, itemStyle: { color: '#91cc75' } },
            { name: '顺特电气SYJ9002系统', value: 32, itemStyle: { color: '#fac858' } },
            { name: '神华集团八轴货运机车', value: 28, itemStyle: { color: '#ee6666' } },
            { name: 'HXD1D型电力机车升级', value: 25, itemStyle: { color: '#73c0de' } },
            { name: '复兴号动车组控制系统', value: 22, itemStyle: { color: '#3ba272' } },
            { name: '城市轨道交通信号系统', value: 19, itemStyle: { color: '#fc8452' } },
            { name: '高速铁路通信设备', value: 17, itemStyle: { color: '#9a60b4' } },
            { name: '智能电网调度系统', value: 15, itemStyle: { color: '#ea7ccc' } },
            { name: '新能源汽车充电桩网络', value: 13, itemStyle: { color: '#5470c6' } },
            { name: '工业自动化生产线', value: 11, itemStyle: { color: '#91cc75' } },
            { name: '智慧城市管理系统', value: 9, itemStyle: { color: '#fac858' } },
            { name: '5G基站建设', value: 7, itemStyle: { color: '#ee6666' } },
            { name: '数据中心基础设施', value: 6, itemStyle: { color: '#73c0de' } },
            { name: '其他重点项目', value: 20, itemStyle: { color: '#3ba272' } }
          ];
          sscxData.value = mockSscxData;
          updateSscxTableData(mockSscxData);
          ElMessage.warning('SSCX统计使用模拟数据展示');
        }

        // 处理SSCX趋势数据
        try {
          if (Array.isArray(sscxTrendResponse) && sscxTrendResponse.length > 0) {
            console.log('📈 原始SSCX趋势数据点数:', sscxTrendResponse.length);
            
            // 使用数据转换工具处理趋势数据
            const convertedTrendData = convertSscxTrendData(sscxTrendResponse, {
              aggregate: true, // 聚合为总计
              formatMonth: true
            });
            
            sscxTrendData.value = convertedTrendData;
            console.log('✅ SSCX趋势数据转换完成:', {
              时间点数: convertedTrendData.months.length,
              系列数: convertedTrendData.series.length,
              月份范围: `${convertedTrendData.months[0]} 至 ${convertedTrendData.months[convertedTrendData.months.length - 1]}`
            });
            
            // 获取趋势数据摘要
            const trendSummary = getSscxDataSummary(sscxTrendResponse, true);
            console.log('📈 SSCX趋势摘要:', trendSummary);
            
            // 初始化SSCX趋势图
            if (convertedTrendData.series && convertedTrendData.series.length > 0) {
              initSscxTrendChart(convertedTrendData);
              ElMessage.success(`SSCX趋势图表加载成功 (${convertedTrendData.months.length}个时间点)`);
            } else {
              throw new Error('转换后趋势数据为空');
            }
          } else {
            throw new Error('原始趋势数据为空或格式无效');
          }
        } catch (error) {
          console.warn('⚠️ SSCX趋势数据处理失败:', error.message, '启用趋势数据降级');
          ElMessage.info({
            message: '📈 趋势数据获取失败，显示历史参考数据',
            type: 'info',
            duration: 3000
          });
          const months = ['2023年9月', '2023年10月', '2023年11月', '2023年12月', '2024年1月', '2024年2月'];
          const mockTrendData = {
            months: months,
            series: [{
              name: '总计',
              type: 'line',
              data: [120, 132, 101, 134, 90, 230],
              smooth: true
            }]
          };
          sscxTrendData.value = mockTrendData;
          initSscxTrendChart(mockTrendData);
          ElMessage.warning('SSCX趋势使用模拟数据展示');
        }

        // SSCX数据处理已完成

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
          formatter: '{b}: {c}'
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
            return `${item.name}<br/>Total: ${item.value}`;
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

    // 新增：SSCX饼图初始化（使用现代化配置）
    // 注意：此方法已废弃，因为已改为表格展示
    /*
    const initSscxPieChart = (data) => {
      // 已废弃的方法内容...
    };
    */

    // 修改：SSCX表格数据更新方法
    const updateSscxTableData = (data) => {
      try {
        console.log('📋 开始更新SSCX表格数据，原始数据:', data);
        
        if (!data || data.length === 0) {
          console.warn('⚠️ SSCX表格数据为空');
          sscxTableData.value = [];
          return;
        }
        
        // 计算总数量
        const total = data.reduce((sum, item) => sum + item.value, 0);
        console.log('📊 SSCX数据总和:', total);
        
        // 构造表格数据
        const tableData = data.map((item, index) => ({
          rank: index + 1,
          name: item.name || '未知项目',
          value: item.value || 0,
          percentage: total > 0 ? parseFloat(((item.value / total) * 100).toFixed(1)) : 0,
          rawItem: item // 保存原始数据用于后续操作
        }));
        
        // 按数量降序排序（虽然表格会自动排序，但这里确保顺序正确）
        tableData.sort((a, b) => b.value - a.value);
        
        // 更新响应式数据
        sscxTableData.value = tableData;
        
        console.log('✅ SSCX表格数据更新完成:', {
          总项目数: tableData.length,
          总数量: total,
          前5名: tableData.slice(0, 5)
        });
        
        // 显示成功消息
        ElMessage.success(`SSCX项目统计表格已更新 (${tableData.length}个项目)`);
        
      } catch (error) {
        console.error('💥 SSCX表格数据更新失败:', error);
        ElMessage.error('SSCX表格数据更新失败: ' + error.message);
        sscxTableData.value = [];
      }
    };

    // 新增：SSCX趋势图初始化（使用现代化配置）
    const initSscxTrendChart = (convertedData) => {
      try {
        console.log('📈 开始初始化SSCX趋势图，数据:', convertedData);
        
        if (!sscxTrendRef.value) {
          console.warn('⚠️ SSCX趋势图容器引用为空');
          return;
        }
        
        if (!convertedData || !convertedData.series || convertedData.series.length === 0) {
          console.warn('⚠️ SSCX趋势图数据为空或格式无效');
          return;
        }
        
        // 销毁旧实例
        if (sscxTrendChart) {
          sscxTrendChart.dispose();
        }
        
        // 初始化图表
        sscxTrendChart = echarts.init(sscxTrendRef.value);
        console.log('✅ SSCX趋势图实例创建成功');
        
        // 使用配置工具生成图表配置
        const chartConfig = getSscxChartConfig('line', {
          title: 'SSCX月度趋势分析',
          showLegend: true,
          animation: true,
          colorPalette: [
            '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'
          ]
        });
        
        // 设置坐标轴
        chartConfig.xAxis.data = convertedData.months;
        chartConfig.yAxis = {
          type: 'value',
          name: '问题数量',
          axisLabel: {
            formatter: '{value}项'
          }
        };
        
        // 设置数据系列
        chartConfig.series = convertedData.series.map((serie, index) => ({
          ...serie,
          smooth: true,
          symbolSize: 6,
          lineStyle: {
            width: 3
          },
          areaStyle: {
            opacity: 0.1
          }
        }));
        
        // 添加额外配置
        chartConfig.grid = {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '20%',
          containLabel: true
        };
        
        chartConfig.tooltip = {
          trigger: 'axis',
          formatter: (params) => {
            let result = `${params[0].axisValue}<br/>`;
            params.forEach(param => {
              result += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${param.color};"></span>`;
              result += `${param.seriesName}: ${param.value}项<br/>`;
            });
            return result;
          }
        };
        
        // 设置配置
        sscxTrendChart.setOption(chartConfig);
        console.log('✅ SSCX趋势图配置设置完成');
        
        // 添加点击事件
        sscxTrendChart.on('click', (params) => {
          console.log('SSCX趋势点击:', params.seriesName, params.name, params.value);
          ElMessage.info(`${params.seriesName} 在 ${params.name} 有 ${params.value} 项问题`);
        });
        
        console.log('🎉 SSCX趋势图初始化完成');
      } catch (error) {
        console.error('💥 SSCX趋势图初始化失败:', error);
        ElMessage.error('SSCX趋势图初始化失败: ' + error.message);
      }
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

    // 新增：SSCX接口数据获取方法
    const fetchSscxInterfaceData = async () => {
      // 模拟从SSCX接口获取问题分类数据
      // 实际项目中这里应该调用具体的API接口
      return new Promise((resolve) => {
        setTimeout(() => {
          const mockData = [
            { category: '质量问题', subCategory: '尺寸偏差', count: 25, severity: '高' },
            { category: '质量问题', subCategory: '表面缺陷', count: 18, severity: '中' },
            { category: '工艺问题', subCategory: '加工参数', count: 15, severity: '高' },
            { category: '工艺问题', subCategory: '设备故障', count: 12, severity: '中' },
            { category: '材料问题', subCategory: '原材料缺陷', count: 10, severity: '高' },
            { category: '材料问题', subCategory: '供应商问题', count: 8, severity: '中' },
            { category: '人员问题', subCategory: '操作失误', count: 6, severity: '低' },
            { category: '人员问题', subCategory: '培训不足', count: 4, severity: '中' }
          ];
          resolve(mockData);
        }, 500);
      });
    };

    const fetchSscxProcessingData = async () => {
      // 模拟从SSCX接口获取处理时效数据
      // 实际项目中这里应该调用具体的API接口
      return new Promise((resolve) => {
        setTimeout(() => {
          const mockData = [
            { id: 1, category: '质量问题', createTime: '2024-01-15', processTime: 3, status: '已完成' },
            { id: 2, category: '工艺问题', createTime: '2024-01-16', processTime: 5, status: '处理中' },
            { id: 3, category: '材料问题', createTime: '2024-01-17', processTime: 2, status: '已完成' },
            { id: 4, category: '质量问题', createTime: '2024-01-18', processTime: 7, status: '待处理' },
            { id: 5, category: '人员问题', createTime: '2024-01-19', processTime: 1, status: '已完成' },
            { id: 6, category: '工艺问题', createTime: '2024-01-20', processTime: 4, status: '处理中' },
            { id: 7, category: '质量问题', createTime: '2024-01-21', processTime: 6, status: '待处理' },
            { id: 8, category: '材料问题', createTime: '2024-01-22', processTime: 3, status: '已完成' }
          ];
          resolve(mockData);
        }, 500);
      });
    };

    // 新增：生成模拟热力图数据
    const generateMockProblemHeatmapData = () => {
      const categories = ['质量问题', '工艺问题', '材料问题', '设备问题', '人员问题'];
      const subCategories = ['类型A', '类型B', '类型C', '类型D', '类型E'];
      const severities = ['高', '中', '低'];
      
      const data = [];
      categories.forEach((category, i) => {
        subCategories.forEach((subCategory, j) => {
          severities.forEach((severity, k) => {
            data.push([
              i,
              j,
              k,
              Math.floor(Math.random() * 30) + 5
            ]);
          });
        });
      });
      return data;
    };

    // 新增：生成模拟散点图数据
    const generateMockProcessingScatterData = () => {
      const categories = ['质量问题', '工艺问题', '材料问题', '设备问题', '人员问题'];
      const statuses = ['已完成', '处理中', '待处理'];
      
      const data = [];
      categories.forEach((category, i) => {
        statuses.forEach((status, j) => {
          const count = Math.floor(Math.random() * 20) + 5;
          for (let k = 0; k < count; k++) {
            data.push([
              i + (Math.random() - 0.5) * 0.3, // x轴：分类
              Math.floor(Math.random() * 10) + 1, // y轴：处理时间
              category, // 分类名称
              status, // 状态
              Math.floor(Math.random() * 100) + 20 // 气泡大小
            ]);
          }
        });
      });
      return data;
    };

    // 新增：SSCX问题分类热力图初始化
    const initSscxProblemHeatmapChart = (data) => {
      if (!sscxProblemHeatmapRef.value) return;
      
      if (sscxProblemHeatmapChart) sscxProblemHeatmapChart.dispose();
      sscxProblemHeatmapChart = echarts.init(sscxProblemHeatmapRef.value);
      
      const categories = ['质量问题', '工艺问题', '材料问题', '设备问题', '人员问题'];
      const subCategories = ['类型A', '类型B', '类型C', '类型D', '类型E'];
      const severities = ['高', '中', '低'];
      
      const option = {
        title: {
          text: 'SSCX问题分类热力图',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          position: 'top',
          formatter: (params) => {
            return `
              <div>
                <strong>${categories[params.value[0]]}</strong><br/>
                子分类: ${subCategories[params.value[1]]}<br/>
                严重程度: ${severities[params.value[2]]}<br/>
                数量: ${params.value[3]}项
              </div>
            `;
          }
        },
        grid: {
          height: '60%',
          top: '20%',
          left: '15%',
          right: '10%'
        },
        xAxis: {
          type: 'category',
          data: subCategories,
          splitArea: { show: true }
        },
        yAxis: {
          type: 'category',
          data: categories,
          splitArea: { show: true }
        },
        visualMap: {
          min: 0,
          max: 35,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          inRange: {
            color: ['#e0f3db', '#a8ddb5', '#7bccc4', '#43a2ca', '#0868ac']
          }
        },
        series: [{
          name: '问题数量',
          type: 'heatmap',
          data: data,
          label: {
            show: true
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      };
      
      sscxProblemHeatmapChart.setOption(option);
    };

    // 新增：SSCX处理时效散点图初始化
    const initSscxProcessingScatterChart = (data) => {
      if (!sscxProcessingScatterRef.value) return;
      
      if (sscxProcessingScatterChart) sscxProcessingScatterChart.dispose();
      sscxProcessingScatterChart = echarts.init(sscxProcessingScatterRef.value);
      
      const categories = ['质量问题', '工艺问题', '材料问题', '设备问题', '人员问题'];
      const statusColors = {
        '已完成': '#52c41a',
        '处理中': '#1890ff',
        '待处理': '#faad14'
      };
      
      const seriesData = {};
      data.forEach(item => {
        if (!seriesData[item[3]]) {
          seriesData[item[3]] = [];
        }
        seriesData[item[3]].push({
          value: [item[0], item[1]],
          symbolSize: item[4],
          category: item[2],
          status: item[3]
        });
      });
      
      const series = Object.keys(seriesData).map(status => ({
        name: status,
        type: 'scatter',
        data: seriesData[status],
        itemStyle: {
          color: statusColors[status] || '#999'
        },
        emphasis: {
          focus: 'series'
        }
      }));
      
      const option = {
        title: {
          text: 'SSCX处理时效散点图',
          left: 'center',
          top: 10,
          textStyle: { fontSize: 14, fontWeight: 'bold' }
        },
        tooltip: {
          trigger: 'item',
          formatter: (params) => {
            return `
              <div>
                <strong>${params.data.category}</strong><br/>
                状态: ${params.seriesName}<br/>
                处理时间: ${params.value[1]}天<br/>
                数量: ${Math.floor(params.data.symbolSize / 20)}项
              </div>
            `;
          }
        },
        legend: {
          data: Object.keys(statusColors),
          bottom: 10
        },
        xAxis: {
          type: 'category',
          data: categories,
          name: '问题分类'
        },
        yAxis: {
          type: 'value',
          name: '处理时间(天)'
        },
        series: series
      };
      
      sscxProcessingScatterChart.setOption(option);
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
      console.error('🚨 组件错误处理:', error);
      
      if (error.message && error.message.includes('runtime.lastError')) {
        if (!window.extensionErrorNotified) {
          ElMessage.warning({
            message: '检测到浏览器扩展干扰，建议临时禁用相关扩展',
            duration: 6000
          });
          window.extensionErrorNotified = true;
          setTimeout(() => {
            window.extensionErrorNotified = false;
          }, 60000);
        }
        // 延迟重试
        setTimeout(() => fetchData(), 3000);
      } else if (error.type === 'extension_interference') {
        // 已经由API拦截器处理过的扩展干扰错误
        console.log('🔄 扩展干扰错误已在API层处理');
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

    // 表格辅助方法
    const getRankTagType = (rank) => {
      if (rank <= 3) return 'danger';  // 前3名红色
      if (rank <= 5) return 'warning'; // 4-5名橙色
      if (rank <= 10) return 'primary'; // 6-10名蓝色
      return 'info'; // 11-15名灰色
    };
    
    const getProgressColor = (percentage) => {
      if (percentage >= 20) return '#52c41a'; // 绿色
      if (percentage >= 10) return '#1890ff'; // 蓝色
      if (percentage >= 5) return '#faad14';  // 黄色
      return '#ff4d4f'; // 红色
    };

    // 生命周期钩子
    onMounted(() => {
      fetchData();
      window.addEventListener('resize', handleResize);
    });

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize);
      // 清理所有图表实例
      [typeRoseChart, stageRadarChart, priorityLiquidChart, 
       dqjdWaterfallChart, responsibilityTreeChart, unreviewedSankeyChart,
       trendLineChart, sscxTrendChart, sscxProblemHeatmapChart, sscxProcessingScatterChart].forEach(chart => {
        if (chart) chart.dispose();
      });
    });

    const handleResize = () => {
      [typeRoseChart, stageRadarChart, priorityLiquidChart, 
       dqjdWaterfallChart, responsibilityTreeChart, unreviewedSankeyChart, 
       trendLineChart, sscxTrendChart]
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
      sscxTrendRef,
      sscxProblemHeatmapRef,
      sscxProcessingScatterRef,
      
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
      applyFilters,
      // 新增SSCX方法
      fetchSscxInterfaceData,
      fetchSscxProcessingData,
      generateMockProblemHeatmapData,
      generateMockProcessingScatterData,
      initSscxProblemHeatmapChart,
      initSscxProcessingScatterChart,
      initSscxTrendChart,
      updateSscxTableData,
      getRankTagType,
      getProgressColor,
      sscxTableData
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
  height: 320px;
}

/* SSCX表格容器样式 */
.sscx-table-container {
  padding: 10px;
  height: 320px;
  display: flex;
  flex-direction: column;
}

.project-name {
  font-weight: 500;
  color: #303133;
}

.count-number {
  font-weight: 600;
  color: #409EFF;
  font-size: 14px;
}

.percentage-text {
  font-size: 12px;
  color: #606266;
  margin-left: 5px;
}

:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.2s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-table .cell) {
  padding: 8px 0;
}

:deep(.el-table__header th) {
  background-color: #f8f9fa;
  font-weight: 600;
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

/* SSCX图表摘要样式 */
.chart-summary {
  margin-top: 15px;
  padding: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border-left: 4px solid #409EFF;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 6px 0;
  border-bottom: 1px dashed #dee2e6;
}

.summary-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.summary-label {
  font-size: 13px;
  color: #6c757d;
  font-weight: 500;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-summary {
    padding: 8px;
  }
  
  .summary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .summary-label, .summary-value {
    font-size: 12px;
  }
}
</style>