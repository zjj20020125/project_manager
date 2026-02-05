"""
NCR业务逻辑服务
处理NCR（不合格品报告）相关的业务逻辑和数据处理
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

# 从database模块导入
from database.database import execute_query

class NcrService:
    """NCR业务逻辑服务类"""
    
    @staticmethod
    def get_ncr_type_distribution() -> List[Dict]:
        """获取NCR类型分布统计"""
        try:
            # 检查jgjncr_copy表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
                # 检查jgjncr表是否存在
                check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
                table_exists = execute_query(check_table_sql)
                if not table_exists:
                    print("警告: jgjncr表也不存在")
                    return []
                table_name = 'jgjncr'
            else:
                table_name = 'jgjncr_copy'
            
            # 检查必要字段是否存在
            describe_sql = f"DESCRIBE {table_name}"
            columns_result = execute_query(describe_sql, fetch_all=True)
            if not columns_result:
                print(f"警告: 无法获取{table_name}表结构")
                return []
            
            column_names = [col['Field'] for col in columns_result if 'Field' in col]
            
            # 检查fsjd字段是否存在
            if 'fsjd' in column_names:
                # 根据fsjd字段统计分布
                type_sql = f"""
                SELECT 
                    COALESCE(fsjd, '未知类型') as type,
                    COUNT(*) as count
                FROM {table_name}
                GROUP BY fsjd
                ORDER BY count DESC
                LIMIT 10
                """
            elif 'problem_category' in column_names:
                # 如果没有fsjd字段，使用problem_category作为备选
                type_sql = f"""
                SELECT 
                    COALESCE(problem_category, '未知类型') as type,
                    COUNT(*) as count
                FROM {table_name}
                GROUP BY problem_category
                ORDER BY count DESC
                LIMIT 10
                """
            elif 'defective_product_name' in column_names:
                # 根据产品名称进行分类
                type_sql = f"""
                SELECT 
                    CASE 
                        WHEN defective_product_name LIKE '%产品%' THEN '产品质量'
                        WHEN defective_product_name LIKE '%工艺%' THEN '工艺问题'
                        WHEN defective_product_name LIKE '%材料%' THEN '材料问题'
                        WHEN defective_product_name LIKE '%设备%' THEN '设备问题'
                        WHEN defective_product_name LIKE '%人员%' THEN '人员问题'
                        ELSE '其他类型'
                    END as type,
                    COUNT(*) as count
                FROM {table_name}
                GROUP BY 
                    CASE 
                        WHEN defective_product_name LIKE '%产品%' THEN '产品质量'
                        WHEN defective_product_name LIKE '%工艺%' THEN '工艺问题'
                        WHEN defective_product_name LIKE '%材料%' THEN '材料问题'
                        WHEN defective_product_name LIKE '%设备%' THEN '设备问题'
                        WHEN defective_product_name LIKE '%人员%' THEN '人员问题'
                        ELSE '其他类型'
                    END
                ORDER BY count DESC
                """
            else:
                # 如果没有合适的分类字段，返回总计数
                total_sql = f"SELECT '总计' as type, COUNT(*) as count FROM {table_name}"
                type_results = execute_query(total_sql, fetch_all=True) or []
                
                formatted_results = []
                for result in type_results:
                    if result is not None and 'type' in result and 'count' in result:
                        formatted_results.append({
                            "name": result['type'],
                            "value": result['count']
                        })
                return formatted_results
            
            type_results = execute_query(type_sql, fetch_all=True) or []
            
            # 格式化返回数据
            formatted_results = []
            for result in type_results:
                if result is not None and 'type' in result and 'count' in result:
                    formatted_results.append({
                        "name": result['type'],
                        "value": result['count']
                    })
            
            # 如果没有数据，返回默认类型分布
            if not formatted_results:
                formatted_results = [
                    {"name": "产品质量", "value": 0},
                    {"name": "工艺问题", "value": 0},
                    {"name": "材料问题", "value": 0},
                    {"name": "设备问题", "value": 0},
                    {"name": "人员问题", "value": 0}
                ]
            
            return formatted_results
        except Exception as e:
            print(f"获取NCR类型分布统计出错: {e}")
            return []

    @staticmethod
    def get_ncr_stage_distribution() -> List[Dict]:
        """获取NCR发生阶段分布统计"""
        try:
            # 检查jgjncr_copy表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
                # 检查jgjncr表是否存在
                check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
                table_exists = execute_query(check_table_sql)
                if not table_exists:
                    print("警告: jgjncr表也不存在")
                    return []
                table_name = 'jgjncr'
            else:
                table_name = 'jgjncr_copy'
            
            # 检查必要字段是否存在
            describe_sql = f"DESCRIBE {table_name}"
            columns_result = execute_query(describe_sql, fetch_all=True)
            if not columns_result:
                print(f"警告: 无法获取{table_name}表结构")
                return []
            
            column_names = [col['Field'] for col in columns_result if 'Field' in col]
            
            # 检查fsjd字段是否存在
            if 'fsjd' in column_names:
                # 根据fsjd字段统计分布
                stage_sql = f"""
                SELECT 
                    COALESCE(fsjd, '未知阶段') as stage,
                    COUNT(*) as count
                FROM {table_name}
                GROUP BY fsjd
                ORDER BY count DESC
                LIMIT 10
                """
            elif 'occurrence_stage' in column_names:
                # 如果没有fsjd字段，使用occurrence_stage作为备选
                stage_sql = f"""
                SELECT 
                    COALESCE(occurrence_stage, '未知阶段') as stage,
                    COUNT(*) as count
                FROM {table_name}
                GROUP BY occurrence_stage
                ORDER BY count DESC
                LIMIT 10
                """
            else:
                # 如果没有合适的阶段字段，返回总计数
                total_sql = f"SELECT '总计' as stage, COUNT(*) as count FROM {table_name}"
                stage_results = execute_query(total_sql, fetch_all=True) or []
                
                formatted_results = []
                for result in stage_results:
                    if result is not None and 'stage' in result and 'count' in result:
                        formatted_results.append({
                            "name": result['stage'],
                            "value": result['count']
                        })
                return formatted_results
            
            stage_results = execute_query(stage_sql, fetch_all=True) or []
            
            # 格式化返回数据
            formatted_results = []
            for result in stage_results:
                if result is not None and 'stage' in result and 'count' in result:
                    formatted_results.append({
                        "name": result['stage'],
                        "value": result['count']
                    })
            
            # 如果没有数据，返回默认阶段分布
            if not formatted_results:
                formatted_results = [
                    {"name": "生产中", "value": 0},
                    {"name": "安装后", "value": 0},
                    {"name": "检验时", "value": 0},
                    {"name": "使用中", "value": 0},
                    {"name": "运输中", "value": 0}
                ]
            
            return formatted_results
        except Exception as e:
            print(f"获取NCR发生阶段分布统计出错: {e}")
            return []

    @staticmethod
    def get_responsibility_analysis() -> List[Dict]:
        """获取评审阶段责任人员分布统计"""
        try:
            # 检查jgjncr_copy表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr_copy表不存在")
                return []
            
            # 检查必要字段是否存在
            describe_sql = "DESCRIBE jgjncr_copy"
            columns_result = execute_query(describe_sql, fetch_all=True)
            if not columns_result:
                print("警告: 无法获取jgjncr_copy表结构")
                return []
            
            column_names = [col['Field'] for col in columns_result if 'Field' in col]
            
            # 检查dqjd和wczz字段是否存在
            if 'dqjd' not in column_names or 'wczz' not in column_names:
                print("警告: jgjncr_copy表缺少dqjd或wczz字段")
                return []
            
            # 查询dqjd为'3-评审'的记录中wczz字段的统计
            responsibility_sql = """
            SELECT wczz
            FROM jgjncr_copy
            WHERE dqjd = '3-评审' AND wczz IS NOT NULL AND TRIM(wczz) != ''
            """
            
            wczz_results = execute_query(responsibility_sql, fetch_all=True) or []
            
            # 统计每个人员姓名出现的次数
            name_count = {}
            for row in wczz_results:
                if row and 'wczz' in row:
                    wczz_value = row['wczz']
                    if wczz_value:
                        # 按多种分隔符分割姓名
                        names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                        for name in names:
                            name = name.strip()
                            if name and name != 'nan' and name != 'NULL':
                                name_count[name] = name_count.get(name, 0) + 1
            
            # 格式化返回数据
            formatted_results = []
            for name, count in name_count.items():
                formatted_results.append({
                    "name": name,
                    "value": count
                })
            
            # 按数量降序排列，返回前五名
            formatted_results.sort(key=lambda x: x['value'], reverse=True)
            return formatted_results[:5]
        except Exception as e:
            print(f"获取责任人员分析统计出错: {e}")
            return []

    @staticmethod
    def get_dqjd_wczz_data(exclude_completed: bool = True) -> Dict:
        """获取DQJD和WCZZ数据统计"""
        try:
            # 检查jgjncr_copy表是否存在
            check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
                # 检查jgjncr表是否存在
                check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
                table_exists = execute_query(check_table_sql)
                if not table_exists:
                    print("警告: jgjncr表也不存在")
                    return {"dqjdStats": [], "wczzStats": [], "tableData": []}
                table_name = 'jgjncr'
            else:
                table_name = 'jgjncr_copy'
            
            # 检查必要字段是否存在
            describe_sql = f"DESCRIBE {table_name}"
            columns_result = execute_query(describe_sql, fetch_all=True)
            if not columns_result:
                print(f"警告: 无法获取{table_name}表结构")
                return {"dqjdStats": [], "wczzStats": [], "tableData": []}
            
            column_names = [col['Field'] for col in columns_result if 'Field' in col]
            
            # 检查所需字段是否存在
            if 'dqjd' not in column_names:
                print(f"警告: {table_name}表中没有dqjd字段")
                return {"dqjdStats": [], "wczzStats": [], "tableData": []}
            
            if 'wczz' not in column_names:
                print(f"警告: {table_name}表中没有wczz字段")
                return {"dqjdStats": [], "wczzStats": [], "tableData": []}
            
            # 构建查询条件
            where_clause = "WHERE dqjd != %s OR dqjd IS NULL" if exclude_completed else ""
            exclude_value = '9-完成' if exclude_completed else None
            
            # 查询DQJD统计
            dqjd_sql = f"SELECT dqjd, COUNT(*) as count FROM {table_name} {where_clause} GROUP BY dqjd ORDER BY count DESC"
            dqjd_params = (exclude_value,) if exclude_completed else ()
            dqjd_data = execute_query(dqjd_sql, dqjd_params, fetch_all=True) or []
            
            # 格式化DQJD统计数据
            dqjd_stats = []
            for record in dqjd_data:
                if record and record.get('dqjd') is not None:
                    dqjd_stats.append({
                        'name': record['dqjd'],
                        'value': record['count']
                    })
            
            # 查询WCZZ原始数据
            wczz_sql = f"SELECT wczz FROM {table_name} {where_clause}"
            wczz_raw_data = execute_query(wczz_sql, dqjd_params, fetch_all=True) or []
            
            # 格式化WCZZ统计数据
            wczz_stats_dict = {}
            for record in wczz_raw_data:
                if record and record.get('wczz') is not None:
                    wczz_value = record['wczz']
                    # 按多种分隔符分割姓名
                    names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                    for name in names:
                        name = name.strip()
                        if name:
                            if name in wczz_stats_dict:
                                wczz_stats_dict[name] += 1
                            else:
                                wczz_stats_dict[name] = 1
            
            # 转换为数组格式
            wczz_stats = []
            for name, count in wczz_stats_dict.items():
                wczz_stats.append({
                    'name': name,
                    'value': count
                })
            
            # 查询详细表格数据
            table_sql = f"SELECT * FROM {table_name} {where_clause} ORDER BY create_date DESC LIMIT 100"
            table_data = execute_query(table_sql, dqjd_params, fetch_all=True) or []
            
            # 格式化表格数据
            formatted_table_data = []
            for record in table_data:
                if record is not None:
                    formatted_record = {}
                    for key, value in record.items():
                        # 处理日期字段
                        if isinstance(value, datetime):
                            formatted_record[key] = str(value)
                        # 处理数字字段
                        elif hasattr(value, 'quantize'):
                            formatted_record[key] = float(value)
                        else:
                            formatted_record[key] = value
                    formatted_table_data.append(formatted_record)
            
            return {
                "dqjdStats": dqjd_stats,
                "wczzStats": wczz_stats,
                "tableData": formatted_table_data
            }
        except Exception as e:
            print(f"获取DQJD/WCZZ数据出错: {e}")
            import traceback
            traceback.print_exc()
            return {"dqjdStats": [], "wczzStats": [], "tableData": []}

    @staticmethod
    def format_ncr_record(record: Dict) -> Dict:
        """格式化NCR记录数据"""
        formatted_record = {}
        for key, value in record.items():
            # 处理日期字段
            if isinstance(value, datetime):
                formatted_record[key] = str(value)
            # 处理数字字段
            elif hasattr(value, 'quantize'):
                formatted_record[key] = float(value)
            else:
                formatted_record[key] = value
        return formatted_record