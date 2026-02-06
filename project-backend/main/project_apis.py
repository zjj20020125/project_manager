"""
项目管理相关API接口
包含项目统计、任务管理、人员统计等功能
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
import pandas as pd
import io
import re
import os

# 从database模块导入
from database.database import execute_query

# 从models模块导入
from models.models import ProjectStats, TaskStats, ChartData, TaskItem

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["项目管理"])

# 1. 获取项目统计数据
@router.get("/project/stats", response_model=ProjectStats)
def get_project_stats():
    """获取项目统计数据"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return {
                "total_projects": 0,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询总项目数
        total_sql = "SELECT COUNT(*) as count FROM projects"
        total_result = execute_query(total_sql)
        if not total_result:
            print("警告: 无法获取项目总数")
            return {
                "total_projects": 0,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        total = total_result["count"] if total_result and "count" in total_result else 0
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE projects"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取projects表结构")
            return {
                "total_projects": total,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['planned_start_date', 'planned_end_date']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: projects表缺少以下列: {missing_columns}")
            return {
                "total_projects": total,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询进行中项目数：当前日期在预计开始时间和预计结束时间之间
        ongoing_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() BETWEEN planned_start_date AND planned_end_date
        """
        ongoing_result = execute_query(ongoing_sql)
        ongoing = ongoing_result["count"] if ongoing_result and "count" in ongoing_result else 0
        
        # 查询未开始项目数：当前日期在预计开始时间之前
        unstarted_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() < planned_start_date
        """
        unstarted_result = execute_query(unstarted_sql)
        unstarted = unstarted_result["count"] if unstarted_result and "count" in unstarted_result else 0
        
        # 查询已结项项目数：当前日期在预计结束时间之后
        completed_sql = """
        SELECT COUNT(*) as count FROM projects 
        WHERE CURDATE() > planned_end_date
        """
        completed_result = execute_query(completed_sql)
        completed = completed_result["count"] if completed_result and "count" in completed_result else 0
        
        return {
            "total_projects": total,  # 已立项项目数
            "unstarted_projects": unstarted,
            "ongoing_projects": ongoing,
            "completed_projects": completed
        }
    except Exception as e:
        print(f"获取项目统计数据出错: {e}")
        # 返回默认值
        return {
            "total_projects": 0,
            "unstarted_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }

# 2. 获取任务统计数据
@router.get("/task/stats", response_model=TaskStats)
def get_task_stats():
    """获取任务统计数据"""
    try:
        # 检查project_tasks表是否存在
        check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: project_tasks表不存在")
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": 0,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        # 检查必要字段是否存在
        describe_sql = "DESCRIBE project_tasks"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取project_tasks表结构")
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": 0,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = ['wbs_code', 'task_status']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            # 尝试使用所有可用任务进行统计
            total_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks"
            total_result = execute_query(total_tasks_sql)
            total_tasks = total_result["count"] if total_result and "count" in total_result else 0
            
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": total_tasks,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }
        
        # 由于jgj-project数据库使用project_tasks表结构，查询任务总数
        total_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks"
        total_result = execute_query(total_tasks_sql)
        total_tasks = total_result["count"] if total_result and "count" in total_result else 0
        
        # 里程碑任务总数（根据wbs_code判断，纯数字如1,2,3为里程碑任务，而1.1,1.2等不是）
        milestone_sql = "SELECT COUNT(*) as count FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'"
        milestone_result = execute_query(milestone_sql)
        total_milestones = milestone_result["count"] if milestone_result and "count" in milestone_result else 0
        
        # 已完成里程碑数（task_status为'完成'的里程碑任务）
        completed_milestone_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE wbs_code REGEXP '^[0-9]+$' AND task_status = '完成'
        """
        completed_result = execute_query(completed_milestone_sql)
        completed_milestones = completed_result["count"] if completed_result and "count" in completed_result else 0
        
        # 子任务总数（非里程碑任务）
        total_subtasks = total_tasks - total_milestones
        
        # 已验收子任务数（填写了实际开始时间和实际完成时间的非里程碑任务）
        accepted_subtask_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE wbs_code NOT REGEXP '^[0-9]+$' AND actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
        """
        accepted_subtask_result = execute_query(accepted_subtask_sql)
        accepted_subtasks = accepted_subtask_result["count"] if accepted_subtask_result and "count" in accepted_subtask_result else 0
        
        # 已验收任务数（填写了实际开始时间和实际完成时间的任务，包括里程碑和子任务）
        completed_tasks_sql = """
        SELECT COUNT(*) as count FROM project_tasks 
        WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
        """
        completed_tasks_result = execute_query(completed_tasks_sql)
        completed_tasks = completed_tasks_result["count"] if completed_tasks_result and "count" in completed_tasks_result else 0
        
        return {
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "total_subtasks": total_subtasks,
            "accepted_subtasks": accepted_subtasks,
            "completed_tasks": completed_tasks
        }
    except Exception as e:
        print(f"获取任务统计数据出错: {e}")
        # 返回默认值
        return {
            "total_milestones": 0,
            "completed_milestones": 0,
            "total_subtasks": 0,
            "accepted_subtasks": 0,
            "completed_tasks": 0
        }

# 3. 获取项目统计信息（简化版本，避免与chart_router冲突）
@router.get("/project/stats/simple")
def get_simple_project_stats():
    """获取简化的项目统计信息"""
    try:
        # 检查projects表是否存在
        check_table_sql = "SHOW TABLES LIKE 'projects'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: projects表不存在")
            return {
                "total_projects": 0,
                "unstarted_projects": 0,
                "ongoing_projects": 0,
                "completed_projects": 0
            }
        
        # 查询总项目数
        total_sql = "SELECT COUNT(*) as count FROM projects"
        total_result = execute_query(total_sql)
        total = total_result["count"] if total_result and "count" in total_result else 0
        
        # 返回简化数据
        return {
            "total_projects": total,
            "unstarted_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }
    except Exception as e:
        print(f"获取简化项目统计信息出错: {e}")
        return {
            "total_projects": 0,
            "unstarted_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }

# 4. 获取项目详细数据并分类
@router.get("/projects/detail", response_model=List[dict])
def get_projects_detail():
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

# 6. 获取异常子任务负责人统计
@router.get("/abnormal-task-owner-stats", response_model=List[dict])
def get_abnormal_task_owner_stats():
    """获取异常子任务负责人统计"""
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
        required_columns = ['task_owner', 'task_status', 'wbs_code']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询异常状态的子任务（状态为'异常'且wbs_code不为纯数字的任务）
        abnormal_subtasks_sql = """
        SELECT 
            task_owner,
            task_name,
            wbs_code
        FROM project_tasks
        WHERE task_status = '异常'
          AND wbs_code NOT REGEXP '^[0-9]+$'  -- 排除里程碑任务，只统计子任务
          AND task_owner IS NOT NULL 
          AND task_owner != ''
          AND task_owner != 'nan'
          AND task_owner != 'NaN'
          AND task_owner != 'null'
        """
        abnormal_tasks_results = execute_query(abnormal_subtasks_sql, fetch_all=True) or []
        
        # 统计负责人数量，处理多人负责的情况
        owner_count = {}
        
        for task in abnormal_tasks_results:
            if task is not None:
                task_owner = task.get('task_owner', '')
                if task_owner and task_owner.strip():
                    # 处理多个负责人的情况（逗号、分号、顿号分隔）
                    separators = [',', '，', ';', '；', '/', '、']
                    names = [task_owner]
                    
                    # 尝试分割多个负责人
                    for sep in separators:
                        if sep in task_owner:
                            names = task_owner.split(sep)
                            break
                    
                    # 清理并统计每个负责人
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']:
                            owner_count[clean_name] = owner_count.get(clean_name, 0) + 1
        
        # 转换为所需格式并排序
        formatted_results = []
        for owner_name, count in owner_count.items():
            formatted_results.append({
                "owner_name": owner_name,
                "task_count": count
            })
        
        # 按任务数量降序排列，只返回前10名
        formatted_results.sort(key=lambda x: x['task_count'], reverse=True)
        return formatted_results[:10]
        
    except Exception as e:
        print(f"获取异常子任务负责人统计出错: {e}")
        return []

# 7. 获取指定负责人负责的异常子任务详情
@router.get("/owner-abnormal-tasks/{owner}", response_model=List[dict])
def get_owner_abnormal_tasks(owner: str):
    """获取指定负责人负责的异常子任务详情"""
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
        required_columns = ['task_owner', 'task_name', 'project_name', 'wbs_code', 'planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date', 'task_status', 'progress', 'created_at']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告: project_tasks表缺少以下列: {missing_columns}")
            return []
        
        # 查询指定负责人负责的异常子任务详情
        # 处理多个负责人的情况
        owner_abnormal_tasks_sql = """
        SELECT 
            task_id,
            task_name,
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
        WHERE task_status = '异常'
          AND wbs_code NOT REGEXP '^[0-9]+$'  -- 只查询子任务
          AND (
            task_owner = %s OR
            task_owner LIKE CONCAT('%%', %s, ',%%') OR
            task_owner LIKE CONCAT('%%', %s, '，%%') OR
            task_owner LIKE CONCAT('%%', %s, ';%%') OR
            task_owner LIKE CONCAT('%%', %s, '；%%') OR
            task_owner LIKE CONCAT('%%', %s, '/%%') OR
            task_owner LIKE CONCAT('%%', %s, '、%%') OR
            task_owner LIKE CONCAT(%s, ',%%') OR
            task_owner LIKE CONCAT(%s, '，%%') OR
            task_owner LIKE CONCAT(%s, ';%%') OR
            task_owner LIKE CONCAT(%s, '；%%') OR
            task_owner LIKE CONCAT(%s, '/%%') OR
            task_owner LIKE CONCAT(%s, '、%%')
          )
        ORDER BY created_at DESC
        """
        
        owner_abnormal_tasks_results = execute_query(owner_abnormal_tasks_sql, 
            (owner, owner, owner, owner, owner, owner, owner, 
             owner, owner, owner, owner, owner, owner), fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in owner_abnormal_tasks_results:
            if result is not None:
                formatted_results.append({
                    "task_id": result.get('task_id'),
                    "taskName": result.get('task_name', ''),
                    "projectName": result.get('project_name', ''),
                    "task_owner": result.get('task_owner', ''),
                    "wbsNo": result.get('wbs_code', ''),
                    "planStart": str(result.get('planned_start_date')) if result.get('planned_start_date') else None,
                    "planEnd": str(result.get('planned_end_date')) if result.get('planned_end_date') else None,
                    "actual_start_date": str(result.get('actual_start_date')) if result.get('actual_start_date') else None,
                    "actual_end_date": str(result.get('actual_end_date')) if result.get('actual_end_date') else None,
                    "status": result.get('task_status', ''),
                    "progress": float(result.get('progress')) if result.get('progress') is not None else 0.0,
                    "created_at": str(result.get('created_at')) if result.get('created_at') else None
                })
        
        return formatted_results
    except Exception as e:
        print(f"获取负责人异常子任务详情出错: {e}")
        return []