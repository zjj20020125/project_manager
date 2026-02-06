"""
NCR管理相关路由模块
包含NCR统计、查询、详情等功能
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

# 从database模块导入
from database.database import execute_query

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["NCR管理"])

# 1. 获取NCR类型分布统计（用于饼图）
@router.get("/ncr/type-distribution", response_model=List[dict])
def get_ncr_type_distribution():
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
            LIMIT 10  -- 限制最多返回10种类型
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
            # 如果没有problem_category，可以根据defective_product_name的首字母或其他方式进行分类
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

# 2. 获取NCR发生阶段分布统计
@router.get("/ncr/stage-distribution", response_model=List[dict])
def get_ncr_stage_distribution():
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
            LIMIT 10  -- 限制最多返回10种阶段
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

# 3. 获取评审阶段责任人员分布统计
@router.get("/ncr/responsibility-analysis", response_model=List[dict])
def get_responsibility_analysis():
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
        
        # 统计每个人员姓名出现的次数（先拆分wczz字段中的姓名）
        name_count = {}
        for row in wczz_results:
            if row and 'wczz' in row:
                wczz_value = row['wczz']
                if wczz_value:
                    # 按逗号或分号拆分姓名
                    names = []
                    # 尝试多种可能的分隔符
                    if ',' in wczz_value:
                        names = wczz_value.split(',')
                    elif '，' in wczz_value:
                        names = wczz_value.split('，')
                    elif ';' in wczz_value:
                        names = wczz_value.split(';')
                    elif '；' in wczz_value:
                        names = wczz_value.split('；')
                    else:
                        names = [wczz_value]
                    
                    # 清理姓名并统计
                    for name in names:
                        clean_name = name.strip()
                        if clean_name and clean_name != 'nan' and clean_name != 'NULL':
                            name_count[clean_name] = name_count.get(clean_name, 0) + 1
        
        # 格式化返回数据
        formatted_results = []
        for name, count in name_count.items():
            formatted_results.append({
                "name": name,
                "value": count
            })
        
        # 按数量降序排列
        formatted_results.sort(key=lambda x: x['value'], reverse=True)
        
        # 只返回前五名
        return formatted_results[:5]
    except Exception as e:
        print(f"获取责任人员分析统计出错: {e}")
        return []

# 4. 获取未评审阶段责任人员分布统计（前15名）
@router.get("/ncr/unreviewed-stage-responsibility", response_model=List[dict])
def get_unreviewed_stage_responsibility():
    """
    获取未评审阶段责任人员分布统计（前15名）
    数据来源：jgjncr_copy表中dqjd='3-未评审'的记录，统计wczz字段中各人员的数量
    """
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
        
        # 查询dqjd为'3-未评审'的记录中wczz字段的统计
        unreviewed_sql = """
        SELECT wczz
        FROM jgjncr_copy
        WHERE dqjd = '3-未评审' AND wczz IS NOT NULL AND TRIM(wczz) != ''
        """
        
        wczz_results = execute_query(unreviewed_sql, fetch_all=True) or []
        
        # 统计每个人员姓名出现的次数（先拆分wczz字段中的姓名）
        name_count = {}
        for record in wczz_results:
            if record and record.get('wczz'):
                wczz_value = record['wczz']
                # 按多种分隔符分割姓名：逗号、中文逗号、分号、中文分号、顿号、加号
                import re
                names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                for name in names:
                    name = name.strip()  # 去除空白字符
                    if name:  # 确保姓名不为空
                        if name in name_count:
                            name_count[name] += 1
                        else:
                            name_count[name] = 1
        
        # 转换为数组格式
        formatted_results = []
        for name, count in name_count.items():
            formatted_results.append({
                "name": name,
                "value": count
            })
        
        # 按数量降序排列
        formatted_results.sort(key=lambda x: x['value'], reverse=True)
        
        # 只返回前15名
        return formatted_results[:15]
    except Exception as e:
        print(f"获取未评审阶段责任人员分布出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 5. 获取未评审状态下的负责人统计（前15名）
@router.get("/ncr/unreviewed-responsibility", response_model=List[dict])
def get_unreviewed_responsibility_stats():
    """获取未评审状态下的负责人统计"""
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
        
        # 查询dqjd为'3-未评审'的记录中wczz字段的统计
        unreviewed_sql = """
        SELECT wczz
        FROM jgjncr_copy
        WHERE dqjd = '3-未评审' AND wczz IS NOT NULL AND TRIM(wczz) != ''
        """
        
        wczz_results = execute_query(unreviewed_sql, fetch_all=True) or []
        
        # 统计每个人员姓名出现的次数（先拆分wczz字段中的姓名）
        name_count = {}
        for record in wczz_results:
            if record and record.get('wczz'):
                wczz_value = record['wczz']
                # 按多种分隔符分割姓名：逗号、中文逗号、分号、中文分号、顿号、加号
                import re
                names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                for name in names:
                    name = name.strip()  # 去除空白字符
                    if name:  # 确保姓名不为空
                        if name in name_count:
                            name_count[name] += 1
                        else:
                            name_count[name] = 1
        
        # 转换为数组格式
        formatted_results = []
        for name, count in name_count.items():
            formatted_results.append({
                "name": name,
                "value": count
            })
        
        # 按数量降序排列
        formatted_results.sort(key=lambda x: x['value'], reverse=True)
        
        # 只返回前15名
        return formatted_results[:15]
    except Exception as e:
        print(f"获取未评审责任人统计出错: {e}")
        import traceback
        traceback.print_exc()
        return []