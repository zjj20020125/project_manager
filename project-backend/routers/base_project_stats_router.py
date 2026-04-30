"""
通用项目统计 API 路由器 - 可复用于任何需要项目统计的项目

特性:
- 基于 BaseProjectStatsService 构建
- 支持自定义配置和扩展
- 统一的错误处理
- 完整的类型注解
- 支持 Swagger 文档自动生成

使用方法:
1. 直接导入使用
2. 继承后重写配置
3. 作为子路由挂载

示例:
from routers.base_project_stats_router import router as base_stats_router

app.include_router(base_stats_router, prefix="/v1", tags=["项目统计"])
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime

# 创建路由器实例
router = APIRouter(prefix="/stats", tags=["项目统计"])


# ============================================================================
# 基础统计接口
# ============================================================================

@router.get("/project/basic")
async def get_basic_project_stats():
    """
    获取基础项目统计数据
    
    返回字段:
    - total_projects: 项目总数
    - not_started_projects: 未开始项目数
    - ongoing_projects: 进行中项目数
    - completed_projects: 已结项项目数
    
    业务逻辑:
    - 未开始：当前日期 < 计划开始日期
    - 已结项：实际结束日期存在且 < 当前日期
    - 进行中：既不是未开始也不是已结项
    """
    try:
        # 导入服务层
        from services.base_project_stats_service import BaseProjectStatsService
        
        # 调用服务层方法
        stats = BaseProjectStatsService.get_project_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"获取基础项目统计失败：{e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取统计数据失败：{str(e)}"
        )


# ============================================================================
# 高级统计接口（可选）
# ============================================================================

@router.get("/project/advanced")
async def get_advanced_project_stats():
    """
    获取高级项目统计数据
    
    返回字段:
    - basic: 基础统计
    - by_month: 按月统计（近 12 个月）
    - by_manager: 按负责人统计
    - delayed_projects: 延期项目统计
    
    适用场景:
    - 需要更详细的数据分析
    - 管理驾驶舱页面
    - 数据报表导出
    """
    try:
        # 导入服务层
        from services.base_project_stats_service import AdvancedProjectStatsService
        
        # 调用服务层方法
        stats = AdvancedProjectStatsService.get_advanced_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"获取高级项目统计失败：{e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取统计数据失败：{str(e)}"
        )


# ============================================================================
# 项目分类接口
# ============================================================================

@router.post("/project/categorize")
async def categorize_projects(projects_data: List[Dict]):
    """
    对项目列表进行状态分类
    
    请求体:
    [
        {
            "project_id": 1,
            "project_name": "项目 A",
            "planned_start_date": "2024-01-01",
            "actual_end_date": null,
            ...
        },
        ...
    ]
    
    返回:
    [
        {
            "project_id": 1,
            "project_name": "项目 A",
            "category": "进行中",  // 添加的分类结果
            ...
        },
        ...
    ]
    
    适用场景:
    - 前端已有项目数据，需要批量分类
    - 避免重复查询数据库
    - 自定义数据处理流程
    """
    try:
        from services.base_project_stats_service import BaseProjectStatsService
        
        # 调用服务层方法
        categorized = BaseProjectStatsService.categorize_projects(projects_data)
        
        return {
            "success": True,
            "data": categorized,
            "count": len(categorized),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"项目分类失败：{e}")
        raise HTTPException(
            status_code=500, 
            detail=f"项目分类失败：{str(e)}"
        )


# ============================================================================
# 自定义配置接口（示例）
# ============================================================================

@router.get("/project/config")
async def get_stats_config():
    """
    获取统计服务的配置信息
    
    返回:
    {
        "table_name": "projects",
        "field_mapping": {...},
        "status_categories": {...}
    }
    
    用途:
    - 前端了解后端配置
    - 动态调整 UI 展示
    - 调试和监控
    """
    try:
        from services.base_project_stats_service import BaseProjectStatsService
        
        return {
            "success": True,
            "config": {
                "table_name": BaseProjectStatsService.TABLE_NAME,
                "field_mapping": BaseProjectStatsService.FIELD_MAPPING,
                "status_categories": BaseProjectStatsService.STATUS_CATEGORIES
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"获取配置信息失败：{e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取配置信息失败：{str(e)}"
        )


# ============================================================================
# 健康检查接口
# ============================================================================

@router.get("/health")
async def health_check():
    """
    健康检查
    
    用于:
    - 监控系统
    - 服务发现
    - 负载均衡
    """
    try:
        from database.database import execute_query
        
        # 检查数据库连接
        test_sql = "SELECT 1"
        result = execute_query(test_sql)
        
        if result:
            return {
                "status": "healthy",
                "service": "project-stats",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "degraded",
                "service": "project-stats",
                "message": "Database connection issue",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "project-stats",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
