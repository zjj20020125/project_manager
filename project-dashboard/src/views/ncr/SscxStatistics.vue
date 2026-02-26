<template>
  <div class="sscx-statistics-container">
    <el-card class="statistics-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📊 SSCX字段统计分析</span>
          <el-button 
            type="primary" 
            @click="refreshData" 
            :loading="loading"
            size="small"
            icon="Refresh"
          >
            刷新数据
          </el-button>
        </div>
      </template>
      
      <!-- 统计概览 -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="overview-card">
              <div class="overview-item">
                <div class="overview-label">统计类别数</div>
                <div class="overview-value">{{ sscxData.length }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="overview-card">
              <div class="overview-item">
                <div class="overview-label">总记录数</div>
                <div class="overview-value">{{ totalRecords }}</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="overview-card">
              <div class="overview-item">
                <div class="overview-label">最热门类别</div>
                <div class="overview-value" v-if="topCategory">{{ topCategory.name }}</div>
                <div class="overview-subvalue" v-if="topCategory">({{ topCategory.value }}项)</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表展示区域 -->
      <el-row :gutter="20" class="charts-section">
        <!-- 饼图展示 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>🥧 SSCX类别分布饼图</span>
              </div>
            </template>
            <div ref="pieChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 横向柱状图 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>📊 SSCX类别横向柱状图</span>
              </div>
            </template>
            <div ref="barChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 趋势分析区域 -->
      <el-card class="trend-card" v-if="trendData.length > 0">
        <template #header>
          <div class="chart-header">
            <span>📈 近一年SSCX趋势分析</span>
          </div>
        </template>
        <div ref="trendChartRef" class="trend-chart-container"></div>
      </el-card>

      <!-- 详细数据表格 -->
      <el-card class="data-table-card">
        <template #header>
          <div class="table-header">
            <span>📋 详细统计表格</span>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索类别名称..."
              style="width: 200px; margin-left: 20px;"
              clearable
              @input="filterData"
            >
              <template #prefix>
                <i class="el-icon-search"></i>
              </template>
            </el-input>
          </div>
        </template>
        
        <el-table 
          :data="filteredData" 
          border 
          style="width: 100%"
          :default-sort="{prop: 'value', order: 'descending'}"
        >
          <el-table-column prop="name" label="类别名称" min-width="200" show-overflow-tooltip>
            <template #default="scope">
              <el-tag type="primary">{{ scope.row.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column 
            prop="value" 
            label="数量" 
            width="120" 
            sortable
            align="center"
          >
            <template #default="scope">
              <el-tag type="success">{{ scope.row.value }} 项</el-tag>
            </template>
          </el-table-column>
          <el-table-column 
            label="占比" 
            width="120" 
            align="center"
          >
            <template #default="scope">
              <el-progress 
                :percentage="(scope.row.value / totalRecords * 100)" 
                :stroke-width="10"
                :show-text="false"
              />
              <div class="percentage-text">
                {{ (scope.row.value / totalRecords * 100).toFixed(1) }}%
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container" v-if="filteredData.length > 10">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredData.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
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
  ElPagination, 
  ElMessage,
  ElProgress
} from 'element-plus';
import { projectApi } from '../../api/index.js';

// 响应式数据
const loading = ref(false);
const sscxData = ref([]);
const trendData = ref([]);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(10);

// 图表引用
const pieChartRef = ref(null);
const barChartRef = ref(null);
const trendChartRef = ref(null);

// 图表实例
let pieChart = null;
let barChart = null;
let trendChart = null;

// 计算属性
const totalRecords = computed(() => {
  return sscxData.value.reduce((sum, item) => sum + item.value, 0);
});

const topCategory = computed(() => {
  if (sscxData.value.length === 0) return null;
  return sscxData.value.reduce((prev, current) => 
    (prev.value > current.value) ? prev : current
  );
});

const filteredData = computed(() => {
  if (!searchKeyword.value) return sscxData.value;
  
  const keyword = searchKeyword.value.toLowerCase();
  return sscxData.value.filter(item => 
    item.name.toLowerCase().includes(keyword)
  );
});

// 分页相关方法
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
};

const filterData = () => {
  currentPage.value = 1;
};

// 数据获取方法
const fetchData = async () => {
  loading.value = true;
  try {
    // 获取SSCX统计数据
    const sscxResponse = await projectApi.getSscxStatistics();
    if (Array.isArray(sscxResponse)) {
      sscxData.value = sscxResponse;
      initPieChart(sscxResponse);
      initBarChart(sscxResponse);
    }

    // 获取趋势数据
    const trendResponse = await projectApi.getSscxTrendStatistics();
    if (Array.isArray(trendResponse)) {
      trendData.value = trendResponse;
      initTrendChart(trendResponse);
    }

    ElMessage.success('数据加载成功');
  } catch (error) {
    console.error('获取SSCX统计数据失败:', error);
    ElMessage.error('数据加载失败');
  } finally {
    loading.value = false;
  }
};

const refreshData = () => {
  fetchData();
};

// 图表初始化方法
const initPieChart = (data) => {
  if (!pieChartRef.value || !data || data.length === 0) return;
  
  if (pieChart) pieChart.dispose();
  pieChart = echarts.init(pieChartRef.value);
  
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
      data: data.map((item, index) => ({
        name: item.name,
        value: item.value,
        itemStyle: {
          color: getColorByIndex(index)
        }
      }))
    }]
  };
  
  pieChart.setOption(option);
};

