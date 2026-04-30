"""
Task Management Router Module
Contains all task-related API interfaces
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
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

# 7. Get project tasks by status (for project status distribution chart click)
@router.get("/project-tasks/status/{status}")
async def get_project_tasks_by_status(status: str):
    """Get project tasks by status from project_tasks table"""
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'progress', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"Warning: project_tasks table missing columns: {missing_columns}")
            return []

        # Map frontend display status to database status
        status_mapping = {
            '未开始': ['未开始'],
            '进行中': ['进行中'],
            '已完成': ['完成', '已完成', '已验收', 'Completed'],
            '已验收': ['已验收', 'Accepted'],
            '异常': ['异常'],
            '按时完成': ['按时完成'],
            '延期完成': ['延期完成']
        }
        
        # Get database statuses for the given display status
        db_statuses = status_mapping.get(status, [status])
        placeholders = ','.join(['%s'] * len(db_statuses))
        
        # Query project tasks by status
        task_sql = f"""
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
        WHERE task_status IN ({placeholders})
        ORDER BY created_at DESC
        """
        
        tasks = execute_query(task_sql, tuple(db_statuses), fetch_all=True) or []
        print(f"Query status: {status}, DB statuses: {db_statuses}, Matched tasks count: {len(tasks)}")
        
        # Format data
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            # Handle Decimal type conversion
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            formatted_task = {
                "task_id": task.get("task_id"),
                "project_name": task.get("project_name", ""),
                "wbs_code": task.get("wbs_code", ""),
                "task_name": task.get("task_name", ""),
                "task_owner": task.get("task_owner", ""),
                "task_status": task.get("task_status", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else None,
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else None,
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else None,
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else None,
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str,
                "created_at": str(task.get("created_at")) if task.get("created_at") else None
            }
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    except Exception as e:
        print(f"Error getting project tasks by status: {e}")
        return []

# 7.5 Get tasks by project status (for tasks-by-project-status endpoint)
@router.get("/tasks-by-project-status/{status}")
async def get_tasks_by_project_status(status: str):
    """Get tasks by project status from project_tasks table"""
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
        required_columns = ['project_name', 'wbs_code', 'task_name', 'task_owner', 'task_status', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'progress', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]

        if missing_columns:
            print(f"Warning: project_tasks table missing columns: {missing_columns}")
            return []

        # Map frontend display status to database status
        status_mapping = {
            '未开始': ['未开始'],
            '进行中': ['进行中'],
            '已完成': ['完成', '已完成', '已验收', 'Completed'],
            '已验收': ['已验收', 'Accepted'],
            '异常': ['异常'],
            '按时完成': ['按时完成'],
            '延期完成': ['延期完成']
        }
        
        # Get database statuses for the given display status
        db_statuses = status_mapping.get(status, [status])
        placeholders = ','.join(['%s'] * len(db_statuses))
        
        # Query project tasks by status
        task_sql = f"""
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
        WHERE task_status IN ({placeholders})
        ORDER BY created_at DESC
        """
        
        tasks = execute_query(task_sql, tuple(db_statuses), fetch_all=True) or []
        print(f"Query status: {status}, DB statuses: {db_statuses}, Matched tasks count: {len(tasks)}")
        
        # Format data
        formatted_tasks = []
        for task in tasks:
            if not task:
                continue
                
            # Handle Decimal type conversion
            progress_value = task.get("progress")
            if hasattr(progress_value, 'quantize'):
                progress_str = str(float(progress_value))
            else:
                progress_str = str(progress_value) if progress_value is not None else "0"

            formatted_task = {
                "task_id": task.get("task_id"),
                "project_name": task.get("project_name", ""),
                "wbs_code": task.get("wbs_code", ""),
                "task_name": task.get("task_name", ""),
                "task_owner": task.get("task_owner", ""),
                "task_status": task.get("task_status", ""),
                "planned_start_date": str(task.get("planned_start_date")) if task.get("planned_start_date") else None,
                "planned_end_date": str(task.get("planned_end_date")) if task.get("planned_end_date") else None,
                "actual_start_date": str(task.get("actual_start_date")) if task.get("actual_start_date") else None,
                "actual_end_date": str(task.get("actual_end_date")) if task.get("actual_end_date") else None,
                "progress": progress_str.rstrip('0').rstrip('.') if '.' in progress_str else progress_str,
                "created_at": str(task.get("created_at")) if task.get("created_at") else None
            }
            formatted_tasks.append(formatted_task)

        return formatted_tasks
    except Exception as e:
        print(f"Error getting tasks by project status: {e}")
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


# 15. Update task information
@router.put("/task/{task_id}")
async def update_task(task_id: int, task_data: Dict[str, Any] = Body(...)):
    """Update task information and record modification history"""
    try:
        # Check if project_tasks table exists
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            raise HTTPException(status_code=404, detail="项目任务表不存在")
        
        # Check if task exists
        check_task_sql = "SELECT task_id FROM project_tasks WHERE task_id = %s"
        task_result = execute_query(check_task_sql, (task_id,))
        if not task_result:
            raise HTTPException(status_code=404, detail=f"任务 ID {task_id} 不存在")
        
        # Prepare update fields
        update_fields = []
        update_values = []
        
        allowed_fields = [
            'task_name', 'wbs_code', 'task_owner', 
            'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date',
            'progress', 'task_status'
        ]
        
        for field in allowed_fields:
            if field in task_data:
                update_fields.append(f"{field} = %s")
                update_values.append(task_data[field])
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供要更新的字段")
        
        # Add task_id to values
        update_values.append(task_id)
        
        # Build update SQL
        update_sql = f"""
        UPDATE project_tasks 
        SET {', '.join(update_fields)}
        WHERE task_id = %s
        """
        
        # Execute update
        execute_query(update_sql, tuple(update_values))
        print(f"✅ 任务 {task_id} 更新成功")
        
        # Record modification history
        modifier_name = task_data.get('modifier_name', '未知用户')
        remarks = task_data.get('remarks_for_modification', '')
        
        # Get original task data for logging
        original_task_sql = "SELECT * FROM project_tasks WHERE task_id = %s"
        original_task = execute_query(original_task_sql, (task_id,), fetch_all=True)
        
        if original_task:
            # Create modification record
            insert_history_sql = """
            INSERT INTO project_task_modifications 
            (task_id, modifier_name, modification_time, remarks_for_modification, 
             original_data, modified_data) 
            VALUES (%s, %s, NOW(), %s, %s, %s)
            """
            
            import json
            original_data = dict(original_task[0]) if original_task[0] else {}
            modified_data = {**original_data, **task_data}
            
            execute_query(
                insert_history_sql, 
                (task_id, modifier_name, remarks, 
                 json.dumps(original_data, default=str), 
                 json.dumps(modified_data, default=str))
            )
            print(f"✅ 修改记录已保存")
        
        # 修改成功后，重新计算并更新项目状态
        try:
            from ..services.project_service import ProjectService
            from datetime import datetime as dt
            
            # 获取该项目的所有任务
            project_name = original_task[0].get('project_name') if original_task and len(original_task) > 0 else None
            project_id = original_task[0].get('project_id') if original_task and len(original_task) > 0 else None
            if project_name:
                print(f"开始重新计算项目状态：{project_name}")
                
                # 查询该项目的所有任务，按照 WBS 编码排序（转换为数字后排序）
                last_task_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date, wbs_code
                FROM project_tasks
                WHERE project_name = %s
                ORDER BY CAST(wbs_code AS UNSIGNED) DESC
                LIMIT 1
                """
                last_task_result = execute_query(last_task_sql, (project_name,), fetch_all=True)
                
                # 获取最后一个子任务的实际完成时间
                last_actual_end = last_task_result[0].get('actual_end_date') if last_task_result else None
                
                # 汇总所有任务的日期信息（用于计划时间和实际开始时间）
                all_tasks_sql = """
                SELECT planned_start_date, planned_end_date, actual_start_date, actual_end_date
                FROM project_tasks
                WHERE project_name = %s
                """
                all_tasks = execute_query(all_tasks_sql, (project_name,), fetch_all=True) or []
                
                if all_tasks:
                    all_planned_starts = [t['planned_start_date'] for t in all_tasks if t.get('planned_start_date')]
                    all_planned_ends = [t['planned_end_date'] for t in all_tasks if t.get('planned_end_date')]
                    all_actual_starts = [t['actual_start_date'] for t in all_tasks if t.get('actual_start_date')]
                    
                    # 取最早的计划开始时间、最晚的计划结束时间、最早的实际开始时间
                    project_planned_start = min(all_planned_starts) if all_planned_starts else None
                    project_planned_end = max(all_planned_ends) if all_planned_ends else None
                    project_actual_start = min(all_actual_starts) if all_actual_starts else None
                    
                    # 项目的实际完成时间严格取最后一个子任务的实际完成时间
                    project_actual_end = last_actual_end
                    
                    # 使用 ProjectService 计算项目状态
                    if project_planned_start and project_planned_end:
                        new_project_status = ProjectService.calculate_project_status(
                            project_planned_start,
                            project_planned_end,
                            project_actual_start,
                            project_actual_end,
                            project_id  # 传入项目ID以检查异常子任务
                        )
                        
                        # 更新 projects 表中的项目状态
                        update_project_status_sql = """
                        UPDATE projects 
                        SET project_status = %s, 
                            actual_start_date = %s, 
                            actual_end_date = %s,
                            updated_at = NOW()
                        WHERE project_name = %s
                        """
                        
                        execute_query(
                            update_project_status_sql,
                            (new_project_status, project_actual_start, project_actual_end, project_name)
                        )
                        print(f"✅ 项目 {project_name} 状态已更新为：{new_project_status}")
                    else:
                        print(f"⚠️ 无法计算项目状态：缺少计划日期")
        except Exception as e:
            print(f"⚠️ 更新项目状态失败：{e}")
            # 不阻断主流程，继续执行
        
        return {
            "success": True,
            "message": "任务修改成功",
            "task_id": task_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新任务失败：{e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新任务失败：{str(e)}")
