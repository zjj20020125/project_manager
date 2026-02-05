"""
NCR管理相关API接口
包含NCR统计、查询、详情等功能
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

# 从database模块导入
from database.database import execute_query

# 创建路由器实例
router = APIRouter(prefix="/v1", tags=["NCR管理"])

# 21. 获取NCR类型分布统计（用于饼图）
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

# 22. 获取NCR发生阶段分布统计
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

# 23. 获取评审阶段责任人员分布统计
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

# 23. 根据阶段获取NCR数据
@router.get("/ncr/by-stage")
async def get_ncr_by_stage(stage: str = None, status: str = None, priority: str = None, page: int = 1, limit: int = 20):
    """根据阶段获取NCR数据"""
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
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
                return {"data": [], "total": 0}
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return {"data": [], "total": 0}
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 构建查询条件
        conditions = []
        params = []
        
        if stage:
            if 'fsjd' in column_names:
                conditions.append("fsjd = %s")
                params.append(stage)
            elif 'occurrence_stage' in column_names:
                conditions.append("occurrence_stage = %s")
                params.append(stage)
            else:
                print("警告: 表中没有fsjd或occurrence_stage字段")
                return {"data": [], "total": 0}
        
        if status:
            if 'status' in column_names:
                conditions.append("status = %s")
                params.append(status)
            else:
                print("警告: 表中没有status字段")
        
        if priority:
            if 'review_level' in column_names:
                conditions.append("review_level = %s")
                params.append(priority)
            else:
                print("警告: 表中没有review_level字段")
        
        # 构建WHERE子句
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询数据总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
        count_result = execute_query(count_sql, tuple(params))
        total_count = count_result.get('total', 0) if count_result else 0
        
        # 查询数据
        query_sql = f"""
        SELECT * FROM {table_name} 
        WHERE {where_clause}
        ORDER BY create_date DESC, process_no DESC
        LIMIT %s OFFSET %s
        """
        
        # 添加LIMIT和OFFSET参数
        params.extend([limit, offset])
        
        ncr_data = execute_query(query_sql, tuple(params), fetch_all=True) or []
        
        # 格式化数据
        formatted_data = []
        for record in ncr_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    # 处理日期字段
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    # 处理数字字段
                    elif hasattr(value, 'quantize'):  # Decimal类型
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_data.append(formatted_record)
        
        return {
            "data": formatted_data,
            "total": total_count
        }
    except Exception as e:
        print(f"根据阶段获取NCR数据出错: {e}")
        return {"data": [], "total": 0}

# 24. 获取NCR详情
@router.get("/ncr/detail/{process_no}")
async def get_ncr_detail(process_no: str):
    """获取NCR详情"""
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
                raise HTTPException(status_code=404, detail="NCR表不存在")
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            raise HTTPException(status_code=404, detail="无法获取表结构")
        
        # 查询特定NCR记录
        query_sql = f"SELECT * FROM {table_name} WHERE process_no = %s"
        ncr_record = execute_query(query_sql, (process_no,), fetch_one=True)
        
        if not ncr_record:
            raise HTTPException(status_code=404, detail=f"未找到NCR编号为 {process_no} 的记录")
        
        # 格式化数据
        formatted_record = {}
        for key, value in ncr_record.items():
            # 处理日期字段
            if isinstance(value, datetime):
                formatted_record[key] = str(value)
            # 处理数字字段
            elif hasattr(value, 'quantize'):  # Decimal类型
                formatted_record[key] = float(value)
            else:
                formatted_record[key] = value
        
        return formatted_record
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取NCR详情出错: {e}")
        raise HTTPException(status_code=500, detail="获取NCR详情失败")

# 25. 获取NCR列表
@router.get("/ncr/list")
async def get_ncr_list(page: int = 1, limit: int = 20):
    """获取NCR列表"""
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
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
        
        # 查询NCR数据
        query_sql = f"""
        SELECT * FROM {table_name}
        ORDER BY create_date DESC, process_no DESC
        LIMIT %s OFFSET %s
        """
        
        ncr_data = execute_query(query_sql, (limit, offset), fetch_all=True) or []
        
        # 格式化数据
        formatted_data = []
        for record in ncr_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    # 处理日期字段
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    # 处理数字字段
                    elif hasattr(value, 'quantize'):  # Decimal类型
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_data.append(formatted_record)
        
        return formatted_data
    except Exception as e:
        print(f"获取NCR列表出错: {e}")
        return []

# 26. 获取DQJD和WCZZ数据统计
@router.get("/dqjd-wczz-data")
async def get_dqjd_wczz_data():
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
        
        # 构建查询条件 - 只查询DQJD不等于'9-完成'的记录
        where_clause = "WHERE dqjd != %s OR dqjd IS NULL"
        exclude_value = '9-完成'
        
        # 查询DQJD统计
        dqjd_sql = f"SELECT dqjd, COUNT(*) as count FROM {table_name} {where_clause} GROUP BY dqjd ORDER BY count DESC"
        dqjd_data = execute_query(dqjd_sql, (exclude_value,), fetch_all=True) or []
        
        # 格式化DQJD统计数据
        dqjd_stats = []
        for record in dqjd_data:
            if record and record.get('dqjd') is not None:
                dqjd_stats.append({
                    'name': record['dqjd'],
                    'value': record['count']
                })
        
        # 查询WCZZ原始数据（不进行GROUP BY，以便拆分多个姓名）
        wczz_sql = f"SELECT wczz FROM {table_name} {where_clause}"
        wczz_raw_data = execute_query(wczz_sql, (exclude_value,), fetch_all=True) or []
        
        # 格式化WCZZ统计数据 - 拆分多个姓名并累加计数
        wczz_stats_dict = {}
        for record in wczz_raw_data:
            if record and record.get('wczz') is not None:
                wczz_value = record['wczz']
                # 按多种分隔符分割姓名：逗号、中文逗号、分号、中文分号、顿号
                import re
                names = re.split(r'[,,，,;,；,、,+]', str(wczz_value))
                for name in names:
                    name = name.strip()  # 去除空白字符
                    if name:  # 确保姓名不为空
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
        table_data = execute_query(table_sql, (exclude_value,), fetch_all=True) or []
        
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
                    elif hasattr(value, 'quantize'):  # Decimal类型
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