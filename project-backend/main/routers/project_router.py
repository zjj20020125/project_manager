"""
项目详情路由模块
包含项目详情相关的API接口
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

# 从database模块导入
try:
    from database.database import execute_query
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database.database import execute_query

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["项目详情"])

# 5. 获取项目详细数据并分类
@router.get("/projects/detail")
async def get_projects_detail():
    """获取项目详细数据并分类"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return []

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return []

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'planned_start_date', 'actual_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []

        # 查询所有项目数据
        projects_sql = """
        SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
               actual_start_date, actual_end_date, project_status, created_at
        FROM projects
        ORDER BY created_at DESC
        """
        all_projects = execute_query(projects_sql, fetch_all=True) or []

        # 获取当前日期进行分类
        current_date = datetime.now().date()

        categorized_projects = []
        for project in all_projects:
            if project is None:
                continue

            proj_dict = dict(project)

            # 根据日期对项目进行分类
            planned_start = proj_dict.get('planned_start_date')
            actual_end = proj_dict.get('actual_end_date')

            # 确保日期值是date类型
            if isinstance(planned_start, datetime):
                planned_start = planned_start.date()
            if isinstance(actual_end, datetime):
                actual_end = actual_end.date()

            if actual_end and actual_end < current_date:
                category = "已结项"
            elif planned_start and planned_start > current_date:
                category = "未开始"
            else:
                category = "进行中"

            proj_dict['category'] = category
            categorized_projects.append(proj_dict)

        return categorized_projects
    except Exception as e:
        print(f"获取项目详细数据出错: {e}")
        return []

# 6. 获取项目分类统计
@router.get("/projects/stats")
async def get_project_category_stats():
    """获取项目分类统计"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['planned_start_date', 'actual_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return {
                "total_projects": 0,
                "not_started_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }

        # 查询项目总数
        total_sql = "SELECT COUNT(*) as count FROM projects"
        total_result = execute_query(total_sql)
        total_projects = total_result["count"] if total_result and "count" in total_result else 0

        # 查询未开始项目数
        not_started_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() < planned_start_date
        """
        not_started_result = execute_query(not_started_sql)
        not_started_projects = not_started_result["count"] if not_started_result and "count" in not_started_result else 0

        # 查询已结项项目数
        completed_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE actual_end_date IS NOT NULL AND actual_end_date < CURDATE()
        """
        completed_result = execute_query(completed_sql)
        completed_projects = completed_result["count"] if completed_result and "count" in completed_result else 0

        # 进行中项目数 = 总数 - 未开始 - 已结项
        ongoing_projects = total_projects - not_started_projects - completed_projects

        return {
            "total_projects": total_projects,
            "not_started_projects": not_started_projects,
            "ongoing_projects": ongoing_projects,
            "completed_projects": completed_projects
        }
    except Exception as e:
        print(f"获取项目分类统计出错: {e}")
        return {
            "total_projects": 0,
            "not_started_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }