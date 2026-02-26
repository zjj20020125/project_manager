<template>
  <div class="ncr-flow-chart-container">
    <!-- 第一个容器：柱状图和饼图 -->
    <el-row :gutter="20" margin-bottom="20px">
      <el-col :span="12">
          <el-card shadow="hover" class="clickable-card" @click="goToTypeDetail">
            <div slot="header" class="card-header">NCR按类型/问题分类的分布统计</div>
            <div ref="typePieRef" class="chart-container"></div>
          </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="clickable-card">
          <div slot="header" class="card-header">未评审阶段责任人员分布（前十五名）</div>
          <div ref="unreviewedStageBarRef" class="chart-container"></div>
        </el-card>
      </el-col>

    </el-row>

    <!-- 第二个容器：柱状图和未操作者统计 -->
    <el-row :gutter="20" margin-bottom="20px">
      <el-col :span="12">
        <el-card shadow="hover" class="clickable-card">
          <div slot="header" class="card-header">NCR趋势统计</div>
          <div ref="trendBarRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="list-card">
          <div slot="header" class="card-header">
            <span>未操作者及其未处理数量统计</span>
          </div>
          <div class="scroll-list-container">
            <div class="scroll-list-content" :class="{ 'auto-scroll': wczzListData.length > 6 }" ref="wczzListRef">
              <div class="list-item" v-for="(item, index) in wczzListData" :key="index">
                <span class="name">{{ item.name }}</span>
                <span class="count">数量: {{ item.value }}</span>
              </div>
              <!-- 重复列表内容以实现无缝滚动 -->
              <div class="list-item" v-for="(item, index) in wczzListData" :key="`duplicate-${index}`">
                <span class="name">{{ item.name }}</span>
                <span class="count">数量: {{ item.value }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增：未处理类型分布统计模块 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <div slot="header" class="card-header">
            <span>未处理类型分布统计</span>
          </div>
          <div ref="dqjdBarRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header" class="card-header">NCR负责人统计</div>
          <el-table 
            :data="ncrOwnerStats" 
            border 
            style="width: 100%" 
            height="260"
            :fit="true"
            v-loading="ownerStatsLoading"
          >
            <el-table-column prop="owner_name" label="负责人姓名" align="center" header-align="center">
              <template #default="scope">
                <span 
                  style="color: #409EFF; cursor: pointer; text-decoration: underline; display: block; width: 100%;"
                >
                  {{ scope.row.owner_name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="ncr_count" label="NCR数量" align="center" header-align="center">
              <template #default="scope">
                <el-tag type="danger" style="text-align: center">{{ scope.row.ncr_count }} 项</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增：责任分析模块 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <div slot="header" class="card-header">评审阶段责任人员分布（前五名）</div>
          <div ref="responsibilityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三个容器：详细情况展示框 -->
    <el-card shadow="hover">
      <div slot="header" class="card-header">NCR详细情况展示</div>
      <div class="ncr-details-container">
        <el-table :data="ncrDetails" border style="width: 100%" v-loading="ncrDetailsLoading" header-align="center">
          <el-table-column prop="process_no" label="NCR编号" width="100" align="center" header-align="center" />
          <el-table-column 
            prop="defective_product_name" 
            label="缺陷产品名称" 
            min-width="150"
            align="center"
            header-align="center"
          >
            <template #default="scope">
              <span 
                style="color: #409EFF; cursor: pointer; text-decoration: underline;"
                @click="goToNcrDetail(scope.row.process_no)"
              >
                {{ scope.row.defective_product_name }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="product_no" label="产品编号" width="100" align="center" header-align="center" />
          <el-table-column prop="creator" label="创建人" width="100" align="center" header-align="center" />
          <el-table-column prop="create_date" label="创建日期" width="120" align="center" header-align="center" />
          <el-table-column prop="occurrence_date" label="发生日期" width="120" align="center" header-align="center" />
          <el-table-column prop="fsjd" label="发生阶段" width="100" align="center" header-align="center" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" header-align="center" />
          <el-table-column prop="problem_category" label="问题分类" width="120" align="center" header-align="center" />
          <el-table-column prop="problem_description" label="问题描述" min-width="150" show-overflow-tooltip align="center" header-align="center" />
          <el-table-column prop="status" label="状态" width="100" align="center" header-align="center" />
          <el-table-column prop="review_level" label="评审级别" width="100" align="center" header-align="center">
            <template #default="scope">
              <el-tag :type="getPriorityTagType(scope.row.review_level)">
                {{ scope.row.review_level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="更新时间" width="120" align="center" header-align="center" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, reactive, onActivated } from 'vue';
import * as echarts from 'echarts';
import { ElCard, ElRow, ElCol, ElTable, ElTableColumn, ElTag, vLoading } from 'element-plus';
import { projectApi } from '../../api/index.js';
import { useRouter } from 'vue-router';

export default {
  name: 'NcrFlowChart',
  components: {
    ElCard,
    ElRow,
    ElCol,
    ElTable,
    ElTableColumn,
    ElTag
  },
  setup() {
    const router = useRouter();
    
    // ECharts实例引用
    const unreviewedStagePieRef = ref(null);  // 未评审阶段责任人员分布扇形图引用
    const typePieRef = ref(null);
    const trendBarRef = ref(null);
    // 新增：DQJD图表和WCZZ列表引用
    const dqjdBarRef = ref(null);
    const wczzListRef = ref(null);
    // 新增：责任分析图表引用
    const responsibilityChartRef = ref(null);
    // 新增：未评审状态柱状图引用
    const unreviewedBarRef = ref(null);

    // 数据状态
    const unreviewedStageData = ref([]);  // 未评审阶段责任人员分布数据
    const ncrOwnerStats = ref([]);
    const ownerStatsLoading = ref(false);
    
    const ncrDetails = ref([]);
    const ncrDetailsLoading = ref(false);

    // 新增：DQJD和WCZZ数据
    const dqjdData = ref([]);
    const wczzListData = ref([]);
    // 新增：责任分析数据
    const responsibilityData = ref([]);
    // 新增：未评审状态数据
    const unreviewedData = ref([]);

    // 图表实例对象
    let unreviewedStagePieChart = null;  // 未评审阶段责任人员分布扇形图实例
    let typePieChart = null;
    let trendBarChart = null;
    // 新增：DQJD和WCZZ图表实例
    let dqjdChart = null;
    let wczzChart = null;
    // 新增：责任分析图表实例
    let responsibilityChart = null;
    // 新增：未评审状态柱状图实例
    let unreviewedBarChart = null;



    // 初始化评审阶段责任人员分布饼图
    const initTypePie = (data) => {
      if (!typePieRef.value) return;

      // 确保之前的图表实例已被销毁
      if (typePieChart) {
        try {
          typePieChart.dispose();
        } catch (e) {
          console.warn('Error disposing typePieChart:', e);
        }
        typePieChart = null;
      }

      typePieChart = echarts.init(typePieRef.value);

      // 定义一组对比明显的颜色，确保相邻数据颜色不会太相近
      const pieColors = [
        '#FF6B6B', // 红色
        '#4ECDC4', // 青绿色
        '#45B7D1', // 蓝色
        '#96CEB4', // 绿色
        '#FFEAA7', // 黄色
        '#DDA0DD', // 梅花色
        '#98D8C8', // 薄荷绿
        '#F7DC6F', // 浅黄色
        '#BB8FCE', // 浅紫色
        '#85C1E9'  // 浅蓝色
      ];

      const option = {
        tooltip: { 
          trigger: 'item',
          formatter: (params) => {
            return `${params.name}: ${params.value} (${((params.percent || 0) / 100).toFixed(2) * 100}%)`;
          }
        },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%' },
        legend: {
          bottom: 10,
          left: 'center',
          itemWidth: 12,
          itemHeight: 12
        },
        series: [
          {
            name: '评审阶段责任人员',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '40%'],
            data: data.map((item, index) => ({
              name: item.name,
              value: item.value,
              itemStyle: { 
                color: pieColors[index % pieColors.length] // 循环使用预定义颜色
              }
            })),
            label: { show: false },
            labelLine: { show: false },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            // 添加点击事件
            selectedMode: 'single',
            selectedOffset: 10
          }
        ]
      };
      typePieChart.setOption(option);
      
      // 添加点击事件监听
      typePieChart.on('click', (params) => {
        if (params && params.name) {
          router.push({
            name: 'NcrTypeDetail',
            params: { type: params.name }
          });
        }
      });
    };

    // 初始化NCR趋势柱状图
    const initTrendBar = (data) => {
      if (!trendBarRef.value) return;

      // 确保之前的图表实例已被销毁
      if (trendBarChart) {
        try {
          trendBarChart.dispose();
        } catch (e) {
          console.warn('Error disposing trendBarChart:', e);
        }
        trendBarChart = null;
      }

      trendBarChart = echarts.init(trendBarRef.value);

      const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '15%', top: '10%' },
        xAxis: {
          type: 'category',
          data: data.labels || ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: data.values || [12, 18, 15, 20, 25, 18],
          type: 'bar',
          itemStyle: { color: '#74b9ff' }
        }]
      };
      trendBarChart.setOption(option);
    };

    // 新增：初始化DQJD分布柱状图
    const initDqjdChart = (data) => {
      if (!dqjdBarRef.value) return;

      if (dqjdBarChart) {
        dqjdBarChart.dispose();
      }

      dqjdBarChart = echarts.init(dqjdBarRef.value);

      // 定义一组对比明显的颜色，确保相邻数据颜色不会太相近
      const barColors = [
        '#FF6B6B', // 红色
        '#4ECDC4', // 青绿色
        '#45B7D1', // 蓝色
        '#96CEB4', // 绿色
        '#FFEAA7', // 黄色
        '#DDA0DD', // 梅花色
        '#98D8C8', // 薄荷绿
        '#F7DC6F', // 浅黄色
        '#BB8FCE', // 浅紫色
        '#85C1E9'  // 浅蓝色
      ];

      // 为数据项添加颜色
      const coloredData = data.map((item, index) => ({
        ...item,
        itemStyle: {
          color: barColors[index % barColors.length]
        }
      }));

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: '{b}: {c}'
        },
        grid: { left: '15%', right: '4%', bottom: '25%', top: '10%', containLabel: true },
        xAxis: {
          type: 'category',
          data: coloredData.map(item => item.name),
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
          name: 'DQJD阶段分布',
          type: 'bar',
          data: coloredData,
          barWidth: '60%',
          label: {
            show: true,
            position: 'top',
            formatter: '{c}'
          }
        }]
      };

      dqjdBarChart.setOption(option);
    };

    // 新增：处理WCZZ数据并填充列表
    const updateWczzList = (data) => {
      // 按数量降序排序
      const sortedData = [...data].sort((a, b) => b.value - a.value);
      wczzListData.value = sortedData;
    };

    // 新增：初始化未评审阶段责任人员分布扇形图
    const initUnreviewedStagePieChart = (data) => {
      if (!unreviewedStagePieRef.value) return;

      if (unreviewedStagePieChart) {
        unreviewedStagePieChart.dispose();
      }

      unreviewedStagePieChart = echarts.init(unreviewedStagePieRef.value);

      // 定义一组对比明显的颜色，确保相邻数据颜色不会太相近
      const pieColors = [
        '#FF6B6B', // 红色
        '#4ECDC4', // 青绿色
        '#45B7D1', // 蓝色
        '#96CEB4', // 绿色
        '#FFEAA7', // 黄色
        '#DDA0DD', // 梅花色
        '#98D8C8', // 薄荷绿
        '#F7DC6F', // 浅黄色
        '#BB8FCE', // 浅紫色
        '#85C1E9', // 浅蓝色
        '#5470c6', // 蓝色
        '#91cc75', // 绿色
        '#fac858', // 黄色
        '#ee6666', // 红色
        '#73c0de'  // 浅蓝色
      ];

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          left: 'center',
          bottom: 0,
          itemGap: 5
        },
        series: [{
          name: '责任人员分布',
          type: 'pie',
          radius: ['40%', '60%'],
          center: ['50%', '40%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2,
            color: function(params) {
              // 循环使用预定义颜色
              return pieColors[params.dataIndex % pieColors.length];
            }
          },
          label: {
            show: true,
            formatter: '{b}: {c}',
            minMargin: 5
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          data: data
        }]
      };

      unreviewedStagePieChart.setOption(option);
    };

    // 新增：初始化责任分析饼图
    const initResponsibilityChart = (data) => {
      if (!responsibilityChartRef.value) return;

      if (responsibilityChart) {
        responsibilityChart.dispose();
      }

      responsibilityChart = echarts.init(responsibilityChartRef.value);

      // 定义一组对比明显的颜色，确保相邻数据颜色不会太相近
      const pieColors = [
        '#FF6B6B', // 红色
        '#4ECDC4', // 青绿色
        '#45B7D1', // 蓝色
        '#96CEB4', // 绿色
        '#FFEAA7', // 黄色
        '#DDA0DD', // 梅花色
        '#98D8C8', // 薄荷绿
        '#F7DC6F', // 浅黄色
        '#BB8FCE', // 浅紫色
        '#85C1E9'  // 浅蓝色
      ];

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          left: 'center',
          bottom: 0,
          itemGap: 5
        },
        series: [{
          name: '责任人员分布',
          type: 'pie',
          radius: ['40%', '60%'],
          center: ['50%', '40%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2,
            color: function(params) {
              // 循环使用预定义颜色
              return pieColors[params.dataIndex % pieColors.length];
            }
          },
          label: {
            show: true,
            formatter: '{b}: {c}',
            minMargin: 5
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            }
          },
          data: data
        }]
      };

      responsibilityChart.setOption(option);
    };

    // 根据阶段获取颜色
    const getColorForStage = (stage) => {
      const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
      return colors[Math.abs(hashCode(stage)) % colors.length];
    };

    // 根据状态获取颜色
    const getColorForStatus = (status) => {
      switch(status) {
        case '待处理':
          return '#e6a23c'; // 橙色
        case '处理中':
          return '#409eff'; // 蓝色
        case '待审核':
          return '#f56c6c'; // 红色
        case '已完成':
          return '#67c23a'; // 绿色
        default:
          return '#909399'; // 灰色
      }
    };

    // 根据类型获取颜色
    const getColorForType = (type) => {
      const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
      return colors[Math.abs(hashCode(type)) % colors.length];
    };

    // 简单的哈希函数
    const hashCode = (str) => {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return Math.abs(hash);
    };

    // 获取优先级标签类型
    const getPriorityTagType = (priority) => {
      if (!priority) return 'info';
      
      switch (priority.toLowerCase()) {
        case '高':
        case '一级':
          return 'danger';
        case '中':
        case '二级':
          return 'warning';
        case '低':
          return 'success';
        default:
          return 'info';
      }
    };

    // 获取NCR统计数据
    const fetchNcrData = async () => {
      try {
        // 获取未评审阶段责任人员分布数据
        try {
          const unreviewedStageResponse = await projectApi.getUnreviewedStageResponsibility();
          if (unreviewedStageResponse && Array.isArray(unreviewedStageResponse)) {
            unreviewedStageData.value = unreviewedStageResponse;
            // 初始化未评审阶段责任人员分布扇形图
            initUnreviewedStagePieChart(unreviewedStageResponse);
          }
        } catch (error) {
          console.error('获取未评审阶段责任人员分布数据失败:', error);
          // 如果API调用失败，使用模拟数据
          const mockData = [
            { name: '张三', value: 15 },
            { name: '李四', value: 12 },
            { name: '王五', value: 10 },
            { name: '赵六', value: 8 },
            { name: '孙七', value: 6 },
            { name: '周八', value: 5 },
            { name: '吴九', value: 4 },
            { name: '郑十', value: 3 }
          ];
          unreviewedStageData.value = mockData;
          initUnreviewedStagePieChart(mockData);
        }

        // 获取NCR类型分布统计（用于饼图显示）
        try {
          const typeDistributionResponse = await projectApi.getNcrTypeDistribution();
          if (typeDistributionResponse && Array.isArray(typeDistributionResponse)) {
            // 初始化类型分布饼图
            initTypePie(typeDistributionResponse);
          }
        } catch (error) {
          console.error('获取NCR类型分布数据失败:', error);
          // 如果API调用失败，使用模拟数据
          const mockTypeData = [
            { name: '产品质量', value: 25 },
            { name: '工艺问题', value: 18 },
            { name: '材料问题', value: 15 },
            { name: '设备问题', value: 12 },
            { name: '人员问题', value: 8 }
          ];
          initTypePie(mockTypeData);
        }

        // 获取NCR列表 - 从API获取真实数据
        ncrDetailsLoading.value = true;
        try {
          const ncrListResponse = await projectApi.getNcrList({ page: 1, limit: 20 });
          if (ncrListResponse && Array.isArray(ncrListResponse)) {
            ncrDetails.value = ncrListResponse;
          } else {
            ncrDetails.value = [];
          }
        } catch (error) {
          console.error('获取NCR列表失败:', error);
          ncrDetails.value = [];
        }

        // 获取DQJD和WCZZ数据
        try {
          const dqjdWczzResponse = await projectApi.getDqjdWczzData();
          if (dqjdWczzResponse) {
            // 初始化DQJD图表
            const dqjdData = dqjdWczzResponse.dqjdStats || [];
            initDqjdChart(dqjdData);

            // 初始化WCZZ图表
            const wczzData = dqjdWczzResponse.wczzStats || [];
            updateWczzList(wczzData);
          }
        } catch (error) {
          console.error('获取DQJD/WCZZ数据失败:', error);
        }

        // 注意：责任分析数据已经在上面获取并初始化了，这里不再重复获取
        // 获取责任分析数据（使用正确的API获取数据）
        try {
          const responsibilityResponse = await projectApi.getResponsibilityAnalysis();
          if (responsibilityResponse) {
            // 初始化责任分析图表
            initResponsibilityChart(responsibilityResponse);
          }
        } catch (error) {
          console.error('获取责任分析数据失败:', error);
        }

        // 模拟负责人统计数据（实际应用中可以从后端获取）
        ncrOwnerStats.value = [
          { owner_name: '张三', ncr_count: 12 },
          { owner_name: '李四', ncr_count: 8 },
          { owner_name: '王五', ncr_count: 15 },
          { owner_name: '赵六', ncr_count: 5 },
          { owner_name: '孙七', ncr_count: 10 }
        ];

        // 初始化趋势图（使用模拟数据，实际应用中可以使用时间序列数据）
        const trendData = {
          labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
          values: [12, 18, 15, 20, 25, 18]
        };
        initTrendBar(trendData);

      } catch (error) {
        console.error('获取NCR数据失败:', error);
      } finally {
        ncrDetailsLoading.value = false;
      }
    };

    // 新增：获取SSCX统计数据
    const fetchSscxData = async () => {
      sscxLoading.value = true;
      try {
        // 获取SSCX统计数据
        const sscxResponse = await projectApi.getSscxStatistics();
        console.log('NcrFlowChart - SSCX Response:', sscxResponse);
        if (Array.isArray(sscxResponse) && sscxResponse.length > 0) {
          sscxData.value = sscxResponse;
          console.log('NcrFlowChart - SSCX Data set:', sscxData.value);
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

        // 获取趋势数据
        const trendResponse = await projectApi.getSscxTrendStatistics();
        console.log('NcrFlowChart - SSCX Trend Response:', trendResponse);
        if (Array.isArray(trendResponse) && trendResponse.length > 0) {
          sscxTrendData.value = trendResponse;
          console.log('NcrFlowChart - SSCX Trend Data set:', sscxTrendData.value);
          initSscxTrendChart(trendResponse);
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
      } catch (error) {
        console.error('获取SSCX统计数据失败:', error);
        // 使用模拟数据作为降级方案
        const mockSscxData = [
          { name: '类型A', value: 25 },
          { name: '类型B', value: 18 },
          { name: '类型C', value: 15 },
          { name: '类型D', value: 12 },
          { name: '类型E', value: 8 }
        ];
        sscxData.value = mockSscxData;
        initSscxPieChart(mockSscxData);
        
        const months = ['2023-09', '2023-10', '2023-11', '2023-12', '2024-01', '2024-02'];
        const mockTrendData = months.map((month, index) => ({
          month: month,
          total: 20 + Math.floor(Math.random() * 15)
        }));
        sscxTrendData.value = mockTrendData;
        initSscxTrendChart(mockTrendData);
      } finally {
        sscxLoading.value = false;
      }
    };

    const refreshSscxData = () => {
      fetchSscxData();
    };

    // 新增：SSCX饼图初始化
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
          data: data.map((item, index) => ({
            name: item.name,
            value: item.value,
            itemStyle: {
              color: getColorByIndex(index)
            }
          }))
        }]
      };
      
      sscxPieChart.setOption(option);
    };

    // 新增：SSCX趋势图初始化
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

    // 辅助方法：获取颜色
    const getColorByIndex = (index) => {
      const colors = [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6'
      ];
      return colors[index % colors.length];
    };

    // 窗口大小调整处理
    const handleResize = () => {
      if (typePieChart) typePieChart.resize();
      if (trendBarChart) trendBarChart.resize();
      if (dqjdChart) dqjdChart.resize();
      if (responsibilityChart) responsibilityChart.resize();
      if (unreviewedBarChart) unreviewedBarChart.resize();
      if (sscxPieChart) sscxPieChart.resize(); // 新增
      if (sscxTrendChart) sscxTrendChart.resize(); // 新增
    };

    // 跳转到阶段详情页
    const goToStageDetail = () => {
      router.push({ name: 'NcrStageDetail' });
    };

    // 跳转到类型详情页
    const goToTypeDetail = () => {
      router.push({ name: 'NcrTypeDetail' });
    };

    // 跳转到NCR项目详情页
    const goToNcrDetail = (processNo) => {
      router.push({
        name: 'NcrItemDetail',
        params: { processNo: processNo }
      });
    };

    onMounted(() => {
      fetchNcrData();
      fetchSscxData(); // 新增：加载SSCX数据
      window.addEventListener('resize', handleResize);
    });

    // 当组件卸载时
    onUnmounted(() => {
      if (typePieChart) typePieChart.dispose();
      if (trendBarChart) trendBarChart.dispose();
      if (dqjdChart) dqjdChart.dispose();
      if (responsibilityChart) responsibilityChart.dispose();
      if (unreviewedBarChart) unreviewedBarChart.dispose();
      if (sscxPieChart) sscxPieChart.dispose(); // 新增
      if (sscxTrendChart) sscxTrendChart.dispose(); // 新增
      window.removeEventListener('resize', handleResize);
    });

    // 当组件被激活时（例如从其他页面返回），重新获取数据
    onActivated(() => {
      fetchNcrData();
    });

    return {
      unreviewedStagePieRef,  // 未评审阶段责任人员分布图表ref
      typePieRef,
      trendBarRef,
      // 修复：返回正确的DQJD ref名称
      dqjdBarRef,
      // 新增：返回WCZZ列表ref
      wczzListRef,
      wczzListData,
      ncrOwnerStats,
      ownerStatsLoading,
      ncrDetails,
      ncrDetailsLoading,
      // 新增：返回未评审状态柱状图ref
      unreviewedBarRef,
      unreviewedData,
      unreviewedStageData,
      getPriorityTagType,
      goToStageDetail,
      goToTypeDetail,
      goToNcrDetail,
      // 新增：返回SSCX相关引用和方法
      sscxPieRef,
      sscxTrendRef,
      sscxData,
      sscxTrendData,
      sscxLoading,
      sscxTotalCount,
      topSscxCategory,
      refreshSscxData
    };
  }
};
</script>

