/**
 * SSCX数据处理器
 * 专门处理SSCX统计和趋势数据的转换逻辑
 */

/**
 * 将SSCX统计字典数据转换为ECharts兼容格式
 * @param {Object} data - 原始数据 {项目名: 数值}
 * @param {Object} options - 配置选项
 * @returns {Array} 转换后的数据 [{name: 项目名, value: 数值}]
 */
export const convertSscxStatisticsData = (data, options = {}) => {
  const {
    sortBy = 'value', // 排序方式: 'value'(数值) 或 'name'(名称)
    sortOrder = 'desc', // 排序顺序: 'asc' 或 'desc'
    limit = null, // 限制返回数量
    minValue = 0, // 最小值过滤
    excludeZero = false // 是否排除零值
  } = options;

  if (!data || typeof data !== 'object') {
    console.warn('SSCX统计数据格式无效:', data);
    return [];
  }

  // 转换为数组格式
  let result = Object.entries(data).map(([name, value]) => ({
    name: name,
    value: Number(value) || 0
  }));

  // 过滤零值
  if (excludeZero) {
    result = result.filter(item => item.value > 0);
  }

  // 最小值过滤
  if (minValue > 0) {
    result = result.filter(item => item.value >= minValue);
  }

  // 排序
  if (sortBy === 'value') {
    result.sort((a, b) => sortOrder === 'desc' ? b.value - a.value : a.value - b.value);
  } else {
    result.sort((a, b) => sortOrder === 'desc' ? 
      b.name.localeCompare(a.name, 'zh-CN') : 
      a.name.localeCompare(b.name, 'zh-CN'));
  }

  // 限制数量
  if (limit && limit > 0) {
    result = result.slice(0, limit);
  }

  console.log('SSCX统计数据转换完成:', {
    原始数据项数: Object.keys(data).length,
    转换后数据项数: result.length,
    排序方式: `${sortBy}-${sortOrder}`,
    过滤条件: { minValue, excludeZero, limit }
  });

  return result;
};

/**
 * 将SSCX趋势数据转换为ECharts时间序列格式
 * @param {Array} data - 原始趋势数据 [{month: 'YYYY-MM', 项目1: 值1, 项目2: 值2, ...}]
 * @param {Object} options - 配置选项
 * @returns {Object} 转换后的数据 {months: [], series: []}
 */
export const convertSscxTrendData = (data, options = {}) => {
  const {
    projectNames = [], // 指定要提取的项目名称
    aggregate = false, // 是否聚合所有项目为总计
    formatMonth = true // 是否格式化月份显示
  } = options;

  if (!Array.isArray(data) || data.length === 0) {
    console.warn('SSCX趋势数据为空或格式无效:', data);
    return { months: [], series: [] };
  }

  // 提取月份
  const months = data.map(item => item.month || '');
  
  // 格式化月份显示
  const formattedMonths = formatMonth ? 
    months.map(month => {
      if (!month) return '';
      const [year, monthNum] = month.split('-');
      return `${year}年${parseInt(monthNum)}月`;
    }) : months;

  let series = [];

  if (aggregate) {
    // 聚合模式：计算每月总和
    const totals = data.map(item => {
      return Object.entries(item)
        .filter(([key]) => key !== 'month')
        .reduce((sum, [, value]) => sum + (Number(value) || 0), 0);
    });

    series.push({
      name: '总计',
      type: 'line',
      data: totals,
      smooth: true,
      symbolSize: 6,
      lineStyle: {
        width: 3
      }
    });
  } else {
    // 分项目模式：提取指定项目或所有项目
    const projectsToProcess = projectNames.length > 0 ? projectNames : 
      Object.keys(data[0]).filter(key => key !== 'month');

    projectsToProcess.forEach(projectName => {
      const projectData = data.map(item => {
        const value = item[projectName];
        return value !== undefined ? Number(value) || 0 : 0;
      });

      // 只添加有数据的项目
      if (projectData.some(val => val > 0)) {
        series.push({
          name: projectName,
          type: 'line',
          data: projectData,
          smooth: true,
          symbolSize: 4
        });
      }
    });
  }

  console.log('SSCX趋势数据转换完成:', {
    时间点数: months.length,
    系列数: series.length,
    模式: aggregate ? '聚合总计' : '分项目显示',
    月份范围: `${months[0]} 至 ${months[months.length - 1]}`
  });

  return {
    months: formattedMonths,
    series: series
  };
};

