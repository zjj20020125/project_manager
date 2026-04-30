"""
项目业务逻辑服务
处理项目相关的业务逻辑和数据处理
"""

from typing import List, Dict, Optional
from datetime import datetime, date
import re

# 从database模块导入
from database.database import execute_query

class ProjectService:
    """项目业务逻辑服务类"""
    
    @staticmethod
    def get_project_statistics() -> Dict:
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

    @staticmethod
    def categorize_projects(projects_data: List[Dict]) -> List[Dict]:
        """对项目进行分类"""
        current_date = datetime.now().date()
        categorized_projects = []
        
        for project in projects_data:
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

    @staticmethod
    def calculate_project_status(planned_start: date, planned_end: date, 
                               actual_start: date = None, actual_end: date = None,
                               project_id: int = None) -> str:
        """根据日期计算项目状态
        
        参数:
            planned_start: 计划开始日期
            planned_end: 计划结束日期
            actual_start: 实际开始日期
            actual_end: 实际结束日期
            project_id: 项目ID（可选），用于检查是否有异常子任务
        """
        current_date = datetime.now().date()
        
        # 如果有实际结束日期且晚于当前日期，则为已完成（延期完成）
        if actual_end and actual_end > current_date:
            return "已完成（延期完成）"
        # 如果有实际完成日期且早于或等于当前日期，则为已结项
        elif actual_end and actual_end <= current_date:
            return "已完成"
        # 如果有实际开始时间，说明项目已经启动
        elif actual_start:
            # 【新增】检查是否有异常子任务（判断顺序在2和3之间）
            if project_id:
                has_abnormal_tasks = ProjectService._check_abnormal_subtasks(project_id)
                if has_abnormal_tasks:
                    return "异常"
            
            # 计划时间范围内
            if planned_start and planned_end and planned_start <= current_date <= planned_end:
                return "进行中"
            # 计划时间已过但未完成
            else:
                return "进行中（延期）"
        # 如果计划开始日期晚于当前日期，则为未开始
        elif planned_start and planned_start > current_date:
            return "未开始"
        # 如果当前日期在计划期间内，则为进行中
        elif planned_start and planned_end and planned_start <= current_date <= planned_end:
            return "进行中"
        # 其他情况：计划时间已过，但没有实际开始
        else:
            return "已计划"
    
    @staticmethod
    def _check_abnormal_subtasks(project_id: int) -> bool:
        """检查项目下是否有状态为'异常'的子任务
        
        参数:
            project_id: 项目ID
        
        返回:
            True: 存在异常子任务
            False: 不存在异常子任务
        """
        try:
            # 查询该项目下是否有状态为'异常'的子任务
            check_sql = """
            SELECT COUNT(*) as abnormal_count
            FROM project_tasks
            WHERE project_id = %s AND task_status = '异常'
            """
            result = execute_query(check_sql, (project_id,), fetch_one=True)
            
            if result and result.get('abnormal_count', 0) > 0:
                print(f"⚠️ 项目 ID={project_id} 存在 {result['abnormal_count']} 个异常子任务")
                return True
            return False
        except Exception as e:
            print(f"检查异常子任务失败: {e}")
            return False

    @staticmethod
    def parse_filename_for_project_info(filename: str) -> tuple:
        """从文件名解析项目名和项目经理信息"""
        name_without_ext = filename.rsplit('.', 1)[0]  # 移除扩展名
        
        # 尝试匹配 "xxx(项目名)-项目经理姓名" 格式
        match = re.match(r'.*\((.+)\)-(.+)', name_without_ext)
        
        if match:
            project_name = match.group(1).strip()
            manager_name = match.group(2).strip()
        else:
            # 尝试匹配 "项目名-项目经理姓名" 格式
            last_dash_index = name_without_ext.rfind('-')
            if last_dash_index != -1:
                project_name = name_without_ext[:last_dash_index].strip()
                manager_name = name_without_ext[last_dash_index+1:].strip()
            else:
                # 如果都不符合，返回整个名字作为项目名，项目经理为未知
                project_name = name_without_ext
                manager_name = "未知"
        
        return project_name, manager_name

    @staticmethod
    def extract_date_fields_from_dataframe(df) -> Dict[str, List[date]]:
        """从DataFrame中提取日期字段"""
        date_fields = {
            'planned_starts': [],
            'planned_ends': [],
            'actual_starts': [],
            'actual_ends': []
        }
        
        # 定义列名关键词
        planned_start_cols = ['计划开始时间', '计划开始日期', 'planned_start', 'planned_start_date', 'start_date_plan', '计划开始', '计划开工']
        planned_end_cols = ['计划结束时间', '计划结束日期', 'planned_end', 'planned_end_date', 'end_date_plan', '计划结束', '计划完工']
        actual_start_cols = ['实际开始时间', '实际开始日期', 'actual_start', 'actual_start_date', 'start_date_actual', '实际开始', '实际开工']
        actual_end_cols = ['实际结束时间', '实际结束日期', 'actual_end', 'actual_end_date', 'end_date_actual', '实际结束', '实际完工']
        
        import pandas as pd
        
        for col_name in df.columns:
            col_name_clean = col_name.strip().replace('\u3000', '').replace(' ', '')
            col_name_lower = col_name_clean.lower()
            
            # 检查各种日期字段
            if any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                   for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_start_cols]):
                for val in df[col_name]:
                    if pd.notna(val):
                        try:
                            date_val = pd.to_datetime(val).date()
                            date_fields['planned_starts'].append(date_val)
                        except:
                            continue
                            
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                     for keyword in [c.replace('\u3000', '').replace(' ', '') for c in planned_end_cols]):
                for val in df[col_name]:
                    if pd.notna(val):
                        try:
                            date_val = pd.to_datetime(val).date()
                            date_fields['planned_ends'].append(date_val)
                        except:
                            continue
                            
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                     for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_start_cols]):
                for val in df[col_name]:
                    if pd.notna(val):
                        try:
                            date_val = pd.to_datetime(val).date()
                            date_fields['actual_starts'].append(date_val)
                        except:
                            continue
                            
            elif any(keyword.replace('\u3000', '').replace(' ', '').lower() in col_name_lower 
                     for keyword in [c.replace('\u3000', '').replace(' ', '') for c in actual_end_cols]):
                for val in df[col_name]:
                    if pd.notna(val):
                        try:
                            date_val = pd.to_datetime(val).date()
                            date_fields['actual_ends'].append(date_val)
                        except:
                            continue
        
        return date_fields

    @staticmethod
    def get_project_list() -> List[Dict]:
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