<style scoped>
.ncr-flow-chart-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.chart-container {
  width: 100%;
  height: 260px;
}

.ncr-details-container {
  width: 100%;
}

.clickable-card {
  cursor: pointer;
}

.card-header {
  font-weight: bold;
  color: #303133;
}

/* 新增：DQJD/WCZZ模块样式 */
.module-content {
  margin: 20px 0;
}

.chart-card {
  height: 400px;
}

.list-card {
  height: 400px;
}

.scroll-list-container {
  height: 300px;
  overflow: hidden;
  position: relative;
}

.scroll-list-content {
  height: auto;
}

.auto-scroll {
  animation: scroll-up 20s linear infinite;
}

@keyframes scroll-up {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-50%);
  }
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s;
}

.list-item:hover {
  background-color: #f5f7fa;
}

.name {
  font-weight: 500;
  color: #303133;
}

.count {
  font-weight: bold;
  color: #f56c6c;
}

/* 新增：SSCX统计模块样式 */
.sscx-overview {
  display: flex;
  justify-content: space-around;
  padding: 15px 0;
  border-top: 1px solid #eee;
  margin-top: 10px;
}

.overview-item {
  text-align: center;
}

.label {
  font-size: 12px;
  color: #606266;
  display: block;
  margin-bottom: 5px;
}

.value {
  font-size: 14px;
  font-weight: bold;
  color: #409EFF;
  display: block;
}
</style>