/**
 * 获取SSCX数据的统计摘要
 * @param {Object|Array} data - SSCX数据
 * @param {boolean} isTrend - 是否为趋势数据
 * @returns {Object} 统计信息
 */
export const getSscxDataSummary = (data, isTrend = false) => {
  if (!data) return {};

  if (isTrend) {
    // 趋势数据统计
    if (!Array.isArray(data) || data.length === 0) return {};
    
    const months = data.map(item => item.month);
    const totalValues = data.map(item => 
      Object.entries(item)
        .filter(([key]) => key !== 'month')
        .reduce((sum, [, value]) => sum + (Number(value) || 0), 0)
    );

    return {
      数据点数: data.length,
      时间范围: `${months[0]} 至 ${months[months.length - 1]}`,
      总计最高值: Math.max(...totalValues),
      总计最低值: Math.min(...totalValues),
      总计平均值: totalValues.reduce((sum, val) => sum + val, 0) / totalValues.length
    };
  } else {
    // 统计数据摘要
    if (typeof data !== 'object') return {};

    const entries = Object.entries(data);
    const values = entries.map(([, value]) => Number(value) || 0);
    const nonZeroEntries = entries.filter(([, value]) => (Number(value) || 0) > 0);

    return {
      项目总数: entries.length,
      非零项目数: nonZeroEntries.length,
      最高值: Math.max(...values),
      最低值: Math.min(...values.filter(val => val > 0)),
      总计: values.reduce((sum, val) => sum + val, 0),
      平均值: nonZeroEntries.length > 0 ? 
        values.filter(val => val > 0).reduce((sum, val) => sum + val, 0) / nonZeroEntries.length : 0
    };
  }
};

/**
 * 生成SSCX数据的可视化配置
 * @param {string} chartType - 图表类型 ('pie', 'bar', 'line')
 * @param {Object} options - 配置选项
 * @returns {Object} ECharts配置对象
 */
export const getSscxChartConfig = (chartType, options = {}) => {
  const {
    title = '',
    showLegend = true,
    colorPalette = [],
    animation = true,
    theme = 'light'
  } = options;

  const defaultColors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6'
  ];

  const colors = colorPalette.length > 0 ? colorPalette : defaultColors;

  const baseConfig = {
    title: {
      text: title,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: theme === 'dark' ? '#fff' : '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: chartType === 'line' ? 
        '{b}<br/>{a}: {c}' : 
        '{b}: {c} ({d}%)'
    },
    animation: animation,
    color: colors
  };

  if (showLegend) {
    baseConfig.legend = {
      show: true,
      type: 'scroll',
      orient: 'horizontal',
      bottom: 10,
      textStyle: {
        fontSize: 12
      }
    };
  }

  switch (chartType) {
    case 'pie':
      return {
        ...baseConfig,
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          avoidLabelOverlap: true,
          label: {
            show: true,
            formatter: '{b}\n{d}%'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            }
          }
        }]
      };

    case 'bar':
      return {
        ...baseConfig,
        xAxis: {
          type: 'category',
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          type: 'bar',
          barWidth: '60%',
          label: {
            show: true,
            position: 'top'
          }
        }]
      };

    case 'line':
      return {
        ...baseConfig,
        xAxis: {
          type: 'category',
          boundaryGap: false
        },
        yAxis: {
          type: 'value'
        },
        series: []
      };

    default:
      return baseConfig;
  }
};

// 默认导出
export default {
  convertSscxStatisticsData,
  convertSscxTrendData,
  getSscxDataSummary,
  getSscxChartConfig
};