"""
任务业务逻辑服务
处理任务相关的业务逻辑
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from typing import List, Dict, Optional
from datetime import datetime

from database.database import execute_query

class TaskService:
    """任务业务逻辑服务类"""
    
    @staticmethod
    def get_task_statistics() -> Dict:
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

            # 查询任务总数
            total_tasks_sql = "SELECT COUNT(*) as count FROM project_tasks"
            total_result = execute_query(total_tasks_sql)
            total_tasks = total_result["count"] if total_result and "count" in total_result else 0

            # 里程碑任务总数
            milestone_sql = "SELECT COUNT(*) as count FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'"
            milestone_result = execute_query(milestone_sql)
            total_milestones = milestone_result["count"] if milestone_result and "count" in milestone_result else 0

            # 已完成里程碑数
            completed_milestone_sql = """
            SELECT COUNT(*) as count FROM project_tasks 
            WHERE wbs_code REGEXP '^[0-9]+$' AND task_status = '完成'
            """
            completed_result = execute_query(completed_milestone_sql)
            completed_milestones = completed_result["count"] if completed_result and "count" in completed_result else 0

            # 子任务总数
            total_subtasks = total_tasks - total_milestones

            # 已验收子任务数
            accepted_subtask_sql = """
            SELECT COUNT(*) as count FROM project_tasks 
            WHERE wbs_code NOT REGEXP '^[0-9]+$' AND actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL
            """
            accepted_subtask_result = execute_query(accepted_subtask_sql)
            accepted_subtasks = accepted_subtask_result["count"] if accepted_subtask_result and "count" in accepted_subtask_result else 0

            # 已验收任务数
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
            return {
                "total_milestones": 0,
                "completed_milestones": 0,
                "total_subtasks": 0,
                "accepted_subtasks": 0,
                "completed_tasks": 0
            }

    @staticmethod
    def get_abnormal_task_owner_stats() -> List[Dict]:
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
            required_columns = ['task_owner', 'task_status', 'wbs_code', 'project_name', 'created_at']
            missing_columns = [col for col in required_columns if col not in column_names]

            if missing_columns:
                print(f"警告: project_tasks表缺少以下列: {missing_columns}")
                return []

            # 查询异常状态的所有任务（状态为'异常'的任务，包括里程碑和子任务）
            # 按项目分组，找出每个项目的第一个异常节点和其他异常节点
            abnormal_tasks_sql = """
            SELECT 
                project_name,
                task_owner,
                task_name,
                wbs_code,
                created_at,
                task_status
            FROM project_tasks
            WHERE task_status = '异常'
              AND (
                task_owner IS NOT NULL 
                AND task_owner != ''
                AND task_owner != 'nan'
                AND task_owner != 'NaN'
                AND task_owner != 'null'
                AND task_owner != 'NULL'
                AND task_owner != '<NULL>'
                AND task_owner != 'None'
                AND TRIM(task_owner) != ''
              )
            ORDER BY project_name, created_at ASC
            """
            abnormal_tasks_results = execute_query(abnormal_tasks_sql, fetch_all=True) or []

            print(f"统计API查询到的异常任务总数: {len(abnormal_tasks_results)}")
            
            # 按项目分组，正确判断异常类型
            project_tasks = {}  # 按项目分组所有异常任务
            owner_stats = {
                'first_abnormal': {},  # 首个异常节点的负责人统计
                'delayed_progress': {}  # 进度推迟的负责人统计
            }

            # 首先按项目分组所有异常任务
            for task in abnormal_tasks_results:
                if task is not None:
                    project_name = task.get('project_name', '')
                    if project_name:
                        if project_name not in project_tasks:
                            project_tasks[project_name] = []
                        project_tasks[project_name].append(task)

            # 对每个项目单独处理，正确判断异常类型
            for project_name, project_task_list in project_tasks.items():
                # 按WBS编码排序
                sorted_tasks = sorted(project_task_list, key=lambda x: x.get('wbs_code', '') or '')
                
                # 为每个负责人分别统计
                owner_processed = set()  # 记录已处理的负责人
                
                # 遍历排序后的任务，判断每个负责人的异常类型
                for task in sorted_tasks:
                    task_owner = task.get('task_owner', '')
                    if not task_owner or not task_owner.strip():
                        continue
                        
                    # 处理多个负责人的情况
                    separators = [',', '，', ';', '；', '/', '、']
                    names = [task_owner]
                    for sep in separators:
                        if sep in task_owner:
                            names = task_owner.split(sep)
                            break
                    
                    # 清理负责人名称
                    clean_names = []
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']:
                            clean_names.append(clean_name)
                    
                    # 为每个负责人判断异常类型
                    for clean_name in clean_names:
                        if clean_name in owner_processed:
                            # 已经处理过的负责人，计入进度推迟
                            owner_stats['delayed_progress'][clean_name] = owner_stats['delayed_progress'].get(clean_name, 0) + 1
                        else:
                            # 判断是否为首个异常节点
                            is_first_abnormal = TaskService._check_is_first_abnormal_for_stats(
                                task, sorted_tasks, clean_name
                            )
                            
                            if is_first_abnormal:
                                owner_stats['first_abnormal'][clean_name] = owner_stats['first_abnormal'].get(clean_name, 0) + 1
                            else:
                                owner_stats['delayed_progress'][clean_name] = owner_stats['delayed_progress'].get(clean_name, 0) + 1
                            
                            owner_processed.add(clean_name)

            # 合并统计结果
            merged_stats = {}
            
            # 处理第一个异常节点统计
            for owner_name, count in owner_stats['first_abnormal'].items():
                if owner_name not in merged_stats:
                    merged_stats[owner_name] = {
                        'owner_name': owner_name,
                        'first_abnormal_count': count,
                        'delayed_progress_count': 0,
                        'total_count': count
                    }
                else:
                    merged_stats[owner_name]['first_abnormal_count'] = count
                    merged_stats[owner_name]['total_count'] += count
            
            # 处理进度推迟统计
            for owner_name, count in owner_stats['delayed_progress'].items():
                if owner_name not in merged_stats:
                    merged_stats[owner_name] = {
                        'owner_name': owner_name,
                        'first_abnormal_count': 0,
                        'delayed_progress_count': count,
                        'total_count': count
                    }
                else:
                    merged_stats[owner_name]['delayed_progress_count'] = count
                    merged_stats[owner_name]['total_count'] += count

            # 转换为所需格式并排序
            formatted_results = list(merged_stats.values())
            
            # 按总任务数量降序排列，只返回前10名
            formatted_results.sort(key=lambda x: x['total_count'], reverse=True)
            
            # 打印朱剑文的统计结果
            zhu_stat = next((item for item in formatted_results if item['owner_name'] == '朱剑文'), None)
            if zhu_stat:
                print(f"朱剑文统计结果: 首个异常节点={zhu_stat['first_abnormal_count']}, 进度推迟={zhu_stat['delayed_progress_count']}, 总计={zhu_stat['total_count']}")
            
            return formatted_results[:10]

        except Exception as e:
            print(f"获取异常子任务负责人统计出错: {e}")
            return []

    @staticmethod
    def get_owner_abnormal_tasks(owner: str) -> List[Dict]:
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

            # 查询指定负责人负责的异常任务详情（包括里程碑和子任务）
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
    
    @staticmethod
    def _determine_abnormal_type(task, wbs_code, owner_task_wbs_map, all_sorted_tasks, owner_name):
        """判断任务的异常类型：首个异常节点 vs 进度推迟（基于整个项目）"""
        task_status = task['task_status']
        project_name = task['project_name']
        
        # 新规则：
        # 规则1：在整个项目中第一个出现异常的任务 -> 首个异常节点
        # 规则2：如果不是第一个异常任务 -> 进度推迟
        
        # 检查是否为整个项目中的首个异常任务
        is_first_abnormal = TaskService._check_is_first_abnormal(task, all_sorted_tasks, owner_name)
        
        if is_first_abnormal:
            return {'chinese': '首个异常节点', 'english': 'first_abnormal'}
        else:
            return {'chinese': '进度推迟', 'english': 'delayed_progress'}
    
    @staticmethod
    def _check_predecessor_delay(current_wbs, all_sorted_tasks, owner_name):
        """检查当前任务是否因为前置任务未完成而延迟"""
        current_level = len(current_wbs.split('.')) if '.' in current_wbs else 1
        
        # 查找同级或上级的前置任务
        for task in all_sorted_tasks:
            task_wbs = task['wbs_code'] or ''
            task_owner = task['task_owner'] or ''
            task_status = task['task_status']
            
            # 清理负责人名称
            separators = [',', '，', ';', '；', '/', '、']
            names = [task_owner]
            for sep in separators:
                if sep in task_owner:
                    names = task_owner.split(sep)
                    break
            clean_names = [name.strip() for name in names if name.strip() not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']]
            
            # 检查是否为前置任务（WBS层级更高或同级但顺序在前）
            task_level = len(task_wbs.split('.')) if '.' in task_wbs else 1
            
            # 如果是前置任务且未完成，且由相同负责人负责
            if (task_level < current_level or (task_level == current_level and task_wbs < current_wbs)) \
               and task_status != '完成' \
               and owner_name in clean_names:
                return True
        
        return False
    
    @staticmethod
    def _check_is_first_abnormal(target_task, all_sorted_tasks, owner_name):
        """检查是否为整个项目中的首个异常任务（不区分负责人）"""
        target_wbs = target_task['wbs_code'] or ''
        
        # 按WBS顺序检查之前的任务
        for task in all_sorted_tasks:
            task_wbs = task['wbs_code'] or ''
            if task_wbs >= target_wbs:  # 到达或超过目标任务，停止检查
                break
                
            task_status = task['task_status']
            
            # 如果之前有任何任务出现异常，则当前不是首个异常节点
            if task_status == '异常':
                return False
        
        return True
    
    @staticmethod
    def _check_is_first_abnormal_for_stats(target_task, all_sorted_tasks, owner_name):
        """为统计API检查是否为首个异常节点（基于整个项目，不区分负责人）"""
        target_wbs = target_task.get('wbs_code', '') or ''
        target_created_at = target_task.get('created_at', '')
        
        # 按WBS和创建时间排序检查之前的任务
        for task in all_sorted_tasks:
            task_wbs = task.get('wbs_code', '') or ''
            task_created_at = task.get('created_at', '')
            
            # 如果是同一任务或后面的，停止检查
            if task_wbs > target_wbs or (task_wbs == target_wbs and task_created_at >= target_created_at):
                break
            
            task_status = task.get('task_status', '')
            
            # 如果之前有任何任务出现异常，则当前不是首个异常节点
            if task_status == '异常':
                return False
        
        return True
    
    @staticmethod
    def get_abnormal_task_detail_by_owner(owner_name: str) -> List[Dict]:
        """获取指定负责人的异常子任务详情，区分首个异常节点和进度推迟"""
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

            # 查询所有异常任务（与统计API使用完全相同的查询逻辑）
            detail_sql = """
            SELECT 
                project_name,
                task_owner,
                task_name,
                wbs_code,
                created_at,
                task_status,
                task_id,
                planned_start_date,
                planned_end_date,
                actual_start_date,
                actual_end_date,
                progress
            FROM project_tasks 
            WHERE task_status = '异常'
              AND (
                task_owner IS NOT NULL 
                AND task_owner != ''
                AND task_owner != 'nan'
                AND task_owner != 'NaN'
                AND task_owner != 'null'
                AND task_owner != 'NULL'
                AND task_owner != '<NULL>'
                AND task_owner != 'None'
                AND TRIM(task_owner) != ''
              )
            ORDER BY project_name, created_at ASC
            """
            
            tasks = execute_query(detail_sql, fetch_all=True) or []
            
            if not tasks:
                return []
            
            # 按项目分组，正确判断首个异常节点
            project_first_abnormal_tasks = {}  # 记录每个项目的第一个异常任务信息
            result_tasks = []
            
            # 首先按项目分组所有异常任务
            project_tasks = {}
            for task in tasks:
                project_name = task['project_name']
                if project_name not in project_tasks:
                    project_tasks[project_name] = []
                project_tasks[project_name].append(task)
            
            # 对每个项目单独处理，正确判断异常类型
            for project_name, project_task_list in project_tasks.items():
                # 按WBS编码排序，确定任务层级关系
                sorted_tasks = sorted(project_task_list, key=lambda x: x['wbs_code'] or '')
                
                # 收集该负责人在该项目中的所有异常任务
                owner_tasks_in_project = []
                owner_task_wbs_map = {}  # 记录该负责人的任务WBS映射
                
                # 第一遍：收集该负责人的所有异常任务
                for task in sorted_tasks:
                    task_owner = task['task_owner']
                    wbs_code = task['wbs_code'] or ''
                    
                    # 处理多个负责人的情况
                    separators = [',', '，', ';', '；', '/', '、']
                    names = [task_owner]
                    for sep in separators:
                        if sep in task_owner:
                            names = task_owner.split(sep)
                            break
                    
                    # 清理负责人名称
                    clean_names = []
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name not in ['nan', 'NaN', 'null', 'NULL', '<NULL>', 'None']:
                            clean_names.append(clean_name)
                    
                    # 检查该任务是否由目标负责人负责
                    if owner_name in clean_names:
                        owner_tasks_in_project.append(task)
                        owner_task_wbs_map[wbs_code] = task
                
                # 第二遍：判断每个任务的异常类型
                for task in owner_tasks_in_project:
                    task_copy = task.copy()
                    wbs_code = task['wbs_code'] or ''
                    task_status = task['task_status']
                    
                    # 判断异常类型的核心逻辑
                    abnormal_type = TaskService._determine_abnormal_type(
                        task, 
                        wbs_code, 
                        owner_task_wbs_map, 
                        sorted_tasks,
                        owner_name
                    )
                    
                    task_copy['abnormal_type'] = abnormal_type['chinese']
                    task_copy['abnormal_type_en'] = abnormal_type['english']
                    result_tasks.append(task_copy)
            
            # 按创建时间整体排序
            result_tasks.sort(key=lambda x: x['created_at'])
            
            # 格式化返回数据
            formatted_results = []
            for task in result_tasks:
                formatted_results.append({
                    "task_id": task.get('task_id'),
                    "taskName": task.get('task_name', ''),
                    "projectName": task.get('project_name', ''),
                    "task_owner": task.get('task_owner', ''),
                    "wbsNo": task.get('wbs_code', ''),
                    "planStart": str(task.get('planned_start_date')) if task.get('planned_start_date') else None,
                    "planEnd": str(task.get('planned_end_date')) if task.get('planned_end_date') else None,
                    "actual_start_date": str(task.get('actual_start_date')) if task.get('actual_start_date') else None,
                    "actual_end_date": str(task.get('actual_end_date')) if task.get('actual_end_date') else None,
                    "status": task.get('task_status', ''),
                    "progress": float(task.get('progress')) if task.get('progress') is not None else 0.0,
                    "created_at": str(task.get('created_at')) if task.get('created_at') else None,
                    "abnormal_type": task.get('abnormal_type', ''),
                    "abnormal_type_en": task.get('abnormal_type_en', '')
                })
            
            print(f"获取负责人 {owner_name} 的异常任务详情，共 {len(formatted_results)} 个任务")
            print(f"其中首个异常节点: {len([t for t in formatted_results if t.get('abnormal_type_en') == 'first_abnormal'])} 个")
            print(f"其中进度推迟: {len([t for t in formatted_results if t.get('abnormal_type_en') == 'delayed_progress'])} 个")
            return formatted_results
            
        except Exception as e:
            print(f"获取异常子任务详情出错: {e}")
            import traceback
            traceback.print_exc()
            return []