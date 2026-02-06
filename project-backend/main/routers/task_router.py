"""
任务管理路由模块
包含任务相关的所有API接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

# 从database模块导入
from database.database import execute_query

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["任务管理"])

# 4. 获取任务列表
@router.get("/task/list")
async def get_task_list(limit: int = 20, offset: int = 0):
    """获取任务列表"""
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        task_sql = """
        SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
               task_name as taskName, task_owner as owner,
               CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
               '重要不紧急' as priority, task_status as status,
               planned_start_date as planStart, planned_end_date as planEnd,
               progress as progress
        FROM project_tasks
        LIMIT %s OFFSET %s
        """
        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []

        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            # 处理Decimal类型转换为字符串
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):  # 如果是Decimal类型
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            # 格式化日期字段
            plan_start = task.get("planStart")
            plan_end = task.get("planEnd")

            formatted_task = {
                "projectNo": task.get("projectNo", ""),
                "projectName": task.get("project_name", ""),
                "wbsNo": task.get("wbsNo", ""),
                "taskName": task.get("taskName", ""),
                "owner": task.get("owner") or "",
                "taskType": task.get("taskType", ""),
                "priority": task.get("priority", ""),
                "status": task.get("status", ""),
                "planStart": str(plan_start) if plan_start else "",
                "planEnd": str(plan_end) if plan_end else "",
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str
            }
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    except Exception as e:
        print(f"获取任务列表出错: {e}")
        return []

# 8. 根据任务类型获取任务列表
@router.get("/tasks/type/{type}")
async def get_tasks_by_type(type: str, limit: int = 10, offset: int = 0):
    """根据任务类型获取任务列表"""
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        # 根据任务类型查询任务
        if type == "milestone":
            # 里程碑任务：wbs_code为纯数字
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '里程碑' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_milestone":
            # 已验收里程碑任务
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '里程碑' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$' AND (task_status = '完成' OR task_status = '已验收')
            LIMIT %s OFFSET %s
            """
        elif type == "subtask":
            # 子任务：wbs_code包含小数点
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   '子任务' as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code NOT REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_task":
            # 已验收任务
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
            LIMIT %s OFFSET %s
            """
        else:
            # 默认返回所有任务
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN '里程碑' ELSE '子任务' END as taskType,
                   '重要不紧急' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            LIMIT %s OFFSET %s
            """

        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []

        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            # 处理Decimal类型转换为字符串
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            # 格式化日期字段
            plan_start = task.get("planStart")
            plan_end = task.get("planEnd")

            formatted_task = {
                "projectNo": task.get("projectNo", ""),
                "projectName": task.get("project_name", ""),
                "wbsNo": task.get("wbsNo", ""),
                "taskName": task.get("taskName", ""),
                "owner": task.get("owner") or "",
                "taskType": task.get("taskType", ""),
                "priority": task.get("priority", ""),
                "status": task.get("status", ""),
                "planStart": str(plan_start) if plan_start else "",
                "planEnd": str(plan_end) if plan_end else "",
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str
            }
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    except Exception as e:
        print(f"获取任务分类列表出错: {e}")
        return []

# 9. 获取指定类型任务的总数
@router.get("/tasks/type/{type}/count", response_model=int)
async def get_tasks_by_type_count(type: str):
    """获取指定类型任务的总数"""
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return 0

        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return 0

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return 0

        # 根据任务类型查询任务总数
        if type == "milestone":
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'"
        elif type == "completed_milestone":
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$' AND (task_status = '完成' OR task_status = '已验收')"
        elif type == "subtask":
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE wbs_code NOT REGEXP '^[0-9]+$'"
        elif type == "completed_task":
            count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL"
        else:
            count_sql = "SELECT COUNT(*) as total FROM project_tasks"

        count_result = execute_query(count_sql)
        total_count = count_result["total"] if count_result and "total" in count_result else 0

        return total_count
    except Exception as e:
        print(f"获取任务总数出错: {e}")
        return 0

# 14. 根据任务状态获取任务列表
@router.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str, limit: int = 100, offset: int = 0):
    """根据任务状态获取任务列表"""
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
        required_columns = ['task_status', 'task_name', 'project_name', 'task_owner', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        # 状态映射
        status_map = {
            "not_started": "未开始",
            "ongoing": "进行中", 
            "completed": "已完成",
            "accepted": "已验收"
        }

        db_status = status_map.get(status, status)
        
        # 检查数据库中是否存在该状态的任务
        count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE task_status = %s"
        count_result = execute_query(count_sql, (db_status,))
        total_count = count_result.get('total', 0) if count_result else 0
        print(f"状态为 '{db_status}' 的任务总数: {total_count}")

        task_sql = """
        SELECT 
            task_id,
            task_name,
            project_name,
            task_owner,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            task_status,
            created_at
        FROM project_tasks
        WHERE task_status = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        tasks = execute_query(task_sql, (db_status, limit, offset), fetch_all=True) or []

        # 格式化数据
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_name": task.get("project_name", ""),
                "task_owner": task.get("task_owner", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else None,
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else None,
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else None,
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else None,
                "task_status": task.get("task_status", ""),
                "created_at": str(task.get("created_at")) if task.get("created_at") else None
            }
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    except Exception as e:
        print(f"获取任务状态列表出错: {e}")
        return []

# 15. 根据项目状态获取任务数据（用于项目状态详情页）
@router.get("/tasks-by-project-status/{status}")
async def get_tasks_by_project_status(status: str):
    """根据项目状态获取任务数据"""
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
        required_columns = ['task_status', 'task_name', 'project_name', 'task_owner', 'wbs_code', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'progress', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []

        # 直接使用传入的状态参数查询
        db_status = status
        
        # 检查数据库中是否存在该状态的任务
        count_sql = "SELECT COUNT(*) as total FROM project_tasks WHERE task_status = %s"
        count_result = execute_query(count_sql, (db_status,))
        total_count = count_result.get('total', 0) if count_result else 0
        print(f"状态为 '{db_status}' 的任务总数: {total_count}")

        task_sql = """
        SELECT 
            task_id,
            project_name,
            wbs_code,
            task_name,
            task_owner,
            task_status,
            planned_start_date,
            planned_end_date,
            actual_start_date,
            actual_end_date,
            progress,
            created_at
        FROM project_tasks
        WHERE task_status = %s
        ORDER BY created_at DESC
        """
        tasks = execute_query(task_sql, (db_status,), fetch_all=True) or []

        # 格式化数据以匹配前端期望的格式
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            # 处理进度字段
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):  # 如果是Decimal类型
                progress_float = float(progress_value)
            else:
                progress_float = float(progress_value) if progress_value is not None else 0.0

            formatted_task = {
                "task_id": task.get("task_id"),
                "task_name": task.get("task_name", ""),
                "project_name": task.get("project_name", ""),
                "wbs_code": task.get("wbs_code", ""),
                "task_owner": task.get("task_owner", ""),
                "task_status": task.get("task_status", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else "",
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else "",
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else "",
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else "",
                "progress": progress_float,
                "created_at": str(task.get("created_at")) if task.get("created_at") else ""
            }
            formatted_tasks.append(formatted_task)

        print(f"根据状态'{status}'返回任务数据: {len(formatted_tasks)} 条")
        return formatted_tasks
    except Exception as e:
        print(f"根据项目状态获取任务数据出错: {e}")
        import traceback
        traceback.print_exc()
        return []