# NCR Dashboard API问题修复说明

## 问题描述

在访问NCR增强看板页面时,前端日志显示以下错误:

```
原始 SSCX 统计响应类型: object 值: []
原始 SSCX 趋势响应类型: object 值: []
SSCX 年度统计响应类型: object 值: []
⚠️ 问题导向统计数据为空或格式无效，使用模拟数据
```

## 根本原因分析

### 1. 数据库字段缺失
通过运行`check_ncr_data.py`诊断脚本发现:
- ✅ `sscx`字段存在且有5861条有效数据
- ✅ `cjrq`时间字段存在
- ✅ `wtdx`(问题导向)和`wtfl`(问题分类)字段存在
- ❌ `wtflxf`(问题分类细分)字段**不存在**

### 2. API路由未注册
`problem-hierarchy-stats` API定义在`main/routers/ncr_router.py`中,但该路由器未被主应用注册。

## 修复方案

### 修复1: 兼容缺失的wtflxf字段

**文件**: `project-backend/main/routers/ncr_router.py`

**修改内容**:
```python
# 修改前: 要求三个字段都必须存在
required_fields = ['wtdx', 'wtfl', 'wtflxf']
missing_fields = [field for field in required_fields if field not in column_names]
if missing_fields:
    print(f"警告：缺少必要字段：{', '.join(missing_fields)}")
    return []

# 修改后: wtflxf作为可选字段
required_fields = ['wtdx', 'wtfl']
optional_fields = ['wtflxf']
missing_required = [field for field in required_fields if field not in column_names]

if missing_required:
    print(f"警告：缺少必要字段：{', '.join(missing_required)}")
    return []

has_wtflxf = 'wtflxf' in column_names
```

然后在构建三层级数据结构时,添加条件判断:
```python
wtflxf_children = []

if has_wtflxf:
    # 查询该 wtfl 下的 wtflxf 分布
    wtflxf_sql = f"""..."""
    wtflxf_results = execute_query(wtflxf_sql, (wtdx_name, wtfl_name), fetch_all=True) or []
    
    for wtflxf_record in wtflxf_results:
        wtflxf_children.append({
            "name": wtflxf_record.get('wtflxf', '未知细分'),
            "value": wtflxf_record.get('count', 0)
        })

# 构建 wtfl 层级(即使没有wtflxf也能正常工作)
wtfl_children.append({
    "name": wtfl_name,
    "value": wtfl_count,
    "children": wtflxf_children  # 可能为空数组
})
```

### 修复2: 注册NCR增强功能路由

**文件**: `project-backend/main/modular_main.py`

**修改内容**:
```python
# 导入NCR增强功能路由
from main.routers.ncr_router import router as ncr_enhanced_router  # NCR增强功能路由

# 注册路由
app.include_router(ncr_router)
app.include_router(ncr_enhanced_router)  # NCR增强功能路由(问题导向统计等)
```

## 验证结果

运行`test_sscx_api.py`测试脚本,所有API正常返回数据:

```
✅ /v1/ncr/sscx-statistics - 返回1772条数据
✅ /v1/ncr/sscx-trend - 返回11个月的数据
✅ /v1/ncr/sscx-yearly-stats - 返回前15名项目
✅ /v1/ncr/problem-hierarchy-stats - 返回6个问题导向分类及子层级
```

## 数据示例

### SSCX年度统计(前5名)
```json
[
  {"name": "CR200J动集", "value": 80},
  {"name": "马来西亚3CS", "value": 67},
  {"name": "川藏线", "value": 60},
  {"name": "/", "value": 54},
  {"name": "澳大利亚机车", "value": 52}
]
```

### 问题导向三层级统计
```json
[
  {
    "name": "制造",
    "value": 1762,
    "children": [
      {
        "name": "加工工艺",
        "value": xxx,
        "children": []  // wtflxf字段不存在,所以为空
      }
    ]
  },
  {
    "name": "客户",
    "value": 1364,
    "children": [...]
  }
]
```

## 后续建议

### 短期优化
1. 如果确实需要三层级结构,可以在数据库中添加`wtflxf`字段
2. 为空的第三层级提供默认提示文本

### 长期改进
1. 建立API健康检查机制,定期监控接口可用性
2. 添加更详细的错误日志,便于快速定位问题
3. 考虑为关键API添加缓存机制,提升性能

## 相关文件清单

### 后端文件
- `project-backend/main/routers/ncr_router.py` - NCR增强功能API(问题导向统计)
- `project-backend/main/ncr_apis.py` - NCR基础API(SSCX统计、趋势等)
- `project-backend/main/modular_main.py` - 主应用入口(路由注册)

### 前端文件
- `project-dashboard/src/views/ncr/NcrEnhancedDashboard.vue` - NCR增强看板页面
- `project-dashboard/src/api/index.js` - API调用封装

### 诊断工具
- `check_ncr_data.py` - 数据库结构和数据检查脚本
- `test_sscx_api.py` - API接口测试脚本

## 注意事项

1. **浏览器扩展干扰**: 日志中的`Uncaught (in promise) Error: A listener indicated an asynchronous response...`是浏览器扩展引起的,不影响功能,可以忽略或临时禁用相关扩展。

2. **模拟数据降级**: 前端代码已实现完善的降级机制,即使API失败也会显示模拟数据,保证用户体验。

3. **服务重启**: 修改后端代码后,FastAPI的`--reload`模式会自动重新加载,无需手动重启。

---

**修复日期**: 2026-05-06  
**修复人员**: AI Assistant  
**影响范围**: NCR增强看板页面的SSCX统计和问题导向旭日图
