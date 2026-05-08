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
        
        # 构建 WHERE 子句
        where_clause = " AND ".join(conditions) if conditions else "1=1"
                
        print(f"🔍 [DEBUG] 查询条件：{where_clause}")
        print(f"🔍 [DEBUG] WHERE 参数：{params}")
                
        # 查询数据总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
        count_result = execute_query(count_sql, tuple(params))
        total_count = count_result.get('total', 0) if count_result else 0
                
        print(f"🔍 [DEBUG] 总记录数：{total_count}")
                
        # 确定排序字段（使用实际存在的字段）
        order_field = None
        if 'create_date' in column_names:
            order_field = 'create_date'
        elif 'create_time' in column_names:
            order_field = 'create_time'
        elif 'occur_date' in column_names:
            order_field = 'occur_date'
        elif 'process_no' in column_names:
            order_field = 'process_no'
        else:
            # 如果都没有，使用第一个字段排序
            order_field = column_names[0] if column_names else '*'
            print(f"警告：表中没有找到合适的排序字段，使用 {order_field} 排序")
        
        print(f"🔍 [DEBUG] 使用排序字段：{order_field}")
        
        # 查询数据 - 只使用一个排序字段，避免 process_no 不存在的情况
        query_sql = f"""
        SELECT * FROM {table_name} 
        WHERE {where_clause}
        ORDER BY {order_field} DESC
        LIMIT %s OFFSET %s
        """
                
        # 构建完整的参数列表（WHERE 条件参数 + LIMIT + OFFSET）
        query_params = params.copy() if isinstance(params, list) else list(params)
        query_params.extend([limit, offset])
                
        print(f"🔍 [DEBUG] 查询 SQL: {query_sql}")
        print(f"🔍 [DEBUG] 完整参数：{tuple(query_params)}")
                
        ncr_data = execute_query(query_sql, tuple(query_params), fetch_all=True) or []
                
        print(f"🔍 [DEBUG] 查询结果数量：{len(ncr_data)}")
        
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
    """获取NCR列表（带分页）"""
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
                
        # 确定排序字段
        order_field = None
        if 'create_date' in column_names:
            order_field = 'create_date'
        elif 'create_time' in column_names:
            order_field = 'create_time'
        elif 'occur_date' in column_names:
            order_field = 'occur_date'
        elif 'process_no' in column_names:
            order_field = 'process_no'
        else:
            order_field = column_names[0] if column_names else '*'
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name}"
        count_result = execute_query(count_sql, fetch_one=True)
        total_count = count_result['total'] if count_result else 0
        
        # 查询 NCR 数据 - 只使用一个排序字段
        query_sql = f"""
        SELECT * FROM {table_name}
        ORDER BY {order_field} DESC
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
        
        return {
            "data": formatted_data,
            "total": total_count
        }
    except Exception as e:
        print(f"获取NCR列表出错: {e}")
        import traceback
        traceback.print_exc()
        return {"data": [], "total": 0}

# 25.1 获取NCR统计数据（用于顶部卡片）
@router.get("/ncr/stats")
async def get_ncr_stats():
    """获取NCR统计数据：总数、已完成、待处理、完成率"""
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在，尝试使用jgjncr表")
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告: jgjncr表也不存在")
                return {
                    "total": 0,
                    "completed": 0,
                    "pending": 0,
                    "completion_rate": "0%"
                }
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查dqjd字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告: 无法获取{table_name}表结构")
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "completion_rate": "0%"
            }
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        if 'dqjd' not in column_names:
            print(f"警告: {table_name}表中没有dqjd字段")
            return {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "completion_rate": "0%"
            }
        
        # 查询总数
        total_sql = f"SELECT COUNT(*) as total FROM {table_name}"
        total_result = execute_query(total_sql, fetch_one=True)
        total_count = total_result['total'] if total_result else 0
        
        # 查询已完成数量（dqjd包含'完成'或'关闭'）
        completed_sql = f"""
        SELECT COUNT(*) as completed 
        FROM {table_name} 
        WHERE dqjd LIKE '%完成%' OR dqjd LIKE '%关闭%'
        """
        completed_result = execute_query(completed_sql, fetch_one=True)
        completed_count = completed_result['completed'] if completed_result else 0
        
        # 查询待处理数量（dqjd包含'未评审'或'待处理'或不包含'完成'）
        pending_sql = f"""
        SELECT COUNT(*) as pending 
        FROM {table_name} 
        WHERE dqjd LIKE '%未评审%' OR dqjd LIKE '%待处理%' OR (dqjd NOT LIKE '%完成%' AND dqjd NOT LIKE '%关闭%')
        """
        pending_result = execute_query(pending_sql, fetch_one=True)
        pending_count = pending_result['pending'] if pending_result else 0
        
        # 计算完成率
        completion_rate = "0%"
        if total_count > 0:
            rate = round((completed_count / total_count) * 100)
            completion_rate = f"{rate}%"
        
        return {
            "total": total_count,
            "completed": completed_count,
            "pending": pending_count,
            "completion_rate": completion_rate
        }
    except Exception as e:
        print(f"获取NCR统计数据出错: {e}")
        import traceback
        traceback.print_exc()
        return {
            "total": 0,
            "completed": 0,
            "pending": 0,
            "completion_rate": "0%"
        }

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


# 28. 获取未评审阶段责任人员分布统计（前15名）
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


# 27. 获取未评审状态下的负责人统计（用于展示dqjd为'3-未评审'的记录中wczz字段的人员统计，显示前15名）
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

# 29. 获取SSCX字段统计（近一年数据）
@router.get("/ncr/sscx-statistics", response_model=List[dict])
def get_sscx_statistics():
    """
    获取jgjncr_copy表中sscx字段的种类和数量统计
    根据cjrq字段筛选近一年的数据
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
        
        # 检查sscx和cjrq字段是否存在
        if 'sscx' not in column_names:
            print("警告: jgjncr_copy表缺少sscx字段")
            return []
        
        if 'cjrq' not in column_names:
            print("警告: jgjncr_copy表缺少cjrq字段")
            return []
        
        # 计算一年前的日期
        from datetime import datetime, timedelta
        one_year_ago = datetime.now() - timedelta(days=365)
        one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
        
        # 查询近一年内sscx字段的统计
        sscx_sql = """
        SELECT 
            COALESCE(sscx, '未知') as sscx_type,
            COUNT(*) as count
        FROM jgjncr_copy
        WHERE cjrq >= %s AND sscx IS NOT NULL AND TRIM(sscx) != ''
        GROUP BY sscx
        ORDER BY count DESC
        """
        
        sscx_results = execute_query(sscx_sql, (one_year_ago_str,), fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in sscx_results:
            if result is not None and 'sscx_type' in result and 'count' in result:
                formatted_results.append({
                    "name": result['sscx_type'],
                    "value": result['count']
                })
        
        # 如果没有数据，返回空数组而不是默认值
        if not formatted_results:
            print("警告: 近一年内没有找到有效的sscx数据")
            return []
        
        return formatted_results
    except Exception as e:
        print(f"获取SSCX统计出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 30. 获取SSCX时间趋势统计（按月份展示近一年数据）
@router.get("/ncr/sscx-trend", response_model=List[dict])
def get_sscx_trend_statistics():
    """
    获取jgjncr_copy表中sscx字段的时间趋势统计
    按月份统计近一年内各类sscx的数量变化
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
        
        # 检查sscx和cjrq字段是否存在
        if 'sscx' not in column_names:
            print("警告: jgjncr_copy表缺少sscx字段")
            return []
        
        if 'cjrq' not in column_names:
            print("警告: jgjncr_copy表缺少cjrq字段")
            return []
        
        # 计算一年前的日期
        from datetime import datetime, timedelta
        one_year_ago = datetime.now() - timedelta(days=365)
        one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
        
        # 查询近一年内sscx字段按月份的统计
        trend_sql = """
        SELECT 
            DATE_FORMAT(cjrq, '%Y-%m') as month,
            COALESCE(sscx, '未知') as sscx_type,
            COUNT(*) as count
        FROM jgjncr_copy
        WHERE cjrq >= %s AND sscx IS NOT NULL AND TRIM(sscx) != ''
        GROUP BY DATE_FORMAT(cjrq, '%Y-%m'), sscx
        ORDER BY month, count DESC
        """
        
        trend_results = execute_query(trend_sql, (one_year_ago_str,), fetch_all=True) or []
        
        # 按月份组织数据
        monthly_data = {}
        sscx_types = set()
        
        for result in trend_results:
            if result and 'month' in result and 'sscx_type' in result and 'count' in result:
                month = result['month']
                sscx_type = result['sscx_type']
                count = result['count']
                
                sscx_types.add(sscx_type)
                
                if month not in monthly_data:
                    monthly_data[month] = {}
                monthly_data[month][sscx_type] = count
        
        # 格式化返回数据
        formatted_results = []
        sorted_months = sorted(monthly_data.keys())
        
        for month in sorted_months:
            month_data = {
                "month": month,
                "total": sum(monthly_data[month].values())
            }
            
            # 为每种sscx类型添加数据
            for sscx_type in sscx_types:
                month_data[sscx_type] = monthly_data[month].get(sscx_type, 0)
            
            formatted_results.append(month_data)
        
        # 如果没有数据，返回空数组
        if not formatted_results:
            print("警告: 近一年内没有找到有效的sscx趋势数据")
            return []
        
        return formatted_results
    except Exception as e:
        print(f"获取SSCX趋势统计出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 32. 获取当前节点详情数据
@router.post("/ncr/current-node-detail")
async def get_current_node_detail(node_info: dict):
    """
    获取当前节点详情数据
    根据前端传递的当前节点信息，返回该节点相关的所有信息和表格数据
    支持多个节点的批量查询
    """
    try:
        # 从请求体中获取节点信息
        current_nodes = node_info.get('currentNodes', [])
        
        if not current_nodes:
            return {"data": [], "total": 0, "nodeStats": []}
        
        # 检查 jgjncr_copy 表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告：jgjncr_copy 表不存在，尝试使用 gjncr 表")
            check_table_sql = "SHOW TABLES LIKE 'jgjncr'"
            table_exists = execute_query(check_table_sql)
            if not table_exists:
                print("警告：jgjncr 表也不存在")
                return {"data": [], "total": 0, "nodeStats": []}
            table_name = 'jgjncr'
        else:
            table_name = 'jgjncr_copy'
        
        # 检查必要字段是否存在
        describe_sql = f"DESCRIBE {table_name}"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print(f"警告：无法获取{table_name}表结构")
            return {"data": [], "total": 0, "nodeStats": []}
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        # 检查 dqjd 字段是否存在
        if 'dqjd' not in column_names:
            print(f"警告：{table_name}表中没有 dqjd 字段")
            return {"data": [], "total": 0, "nodeStats": []}
        
        # 构建查询条件 - 支持多节点查询
        conditions = []
        params = []
        
        for node in current_nodes:
            if node:
                conditions.append("dqjd = %s")
                params.append(node)
        
        where_clause = " OR ".join(conditions) if conditions else "1=1"
        
        # 查询数据总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
        count_result = execute_query(count_sql, tuple(params))
        total_count = count_result.get('total', 0) if count_result else 0
        
        # 查询每个节点的统计信息
        node_stats = []
        for node in current_nodes:
            node_count_sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE dqjd = %s"
            node_count_result = execute_query(node_count_sql, (node,))
            node_count = node_count_result.get('count', 0) if node_count_result else 0
            node_stats.append({
                'nodeName': node,
                'count': node_count
            })
        
        # 确定排序字段
        order_field = None
        if 'create_date' in column_names:
            order_field = 'create_date'
        elif 'create_time' in column_names:
            order_field = 'create_time'
        elif 'cjrq' in column_names:
            order_field = 'cjrq'
        elif 'process_no' in column_names:
            order_field = 'process_no'
        else:
            order_field = column_names[0] if column_names else '*'
        
        # 查询详细数据（不限制数量，返回所有匹配的记录）
        query_sql = f"""
        SELECT * FROM {table_name}
        WHERE {where_clause}
        ORDER BY {order_field} DESC
        """
        
        table_data = execute_query(query_sql, tuple(params), fetch_all=True) or []
        
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
            "data": formatted_table_data,
            "total": total_count,
            "nodeStats": node_stats
        }
    except Exception as e:
        print(f"获取当前节点详情数据出错：{e}")
        import traceback
        traceback.print_exc()
        return {"data": [], "total": 0, "nodeStats": []}

# 33. 获取 SSCX 字段近一年统计数据（前 15 名）
@router.get("/ncr/sscx-yearly-stats", response_model=List[dict])
def get_sscx_yearly_statistics():
    """获取jgjncr_copy表中sscx字段近一年数据出现次数统计（前15名）"""
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在")
            return []
        
        # 检查sscx字段是否存在
        describe_sql = "DESCRIBE jgjncr_copy"
        columns_result = execute_query(describe_sql, fetch_all=True)
        if not columns_result:
            print("警告: 无法获取jgjncr_copy表结构")
            return []
        
        column_names = [col['Field'] for col in columns_result if 'Field' in col]
        
        if 'sscx' not in column_names:
            print("警告: jgjncr_copy表缺少sscx字段")
            return []
        
        # 计算一年前的日期
        from datetime import datetime, timedelta
        one_year_ago = datetime.now() - timedelta(days=365)
        one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
        
        # 查询近一年内sscx字段的数据统计
        # 注意：这里假设表中有时间字段，如果没有则统计全部数据
        sscx_sql = """
        SELECT 
            sscx as category,
            COUNT(*) as count
        FROM jgjncr_copy
        WHERE sscx IS NOT NULL 
            AND TRIM(sscx) != ''
            AND sscx != 'nan'
            AND sscx != 'NULL'
        GROUP BY sscx
        ORDER BY count DESC
        LIMIT 15
        """
        
        # 如果表中有创建时间或更新时间字段，可以添加时间过滤
        # 检查是否有时间字段
        time_fields = ['create_time', 'created_at', 'update_time', 'updated_at', 'create_date', 'cjrq']
        time_field_found = None
        for field in time_fields:
            if field in column_names:
                time_field_found = field
                break
        
        if time_field_found:
            # 如果有时间字段，则添加近一年的时间过滤
            sscx_sql = f"""
            SELECT 
                sscx as category,
                COUNT(*) as count
            FROM jgjncr_copy
            WHERE sscx IS NOT NULL 
                AND TRIM(sscx) != ''
                AND sscx != 'nan'
                AND sscx != 'NULL'
                AND {time_field_found} >= '{one_year_ago_str}'
            GROUP BY sscx
            ORDER BY count DESC
            LIMIT 15
            """
        
        sscx_results = execute_query(sscx_sql, fetch_all=True) or []
        
        # 格式化返回数据
        formatted_results = []
        for result in sscx_results:
            if result is not None and 'category' in result and 'count' in result:
                category_name = result['category']
                count_value = result['count']
                
                # 数据清理
                if category_name and isinstance(category_name, str):
                    category_name = category_name.strip()
                    if category_name:  # 确保不是空字符串
                        formatted_results.append({
                            "name": category_name,
                            "value": count_value
                        })
        
        print(f"SSCX统计完成，返回 {len(formatted_results)} 条记录")
        return formatted_results
        
    except Exception as e:
        print(f"获取SSCX年度统计出错: {e}")
        import traceback
        traceback.print_exc()
        return []

# 26. 根据问题层级获取NCR列表(用于旭日图点击跳转)
@router.get("/ncr/problem-hierarchy-detail", response_model=dict)
async def get_ncr_by_problem_hierarchy(
    level: str,  # wtdx/wtfl/wtflxfn
    name: str,   # 层级名称
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """
    根据问题层级获取NCR列表
    - level: 层级类型 (wtdx=问题导向, wtfl=问题分类, wtflxfn=问题分类细分)
    - name: 层级名称 (如: 设计问题、尺寸偏差等)
    """
    try:
        # 检查jgjncr_copy表是否存在
        check_table_sql = "SHOW TABLES LIKE 'jgjncr_copy'"
        table_exists = execute_query(check_table_sql)
        if not table_exists:
            print("警告: jgjncr_copy表不存在,尝试使用jgjncr表")
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
        
        # 确定要查询的字段名
        field_map = {
            'wtdx': 'wtdx',      # 问题导向
            'wtfl': 'wtfl',      # 问题分类
            'wtflxfn': 'wtflxfn'   # 问题分类细分
        }
        
        query_field = field_map.get(level)
        if not query_field:
            print(f"警告: 不支持的层级类型: {level}")
            return {"data": [], "total": 0}
        
        if query_field not in column_names:
            print(f"警告: 表中没有{query_field}字段 (当前请求的层级: {level})")
            # 如果字段不存在，返回空结果但不报错
            return {"data": [], "total": 0}
        
        # 构建WHERE条件
        where_clauses = [f"{query_field} = %s"]
        params = [name]
        
        # 添加状态筛选
        if status:
            where_clauses.append("status = %s")
            params.append(status)
        
        # 添加优先级筛选
        if priority:
            where_clauses.append("priority = %s")
            params.append(priority)
        
        where_sql = " AND ".join(where_clauses)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_sql}"
        count_result = execute_query(count_sql, tuple(params), fetch_one=True)
        total_count = count_result['total'] if count_result else 0
        
        # 计算分页
        offset = (page - 1) * limit
        
        # 查询数据
        query_sql = f"""
        SELECT * FROM {table_name} 
        WHERE {where_sql}
        ORDER BY create_date DESC, id DESC
        LIMIT %s OFFSET %s
        """
        query_params = tuple(params + [limit, offset])
        ncr_data = execute_query(query_sql, query_params, fetch_all=True) or []
        
        # 格式化数据
        formatted_data = []
        for record in ncr_data:
            if record is not None:
                formatted_record = {}
                for key, value in record.items():
                    if isinstance(value, datetime):
                        formatted_record[key] = str(value)
                    elif hasattr(value, 'quantize'):
                        formatted_record[key] = float(value)
                    else:
                        formatted_record[key] = value
                formatted_data.append(formatted_record)
        
        print(f"✅ 问题层级详情查询成功: level={level}, name={name}, total={total_count}")
        
        return {
            "data": formatted_data,
            "total": total_count
        }
        
    except Exception as e:
        print(f"获取问题层级详情出错: {e}")
        import traceback
        traceback.print_exc()
        return {"data": [], "total": 0}
