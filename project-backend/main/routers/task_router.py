"""
Task Management Router Module
Contains all task-related API interfaces
"""

from fastapi import APIRouter
from typing import List
from datetime import datetime

# Import from database module
from database.database import execute_query

# Import service layer
from ..services.task_service import TaskService

# Create router instance
router = APIRouter(prefix="/v1", tags=["Task Management"])

# 1. Get abnormal task owner statistics
@router.get("/task/abnormal-owner-stats")
async def get_abnormal_task_owner_stats():
    """Get abnormal task owner statistics, distinguishing first abnormal node and delayed progress"""
    return TaskService.get_abnormal_task_owner_stats()

# 2. Get specified owner abnormal task details
@router.get("/task/abnormal-detail/{owner}")
async def get_abnormal_task_detail_by_owner(owner: str):
    """Get abnormal task details for specified owner, distinguishing first abnormal node and delayed progress"""
    return TaskService.get_abnormal_task_detail_by_owner(owner)

# 4. Get task list
@router.get("/task/list")
async def get_task_list(limit: int = 20, offset: int = 0):
    """Get task list"""
    try:
        # Check if project_tasks table exists
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("Warning: project_tasks table does not exist")
            return []

        # Check if required fields exist
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("Warning: Cannot get project_tasks table structure")
            return []

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"Warning: project_tasks table missing columns: {missing_columns}")
            return []

        task_sql = """
        SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
               task_name as taskName, task_owner as owner,
               CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN 'Milestone' ELSE 'Subtask' END as taskType,
               'Important Not Urgent' as priority, task_status as status,
               planned_start_date as planStart, planned_end_date as planEnd,
               progress as progress
        FROM project_tasks
        LIMIT %s OFFSET %s
        """
        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []

        # Format data
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            # Handle Decimal type conversion to string
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):  # If it's Decimal type
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            # Format date fields
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
        print(f"Error getting task list: {e}")
        return []

# 8. Get tasks by type
@router.get("/tasks/type/{type}")
async def get_tasks_by_type(type: str, limit: int = 10, offset: int = 0):
    """Get tasks by type"""
    try:
        # Check if project_tasks table exists
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("Warning: project_tasks table does not exist")
            return []

        # Check if required fields exist
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("Warning: Cannot get project_tasks table structure")
            return []

        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'progress']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"Warning: project_tasks table missing columns: {missing_columns}")
            return []

        # Query tasks by type
        if type == "milestone":
            # Milestone tasks: wbs_code is pure digits
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   'Milestone' as taskType,
                   'Important Not Urgent' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_milestone":
            # Completed milestone tasks
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   'Milestone' as taskType,
                   'Important Not Urgent' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code REGEXP '^[0-9]+$' AND (task_status = 'Completed' OR task_status = 'Accepted')
            LIMIT %s OFFSET %s
            """
        elif type == "subtask":
            # Subtasks: wbs_code contains decimal point
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   'Subtask' as taskType,
                   'Important Not Urgent' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE wbs_code NOT REGEXP '^[0-9]+$'
            LIMIT %s OFFSET %s
            """
        elif type == "completed_task":
            # Completed tasks
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN 'Milestone' ELSE 'Subtask' END as taskType,
                   'Important Not Urgent' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
            LIMIT %s OFFSET %s
            """
        else:
            # Return all tasks by default
            task_sql = """
            SELECT project_name as projectNo, project_name, wbs_code as wbsNo,
                   task_name as taskName, task_owner as owner,
                   CASE WHEN wbs_code REGEXP '^[0-9]+$' THEN 'Milestone' ELSE 'Subtask' END as taskType,
                   'Important Not Urgent' as priority, task_status as status,
                   planned_start_date as planStart, planned_end_date as planEnd,
                   progress as progress
            FROM project_tasks
            LIMIT %s OFFSET %s
            """

        tasks = execute_query(task_sql, (limit, offset), fetch_all=True) or []

        # Format data
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue

            # Handle Decimal type conversion to string
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            # Format date fields
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
        print(f"Error getting tasks by type: {e}")
        return []
