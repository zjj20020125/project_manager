"""
项目详情路由模块
包含项目详情相关的API接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

# 从database模块导入
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

# 7. 根据项目状态获取项目列表
@router.get("/projects/status/{status}")
async def get_projects_by_status(status: str, limit: int = 10, offset: int = 0):
    """根据项目状态获取项目列表"""
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

        # 根据状态查询项目
        current_date = datetime.now().date()

        if status == "total":
            # 所有项目
            sql = """
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []

        elif status == "not_started":
            # 未开始项目
            sql = """
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects 
            WHERE CURDATE() < planned_start_date
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []

        elif status == "ongoing":
            # 进行中项目
            sql = """
            SELECT p.project_id, p.project_name, p.project_manager, p.planned_start_date, p.planned_end_date, 
                   p.actual_start_date, p.actual_end_date, p.project_status, p.created_at
            FROM projects p
            WHERE CURDATE() >= p.planned_start_date AND (p.planned_end_date IS NULL OR CURDATE() <= p.planned_end_date) 
              AND (p.actual_end_date IS NULL OR p.actual_end_date >= CURDATE())
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []

        elif status == "completed":
            # 已结项项目
            sql = """
            SELECT project_id, project_name, project_manager, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, project_status, created_at
            FROM projects 
            WHERE actual_end_date IS NOT NULL AND actual_end_date < CURDATE()
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            projects = execute_query(sql, (limit, offset), fetch_all=True) or []
        else:
            return []

        # 转换项目数据并添加分类信息
        result = []
        for project in projects:
            if project is None:
                continue
            proj_dict = dict(project)

            # 添加分类信息
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
            result.append(proj_dict)

        return result
    except Exception as e:
        print(f"获取项目分类列表出错: {e}")
        return []

# 10. 获取项目列表
@router.get("/projects-list")
async def get_projects_list():
    """获取项目列表"""
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
        required_columns = ['project_name']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return []

        # 查询项目列表
        projects_sql = """
        SELECT DISTINCT project_id, project_name
        FROM projects
        ORDER BY project_name
        """

        projects_results = execute_query(projects_sql, fetch_all=True) or []

        # 格式化返回数据
        formatted_results = []
        for result in projects_results:
            if result is not None:
                formatted_results.append({
                    "project_id": result.get('project_id'),
                    "project_name": result.get('project_name', '')
                })

        return formatted_results
    except Exception as e:
        print(f"获取项目列表数据出错: {e}")
        return []

# 16. 根据项目ID或项目名称获取子任务数据
@router.get("/project-subtasks/{project_identifier}")
async def get_project_subtasks(project_identifier: str):
    """根据项目ID或项目名称获取子任务数据"""
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return []

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return []

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'project_id', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        # 尝试按项目ID查询（如果project_identifier是数字）
        task_sql = """
        SELECT 
            task_id,
            task_name,
            project_id,
            project_name,
            task_owner,
            wbs_code,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            progress,
            created_at
        FROM project_tasks
        WHERE 
        """

        # 首先尝试将project_identifier作为项目ID（数字）查询
        try:
            project_id_int = int(project_identifier)
            task_sql += "project_id = %s OR project_name = %s"
            tasks = execute_query(task_sql, (project_id_int, project_identifier), fetch_all=True) or []
        except ValueError:
            # 如果project_identifier不是数字，则只按项目名称查询
            task_sql += "project_name = %s"
            tasks = execute_query(task_sql, (project_identifier,), fetch_all=True) or []

        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_id": task.get("project_id"),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "wbs_code": task.get("wbs_code", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else "",
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else "",
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else "",
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else "",
                "task_status": task.get("task_status", ""),
                "progress": float(task.get("progress")) if task.get("progress") is not None else 0.0,
                "created_at": str(task.get("created_at")) if task.get("created_at") else ""
            }
            formatted_tasks.append(formatted_task)

        print(f"根据项目标识符'{project_identifier}'查询到 {len(formatted_tasks)} 个子任务")
        return formatted_tasks
    except Exception as e:
        print(f"获取项目子任务数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []