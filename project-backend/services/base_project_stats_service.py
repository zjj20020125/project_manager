"""
通用项目统计服务 - 可复用于任何需要项目统计的项目

特性:
- 完全解耦，不依赖特定业务场景
- 支持自定义统计维度
- 灵活的日期判定逻辑
- 可配置的状态分类规则
- 统一的错误处理

使用方式:
1. 直接导入使用
2. 继承后重写部分方法
3. 作为 mixin 混入其他服务

示例:
from services.base_project_stats_service import BaseProjectStatsService

class CustomProjectStatsService(BaseProjectStatsService):
    # 可以重写统计逻辑
    pass
"""

from typing import List, Dict, Optional
from datetime import datetime, date


class BaseProjectStatsService:
    """基础项目统计服务类"""
    
    # 可配置的表名
    TABLE_NAME = 'projects'
    
    # 可配置的字段映射
    FIELD_MAPPING = {
        'planned_start': 'planned_start_date',
        'planned_end': 'planned_end_date',
        'actual_start': 'actual_start_date',
        'actual_end': 'actual_end_date',
        'status': 'project_status'
    }
    
    # 可配置的状态分类
    STATUS_CATEGORIES = {
        'not_started': '未开始',
        'ongoing': '进行中',
        'completed': '已结项'
    }
    
    @classmethod
    def get_project_statistics(cls) -> Dict:
        """
        获取项目统计数据
        
        返回格式:
        {
            "total_projects": 150,
            "not_started_projects": 30,
            "ongoing_projects": 95,
            "completed_projects": 25
        }
        """
        try:
            # 从 database 模块导入
            from database.database import execute_query
            
            # 检查表是否存在
            if not cls._table_exists(execute_query):
                return cls._get_empty_stats()
            
            # 检查必要字段
            if not cls._validate_fields(execute_query):
                return cls._get_empty_stats()
            
            # 查询总数
            total = cls._count_total(execute_query)
            
            # 查询未开始数量
            not_started = cls._count_not_started(execute_query)
            
            # 查询已结项数量
            completed = cls._count_completed(execute_query)
            
            # 计算进行中数量
            ongoing = total - not_started - completed
            
            return {
                "total_projects": total,
                "not_started_projects": not_started,
                "ongoing_projects": ongoing,
                "completed_projects": completed
            }
            
        except Exception as e:
            print(f"获取项目统计数据出错：{e}")
            return cls._get_empty_stats()
    
    @classmethod
    def _table_exists(cls, execute_query) -> bool:
        """检查表是否存在"""
        check_sql = f"SHOW TABLES LIKE '{cls.TABLE_NAME}'"
        return bool(execute_query(check_sql))
    
    @classmethod
    def _validate_fields(cls, execute_query) -> bool:
        """验证必要字段是否存在"""
        describe_sql = f"DESCRIBE {cls.TABLE_NAME}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        
        if not columns_result:
            return False
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        required_columns = [
            cls.FIELD_MAPPING['planned_start'],
            cls.FIELD_MAPPING['actual_end']
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"警告：{cls.TABLE_NAME}表缺少以下列：{missing_columns}")
            return False
        
        return True
    
    @classmethod
    def _count_total(cls, execute_query) -> int:
        """查询总项目数"""
        total_sql = f"SELECT COUNT(*) as count FROM {cls.TABLE_NAME}"
        total_result = execute_query(total_sql)
        return total_result["count"] if total_result and "count" in total_result else 0
    
    @classmethod
    def _count_not_started(cls, execute_query) -> int:
        """
        查询未开始项目数
        
        判定逻辑：当前日期 < 计划开始日期
        可通过重写此方法自定义判定规则
        """
        field_name = cls.FIELD_MAPPING['planned_start']
        not_started_sql = f"""
        SELECT COUNT(*) as count FROM {cls.TABLE_NAME} 
        WHERE CURDATE() < {field_name}
        """
        not_started_result = execute_query(not_started_sql)
        return not_started_result["count"] if not_started_result and "count" in not_started_result else 0
    
    @classmethod
    def _count_completed(cls, execute_query) -> int:
        """
        查询已结项项目数
        
        判定逻辑：实际结束日期存在 AND 实际结束日期 < 当前日期
        可通过重写此方法自定义判定规则
        """
        field_name = cls.FIELD_MAPPING['actual_end']
        completed_sql = f"""
        SELECT COUNT(*) as count FROM {cls.TABLE_NAME} 
        WHERE {field_name} IS NOT NULL AND {field_name} < CURDATE()
        """
        completed_result = execute_query(completed_sql)
        return completed_result["count"] if completed_result and "count" in completed_result else 0
    
    @staticmethod
    def _get_empty_stats() -> Dict:
        """返回空统计数据"""
        return {
            "total_projects": 0,
            "not_started_projects": 0,
            "ongoing_projects": 0,
            "completed_projects": 0
        }
    
    @classmethod
    def categorize_project(cls, project_data: Dict) -> str:
        """
        对单个项目进行状态分类
        
        参数:
            project_data: 包含日期字段的项目数据
        
        返回:
            状态分类：'未开始' | '进行中' | '已结项'
        
        可通过重写此方法自定义分类逻辑
        """
        current_date = datetime.now().date()
        
        planned_start = project_data.get(cls.FIELD_MAPPING['planned_start'])
        actual_end = project_data.get(cls.FIELD_MAPPING['actual_end'])
        
        # 确保是 date 类型
        if isinstance(planned_start, datetime):
            planned_start = planned_start.date()
        if isinstance(actual_end, datetime):
            actual_end = actual_end.date()
        
        # 已结项判定
        if actual_end and actual_end < current_date:
            return cls.STATUS_CATEGORIES['completed']
        
        # 未开始判定
        if planned_start and planned_start > current_date:
            return cls.STATUS_CATEGORIES['not_started']
        
        # 默认：进行中
        return cls.STATUS_CATEGORIES['ongoing']
    
    @classmethod
    def categorize_projects(cls, projects_data: List[Dict]) -> List[Dict]:
        """
        对项目列表进行批量分类
        
        参数:
            projects_data: 项目数据列表
        
        返回:
            添加了 category 字段的项目列表
        """
        categorized = []
        
        for project in projects_data:
            if project is None:
                continue
            
            proj_dict = dict(project)
            proj_dict['category'] = cls.categorize_project(proj_dict)
            categorized.append(proj_dict)
        
        return categorized


# ============================================================================
# 扩展服务示例 - 可以根据需要添加更多统计维度
# ============================================================================

class AdvancedProjectStatsService(BaseProjectStatsService):
    """
    高级项目统计服务 - 扩展更多统计维度
    
    示例用法:
    stats = AdvancedProjectStatsService.get_advanced_statistics()
    """
    
    @classmethod
    def get_advanced_statistics(cls) -> Dict:
        """
        获取更详细的项目统计数据
        
        返回格式:
        {
            "basic": {...},  // 基础统计（来自父类）
            "by_month": [...],  // 按月统计
            "by_manager": [...],  // 按负责人统计
            "delayed_projects": {...}  // 延期项目统计
        }
        """
        try:
            from database.database import execute_query
            
            # 基础统计
            basic_stats = cls.get_project_statistics()
            
            # 按月统计（可选）
            monthly_stats = cls._get_monthly_stats(execute_query)
            
            # 按负责人统计（可选）
            manager_stats = cls._get_manager_stats(execute_query)
            
            # 延期项目统计（可选）
            delayed_stats = cls._get_delayed_projects_stats(execute_query)
            
            return {
                "basic": basic_stats,
                "by_month": monthly_stats,
                "by_manager": manager_stats,
                "delayed_projects": delayed_stats
            }
            
        except Exception as e:
            print(f"获取高级统计数据出错：{e}")
            return {
                "basic": cls._get_empty_stats(),
                "by_month": [],
                "by_manager": [],
                "delayed_projects": {"count": 0, "projects": []}
            }
    
    @classmethod
    def _get_monthly_stats(cls, execute_query) -> List[Dict]:
        """
        获取按月统计的项目数量
        
        返回格式:
        [
            {"month": "2024-01", "count": 10},
            {"month": "2024-02", "count": 15},
            ...
        ]
        """
        try:
            start_field = cls.FIELD_MAPPING['planned_start']
            monthly_sql = f"""
            SELECT DATE_FORMAT({start_field}, '%Y-%m') as month, 
                   COUNT(*) as count
            FROM {cls.TABLE_NAME}
            WHERE {start_field} IS NOT NULL
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
            """
            
            results = execute_query(monthly_sql, fetch_all=True) or []
            return [dict(r) for r in results]
            
        except Exception as e:
            print(f"获取月度统计失败：{e}")
            return []
    
    @classmethod
    def _get_manager_stats(cls, execute_query) -> List[Dict]:
        """
        获取按负责人统计的项目数量
        
        返回格式:
        [
            {"manager": "张三", "count": 5},
            {"manager": "李四", "count": 8},
            ...
        ]
        """
        try:
            manager_field = 'project_manager'  # 可以根据需要配置
            manager_sql = f"""
            SELECT {manager_field} as manager, 
                   COUNT(*) as count
            FROM {cls.TABLE_NAME}
            WHERE {manager_field} IS NOT NULL AND {manager_field} != ''
            GROUP BY {manager_field}
            ORDER BY count DESC
            """
            
            results = execute_query(manager_sql, fetch_all=True) or []
            return [dict(r) for r in results]
            
        except Exception as e:
            print(f"获取负责人统计失败：{e}")
            return []
    
    @classmethod
    def _get_delayed_projects_stats(cls, execute_query) -> Dict:
        """
        获取延期项目统计
        
        返回格式:
        {
            "count": 5,
            "projects": [...]
        }
        """
        try:
            # 延期判定：当前日期 > 计划结束日期 AND (无实际结束日期 OR 实际结束日期 > 计划结束日期)
            planned_end = cls.FIELD_MAPPING['planned_end']
            actual_end = cls.FIELD_MAPPING['actual_end']
            
            delayed_sql = f"""
            SELECT * FROM {cls.TABLE_NAME}
            WHERE {planned_end} IS NOT NULL 
              AND CURDATE() > {planned_end}
              AND ({actual_end} IS NULL OR {actual_end} > {planned_end})
            """
            
            delayed_projects = execute_query(delayed_sql, fetch_all=True) or []
            
            return {
                "count": len(delayed_projects),
                "projects": [dict(p) for p in delayed_projects]
            }
            
        except Exception as e:
            print(f"获取延期项目统计失败：{e}")
            return {"count": 0, "projects": []}