const initBarChart = (data) => {
  if (!barChartRef.value || !data || data.length === 0) return;
  
  if (barChart) barChart.dispose();
  barChart = echarts.init(barChartRef.value);
  
  // 按数量排序，取前15个
  const sortedData = [...data].sort((a, b) => b.value - a.value).slice(0, 15);
  
  const option = {
    title: {
      text: 'SSCX类别排行',
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
        const percentage = ((item.value / totalRecords.value) * 100).toFixed(1);
        return `${item.name}<br/>数量: ${item.value}项<br/>占比: ${percentage}%`;
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
      data: sortedData.map(item => item.name),
      axisLabel: {
        interval: 0,
        rotate: 0
      }
    },
    series: [{
      type: 'bar',
      data: sortedData.map((item, index) => ({
        value: item.value,
        itemStyle: {
          color: echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: getColorByIndex(index) },
            { offset: 1, color: lightenColor(getColorByIndex(index), 0.3) }
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
        focus: 'series'
      }
    }]
  };
  
  barChart.setOption(option);
};

const initTrendChart = (data) => {
  if (!trendChartRef.value || !data || data.length === 0) return;
  
  if (trendChart) trendChart.dispose();
  trendChart = echarts.init(trendChartRef.value);
  
  // 提取月份和总量数据
  const months = data.map(item => item.month);
  const totals = data.map(item => item.total);
  
  // 提取前5个主要类别作为系列
  const topCategories = Object.keys(data[0] || {})
    .filter(key => !['month', 'total'].includes(key))
    .sort((a, b) => {
      const sumA = data.reduce((sum, item) => sum + (item[a] || 0), 0);
      const sumB = data.reduce((sum, item) => sum + (item[b] || 0), 0);
      return sumB - sumA;
    })
    .slice(0, 5);
  
  const series = topCategories.map((category, index) => ({
    name: category,
    type: 'line',
    data: data.map(item => item[category] || 0),
    smooth: true,
    itemStyle: { color: getColorByIndex(index) },
    areaStyle: { opacity: 0.1 }
  }));
  
  // 添加总量线
  series.unshift({
    name: '总量',
    type: 'line',
    data: totals,
    smooth: true,
    itemStyle: { color: '#333' },
    lineStyle: { width: 3 }
  });
  
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
        let result = `${params[0].name}<br/>`;
        params.forEach(param => {
          result += `${param.marker} ${param.seriesName}: ${param.value}项<br/>`;
        });
        return result;
      }
    },
    legend: {
      data: ['总量', ...topCategories],
      top: 30
    },
    grid: {
      left: '5%',
      right: '5%',
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
    series: series
  };
  
  trendChart.setOption(option);
};

// 辅助方法
const getColorByIndex = (index) => {
  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6'
  ];
  return colors[index % colors.length];
};

const lightenColor = (color, percent) => {
  const num = parseInt(color.replace("#", ""), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
};

// 窗口大小调整处理
const handleResize = () => {
  if (pieChart) pieChart.resize();
  if (barChart) barChart.resize();
  if (trendChart) trendChart.resize();
};

// 生命周期钩子
onMounted(() => {
  fetchData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (pieChart) pieChart.dispose();
  if (barChart) barChart.dispose();
  if (trendChart) trendChart.dispose();
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.sscx-statistics-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.statistics-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #303133;
}

.overview-section {
  margin-bottom: 30px;
}

.overview-card {
  height: 100px;
}

.overview-item {
  text-align: center;
  padding: 15px 0;
}

.overview-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.overview-subvalue {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 400px;
}

.trend-card {
  height: 500px;
  margin-bottom: 30px;
}

.data-table-card {
  margin-bottom: 20px;
}

.chart-header, .table-header {
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
}

.table-header {
  justify-content: space-between;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.trend-chart-container {
  width: 100%;
  height: 420px;
}

.percentage-text {
  text-align: center;
  font-size: 12px;
  color: #606266;
  margin-top: 5px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>