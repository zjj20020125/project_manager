"""
客户反馈管理路由模块
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime, date
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db_connection

router = APIRouter(prefix="/v1/feedback", tags=["客户反馈管理"])


# ==================== 数据模型 ====================

class FeedbackCreate(BaseModel):
    """创建客户反馈请求模型"""
    customer_name: str
    contact_info: str
    project_name: Optional[str] = None
    feedback_type: str  # 质量投诉、技术建议、售后服务、其他
    priority: str  # 高、中、低
    title: str
    description: str
    expected_solution: Optional[str] = None
    remarks: Optional[str] = None


class FeedbackUpdate(BaseModel):
    """更新客户反馈请求模型"""
    status: Optional[str] = None
    handler: Optional[str] = None
    process_record: Optional[str] = None
    solution: Optional[str] = None
    remarks: Optional[str] = None


class FeedbackResponse(BaseModel):
    """客户反馈响应模型"""
    feedback_id: int
    customer_name: str
    contact_info: str
    project_name: Optional[str]
    feedback_type: str
    priority: str
    title: str
    description: str
    expected_solution: Optional[str]
    status: str  # 待处理、处理中、已解决、已关闭
    handler: Optional[str]
    process_record: Optional[str]
    solution: Optional[str]
    create_time: datetime
    update_time: Optional[datetime]
    remarks: Optional[str]


# ==================== API 接口 ====================

@router.get("/stats", response_model=Dict)
async def get_feedback_stats():
    """获取客户反馈统计数据"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 总反馈数
        total_sql = "SELECT COUNT(*) as count FROM customer_feedback"
        cursor.execute(total_sql)
        total = cursor.fetchone()['count']
        
        # 各状态统计
        status_sql = """
        SELECT status, COUNT(*) as count 
        FROM customer_feedback 
        GROUP BY status
        """
        cursor.execute(status_sql)
        status_list = cursor.fetchall()
        
        # 各类型统计
        type_sql = """
        SELECT feedback_type, COUNT(*) as count 
        FROM customer_feedback 
        GROUP BY feedback_type
        """
        cursor.execute(type_sql)
        type_list = cursor.fetchall()
        
        # 优先级统计
        priority_sql = """
        SELECT priority, COUNT(*) as count 
        FROM customer_feedback 
        GROUP BY priority
        """
        cursor.execute(priority_sql)
        priority_list = cursor.fetchall()
        
        # 本月新增
        month_sql = """
        SELECT COUNT(*) as count 
        FROM customer_feedback 
        WHERE MONTH(create_time) = MONTH(CURDATE()) 
        AND YEAR(create_time) = YEAR(CURDATE())
        """
        cursor.execute(month_sql)
        month_count = cursor.fetchone()['count']
        
        stats = {
            'total': total,
            'status_distribution': {item['status']: item['count'] for item in status_list},
            'type_distribution': {item['feedback_type']: item['count'] for item in type_list},
            'priority_distribution': {item['priority']: item['count'] for item in priority_list},
            'new_this_month': month_count
        }
        
        return {"success": True, "data": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.get("/list", response_model=List[FeedbackResponse])
async def get_feedback_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    feedback_type: Optional[str] = None,
    priority: Optional[str] = None,
    keyword: Optional[str] = None
):
    """获取客户反馈列表（支持分页和筛选）"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询条件
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("status = %s")
            params.append(status)
        
        if feedback_type:
            where_clauses.append("feedback_type = %s")
            params.append(feedback_type)
        
        if priority:
            where_clauses.append("priority = %s")
            params.append(priority)
        
        if keyword:
            where_clauses.append("(customer_name LIKE %s OR title LIKE %s OR project_name LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # 查询列表
        sql = f"""
        SELECT * FROM customer_feedback
        {where_sql}
        ORDER BY create_time DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(sql, params)
        feedback_list = cursor.fetchall()
        
        # 格式化日期
        for feedback in feedback_list:
            if feedback.get('create_time'):
                feedback['create_time'] = feedback['create_time'].isoformat()
            if feedback.get('update_time'):
                feedback['update_time'] = feedback['update_time'].isoformat()
        
        return feedback_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_detail(feedback_id: int):
    """获取客户反馈详情"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM customer_feedback WHERE feedback_id = %s"
        cursor.execute(sql, (feedback_id,))
        feedback = cursor.fetchone()
        
        if not feedback:
            raise HTTPException(status_code=404, detail="反馈记录不存在")
        
        # 格式化日期
        if feedback.get('create_time'):
            feedback['create_time'] = feedback['create_time'].isoformat()
        if feedback.get('update_time'):
            feedback['update_time'] = feedback['update_time'].isoformat()
        
        return feedback
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.post("/", response_model=Dict)
async def create_feedback(feedback: FeedbackCreate):
    """创建新的客户反馈"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO customer_feedback 
        (customer_name, contact_info, project_name, feedback_type, priority, 
         title, description, expected_solution, status, create_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '待处理', NOW())
        """
        
        cursor.execute(sql, (
            feedback.customer_name,
            feedback.contact_info,
            feedback.project_name,
            feedback.feedback_type,
            feedback.priority,
            feedback.title,
            feedback.description,
            feedback.expected_solution
        ))
        
        conn.commit()
        feedback_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "客户反馈创建成功",
            "feedback_id": feedback_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")
    finally:
        conn.close()


@router.put("/{feedback_id}", response_model=Dict)
async def update_feedback(feedback_id: int, feedback: FeedbackUpdate):
    """更新客户反馈"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor()
        
        # 动态构建更新字段
        update_fields = []
        values = []
        
        if feedback.status is not None:
            update_fields.append("status = %s")
            values.append(feedback.status)
        
        if feedback.handler is not None:
            update_fields.append("handler = %s")
            values.append(feedback.handler)
        
        if feedback.process_record is not None:
            update_fields.append("process_record = %s")
            values.append(feedback.process_record)
        
        if feedback.solution is not None:
            update_fields.append("solution = %s")
            values.append(feedback.solution)
        
        if feedback.remarks is not None:
            update_fields.append("remarks = %s")
            values.append(feedback.remarks)
        
        if update_fields:
            update_fields.append("update_time = NOW()")
            values.append(feedback_id)
            
            sql = f"UPDATE customer_feedback SET {', '.join(update_fields)} WHERE feedback_id = %s"
            cursor.execute(sql, values)
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="反馈记录不存在")
            
            conn.commit()
            
            return {
                "success": True,
                "message": "客户反馈更新成功"
            }
        else:
            return {
                "success": True,
                "message": "没有需要更新的字段"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败：{str(e)}")
    finally:
        conn.close()


@router.delete("/{feedback_id}", response_model=Dict)
async def delete_feedback(feedback_id: int):
    """删除客户反馈"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor()
        
        sql = "DELETE FROM customer_feedback WHERE feedback_id = %s"
        cursor.execute(sql, (feedback_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="反馈记录不存在")
        
        conn.commit()
        
        return {
            "success": True,
            "message": "客户反馈删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败：{str(e)}")
    finally:
        conn.close()



# ==================== 质量问题管理接口 ====================

@router.get("/problem/stats", response_model=Dict)
async def get_problem_stats(
    problem_type: Optional[str] = None,  # 支持多选，逗号分隔
    department: Optional[str] = None,    # 支持多选，逗号分隔
    product_type: Optional[str] = None,  # 支持多选，逗号分隔
    month: Optional[str] = None,
    week: Optional[str] = None,  # 新增：周数筛选，格式如 "2026年第5周"
    market_category: Optional[str] = None,  # 新增：市场分类筛选
    occurrence_unit: Optional[str] = None,  # 新增：发生单位筛选
    vehicle_model: Optional[str] = None,  # 新增：车型筛选
    repair_type: Optional[str] = None,  # 新增：新造/检修类型筛选（other1字段）
    problem_category: Optional[str] = None,  # 新增：问题分类筛选
    problem_category_1: Optional[str] = None,  # 新增：问题分类1筛选
    supplement_category_2: Optional[str] = None,  # 新增：补充分类2筛选
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
):
    """获取质量问题统计数据（支持筛选）"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 构建筛选条件
        where_clauses = []
        params = []
        
        # 处理多选字段
        if problem_type:
            types = problem_type.split(',')
            if len(types) > 1:
                where_clauses.append(f"problem_nature IN ({','.join(['%s'] * len(types))})")
                params.extend(types)
            else:
                where_clauses.append("problem_nature = %s")
                params.append(types[0])
        
        if department:
            depts = department.split(',')
            if len(depts) > 1:
                where_clauses.append(f"responsible_team IN ({','.join(['%s'] * len(depts))})")
                params.extend(depts)
            else:
                where_clauses.append("responsible_team = %s")
                params.append(depts[0])
        
        if product_type:
            types = product_type.split(',')
            if len(types) > 1:
                where_clauses.append(f"vehicle_model IN ({','.join(['%s'] * len(types))})")
                params.extend(types)
            else:
                where_clauses.append("vehicle_model = %s")
                params.append(types[0])
        
        # 处理月份多选（使用 month 字段）
        if month:
            months = month.split(',')
            if len(months) > 1:
                # 多选：使用 IN 查询
                in_placeholders = ','.join(['%s'] * len(months))
                where_clauses.append(f"month IN ({in_placeholders})")
                params.extend(months)
            else:
                # 单选
                where_clauses.append("month = %s")
                params.append(months[0])
        
        # 处理周数筛选（从 occurrence_date 计算）
        if week:
            weeks = week.split(',')
            if len(weeks) > 1:
                # 多选：解析每个周数并构建 OR 条件
                week_conditions = []
                for w in weeks:
                    # 解析 "2026年第5周" 格式
                    import re
                    match = re.match(r'(\d{4})年.*?(\d+)周', w)
                    if match:
                        year, week_num = match.groups()
                        week_conditions.append(f"(YEAR(occurrence_date) = %s AND WEEK(occurrence_date, 1) = %s)")
                        params.extend([year, week_num])
                if week_conditions:
                    where_clauses.append("(" + " OR ".join(week_conditions) + ")")
            else:
                # 单选
                import re
                match = re.match(r'(\d{4})年.*?(\d+)周', weeks[0])
                if match:
                    year, week_num = match.groups()
                    where_clauses.append("YEAR(occurrence_date) = %s AND WEEK(occurrence_date, 1) = %s")
                    params.extend([year, week_num])
        
        # 处理市场分类筛选
        if market_category:
            categories = market_category.split(',')
            if len(categories) > 1:
                in_placeholders = ','.join(['%s'] * len(categories))
                where_clauses.append(f"market_category IN ({in_placeholders})")
                params.extend(categories)
            else:
                where_clauses.append("market_category = %s")
                params.append(categories[0])
        
        # 处理发生单位筛选
        if occurrence_unit:
            units = occurrence_unit.split(',')
            if len(units) > 1:
                in_placeholders = ','.join(['%s'] * len(units))
                where_clauses.append(f"occurrence_unit IN ({in_placeholders})")
                params.extend(units)
            else:
                where_clauses.append("occurrence_unit = %s")
                params.append(units[0])
        
        # 处理车型筛选
        if vehicle_model:
            models = vehicle_model.split(',')
            if len(models) > 1:
                in_placeholders = ','.join(['%s'] * len(models))
                where_clauses.append(f"vehicle_model IN ({in_placeholders})")
                params.extend(models)
            else:
                where_clauses.append("vehicle_model = %s")
                params.append(models[0])
        
        # 处理新造/检修类型筛选（production_repair_type字段）
        if repair_type:
            types = repair_type.split(',')
            if len(types) > 1:
                in_placeholders = ','.join(['%s'] * len(types))
                where_clauses.append(f"production_repair_type IN ({in_placeholders})")
                params.extend(types)
            else:
                where_clauses.append("production_repair_type = %s")
                params.append(types[0])
        
        # 处理问题分类筛选
        if problem_category:
            categories = problem_category.split(',')
            if len(categories) > 1:
                in_placeholders = ','.join(['%s'] * len(categories))
                where_clauses.append(f"problem_category IN ({in_placeholders})")
                params.extend(categories)
            else:
                where_clauses.append("problem_category = %s")
                params.append(categories[0])
        
        # 处理问题分类1筛选
        if problem_category_1:
            categories = problem_category_1.split(',')
            if len(categories) > 1:
                in_placeholders = ','.join(['%s'] * len(categories))
                where_clauses.append(f"problem_category_1 IN ({in_placeholders})")
                params.extend(categories)
            else:
                where_clauses.append("problem_category_1 = %s")
                params.append(categories[0])
        
        # 处理补充分类2筛选
        if supplement_category_2:
            categories = supplement_category_2.split(',')
            if len(categories) > 1:
                in_placeholders = ','.join(['%s'] * len(categories))
                where_clauses.append(f"supplement_category_2 IN ({in_placeholders})")
                params.extend(categories)
            else:
                where_clauses.append("supplement_category_2 = %s")
                params.append(categories[0])
        
        if min_amount is not None:
            where_clauses.append("assessment_amount >= %s")
            params.append(min_amount)
        
        if max_amount is not None:
            where_clauses.append("assessment_amount <= %s")
            params.append(max_amount)
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # 问题总数
        total_sql = f"SELECT COUNT(*) as count FROM customer_quality {where_sql}"
        cursor.execute(total_sql, params)
        total = cursor.fetchone()['count']
        
        # 平均考核金额
        avg_sql = f"SELECT COALESCE(AVG(assessment_amount), 0) as avg_amount FROM customer_quality {where_sql}"
        cursor.execute(avg_sql, params)
        avg_amount = round(cursor.fetchone()['avg_amount'], 2)
        
        # 已关闭问题数
        if where_sql:
            closed_sql = f"SELECT COUNT(*) as count FROM customer_quality {where_sql} AND is_closed = '是'"
            cursor.execute(closed_sql, params)
        else:
            closed_sql = "SELECT COUNT(*) as count FROM customer_quality WHERE is_closed = '是'"
            cursor.execute(closed_sql)
        closed = cursor.fetchone()['count']
        
        # 问题定性分布（按 problem_nature 字段分组）
        type_sql = f"""
        SELECT problem_nature, COUNT(*) as count 
        FROM customer_quality 
        {where_sql}
        GROUP BY problem_nature
        ORDER BY count DESC
        """
        cursor.execute(type_sql, params)
        type_list = cursor.fetchall()
        
        # 责任主体统计（整合 responsible_team、supplier、workshop 字段）
        responsible_sql = f"""
        SELECT 
            COALESCE(NULLIF(responsible_team, ''), NULLIF(supplier, ''), NULLIF(workshop, '其他')) as subject,
            COUNT(*) as count
        FROM customer_quality
        {where_sql}
        GROUP BY subject
        ORDER BY count DESC
        """
        cursor.execute(responsible_sql, params)
        responsible_list = cursor.fetchall()
        
        # 产品类型统计（按 product_name 提取关键词）
        product_sql = f"""
        SELECT 
            CASE
                WHEN product_name LIKE '%油箱%' THEN '油箱'
                WHEN product_name LIKE '%箱盖%' THEN '箱盖'
                WHEN product_name LIKE '%垫脚%' THEN '垫脚'
                WHEN product_name LIKE '%导油管%' THEN '导油管'
                ELSE '其他'
            END as product_category,
            COUNT(*) as count
        FROM customer_quality
        {where_sql}
        GROUP BY product_category
        ORDER BY count DESC
        """
        cursor.execute(product_sql, params)
        product_list = cursor.fetchall()
        
        # 问题分类统计（从 problem_category 和 corrective_measures 提取关键词）
        category_sql = f"""
        SELECT 
            CASE
                WHEN problem_category LIKE '%外观%' THEN '外观问题'
                WHEN problem_category LIKE '%尺寸%' THEN '尺寸超差'
                WHEN corrective_measures LIKE '%焊接%' THEN '焊接工序'
                WHEN corrective_measures LIKE '%油漆%' THEN '油漆工序'
                ELSE '其他'
            END as issue_category,
            COUNT(*) as count
        FROM customer_quality
        {where_sql}
        GROUP BY issue_category
        ORDER BY count DESC
        """
        cursor.execute(category_sql, params)
        category_list = cursor.fetchall()
        
        # 问题分类 1 统计（新增）
        category_1_sql = f"""
        SELECT problem_category_1, COUNT(*) as count 
        FROM customer_quality 
        {where_sql}
        GROUP BY problem_category_1
        ORDER BY count DESC
        """
        cursor.execute(category_1_sql, params)
        category_1_list = cursor.fetchall()
        
        # 补充分类 2 统计（新增）
        supplement_2_sql = f"""
        SELECT supplement_category_2, COUNT(*) as count 
        FROM customer_quality 
        {where_sql}
        GROUP BY supplement_category_2
        ORDER BY count DESC
        """
        cursor.execute(supplement_2_sql, params)
        supplement_2_list = cursor.fetchall()
        
        # 关键指标计算
        kpi_sql = f"""
        SELECT 
            SUM(CASE WHEN is_closed = '是' THEN 1 ELSE 0 END) as closed_count,
            COALESCE(SUM(assessment_amount), 0) as total_amount
        FROM customer_quality
        {where_sql}
        """
        if params:
            cursor.execute(kpi_sql, params)
        else:
            cursor.execute(kpi_sql)
        kpi_result = cursor.fetchone()
        
        stats = {
            'total': total,
            'average_amount': avg_amount,
            'closed': closed,
            'type_distribution': {item['problem_nature']: item['count'] for item in type_list},  # 问题定性统计
            'responsible_subject_distribution': {item['subject']: item['count'] for item in responsible_list},  # 责任主体统计
            'product_category_distribution': {item['product_category']: item['count'] for item in product_list},  # 产品类型统计
            'issue_category_distribution': {item['issue_category']: item['count'] for item in category_list},  # 问题分类统计
            'category_1_distribution': {item['problem_category_1']: item['count'] for item in category_1_list if item['problem_category_1']},  # 问题分类 1 统计
            'supplement_category_2_distribution': {item['supplement_category_2']: item['count'] for item in supplement_2_list if item['supplement_category_2']},  # 补充分类 2 统计
            'kpi_metrics': {
                'closed_count': kpi_result['closed_count'] or 0,  # 已关闭问题数
                'total_amount': kpi_result['total_amount'] or 0  # 累计考核金额
            }
        }
        
        return {"success": True, "data": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.get("/problem/list", response_model=Dict)
async def get_problem_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    problem_type: Optional[str] = None,  # 支持多选，逗号分隔
    department: Optional[str] = None,    # 支持多选，逗号分隔
    product_type: Optional[str] = None,  # 支持多选，逗号分隔
    month: Optional[str] = None,
    week: Optional[str] = None,  # 新增：周数筛选
    market_category: Optional[str] = None,  # 新增：市场分类筛选
    occurrence_unit: Optional[str] = None,  # 新增：发生单位筛选
    vehicle_model: Optional[str] = None,  # 新增：车型筛选
    repair_type: Optional[str] = None,  # 新增：新造/检修类型筛选
    problem_category: Optional[str] = None,  # 新增：问题分类筛选
    problem_category_1: Optional[str] = None,  # 新增：问题分类1筛选
    supplement_category_2: Optional[str] = None,  # 新增：补充分类2筛选
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None  # 新增搜索参数
):
    """获取质量问题列表（支持分页、筛选和搜索）"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 构建筛选条件
        where_clauses = []
        params = []
        
        # 处理多选字段
        if problem_type:
            types = problem_type.split(',')
            if len(types) > 1:
                where_clauses.append(f"problem_nature IN ({','.join(['%s'] * len(types))})")
                params.extend(types)
            else:
                where_clauses.append("problem_nature = %s")
                params.append(types[0])
        
        if department:
            depts = department.split(',')
            if len(depts) > 1:
                where_clauses.append(f"responsible_team IN ({','.join(['%s'] * len(depts))})")
                params.extend(depts)
            else:
                where_clauses.append("responsible_team = %s")
                params.append(depts[0])
        
        if product_type:
            types = product_type.split(',')
            if len(types) > 1:
                where_clauses.append(f"vehicle_model IN ({','.join(['%s'] * len(types))})")
                params.extend(types)
            else:
                where_clauses.append("vehicle_model = %s")
                params.append(types[0])
        
        # 处理月份多选（使用 month 字段）
        if month:
            months = month.split(',')
            if len(months) > 1:
                # 多选：使用 IN 查询
                in_placeholders = ','.join(['%s'] * len(months))
                where_clauses.append(f"month IN ({in_placeholders})")
                params.extend(months)
            else:
                # 单选
                where_clauses.append("month = %s")
                params.append(months[0])
        
        # 处理周数筛选（从 occurrence_date 计算）
        if week:
            weeks = week.split(',')
            if len(weeks) > 1:
                # 多选：解析每个周数并构建 OR 条件
                week_conditions = []
                for w in weeks:
                    # 解析 "2026年第5周" 格式
                    import re
                    match = re.match(r'(\d{4})年.*?(\d+)周', w)
                    if match:
                        year, week_num = match.groups()
                        week_conditions.append(f"(YEAR(occurrence_date) = %s AND WEEK(occurrence_date, 1) = %s)")
                        params.extend([year, week_num])
                if week_conditions:
                    where_clauses.append("(" + " OR ".join(week_conditions) + ")")
            else:
                # 单选
                import re
                match = re.match(r'(\d{4})年.*?(\d+)周', weeks[0])
                if match:
                    year, week_num = match.groups()
                    where_clauses.append("YEAR(occurrence_date) = %s AND WEEK(occurrence_date, 1) = %s")
                    params.extend([year, week_num])
        
        if min_amount is not None:
            where_clauses.append("assessment_amount >= %s")
            params.append(min_amount)
        
        if max_amount is not None:
            where_clauses.append("assessment_amount <= %s")
            params.append(max_amount)
        
        # 添加搜索条件
        if search and search.strip():
            where_clauses.append("(product_name LIKE %s OR problem_description LIKE %s OR responsible_team LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM customer_quality {where_sql}"
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()['total']
        
        # 查询列表 - 返回所有筛选条件对应的字段
        sql = f"""
        SELECT 
            id as problem_id,
            CONCAT(market_category, '-', occurrence_unit) as customer_name,
            product_name,
            problem_nature as problem_type,
            responsible_team as department,
            problem_description as problem_desc,
            assessment_amount,
            DATE(occurrence_date) as occur_date,
            created_time as discovery_date,
            problem_category as severity,
            measure_implementation as priority,
            is_closed as status,
            responsible_person as handler,
            corrective_measures as expected_solution,
            remark as remarks,
            created_time as create_time,
            -- 新增：返回12个筛选条件对应的原始字段
            market_category,
            occurrence_unit,
            vehicle_model,
            other1 as production_repair_type,
            problem_category,
            problem_category_1,
            supplement_category_2,
            product_category as product_type,
            month,
            week_number as week
        FROM customer_quality
        {where_sql}
        ORDER BY occurrence_date DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, (page - 1) * limit])
        
        cursor.execute(sql, params)
        problem_list = cursor.fetchall()
        
        # 格式化日期
        for problem in problem_list:
            if problem.get('occur_date') and isinstance(problem['occur_date'], (date, datetime)):
                problem['occur_date'] = problem['occur_date'].isoformat() if hasattr(problem['occur_date'], 'isoformat') else str(problem['occur_date'])
            if problem.get('discovery_date') and isinstance(problem['discovery_date'], datetime):
                problem['discovery_date'] = problem['discovery_date'].isoformat()
            if problem.get('create_time') and isinstance(problem['create_time'], datetime):
                problem['create_time'] = problem['create_time'].isoformat()
        
        return {
            "list": problem_list,
            "total": total_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.get("/problem/detail/{problem_id}", response_model=Dict)
async def get_problem_detail(problem_id: int):
    """获取质量问题详情"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        sql = """
        SELECT 
            id as problem_id,
            CONCAT(market_category, '-', occurrence_unit) as customer_name,
            occurrence_unit as company_name,
            product_name,
            '' as project_name,
            problem_nature as problem_type,
            problem_description as problem_desc,
            DATE(occurrence_date) as occur_date,
            created_time as discovery_date,
            problem_category as severity,
            measure_implementation as priority,
            assessment_amount,
            is_closed as status,
            responsible_person as handler,
            corrective_measures as solution,
            remark as remarks,
            created_time as create_time,
            updated_time as update_time
        FROM customer_quality
        WHERE id = %s
        """
        cursor.execute(sql, (problem_id,))
        problem = cursor.fetchone()
        
        if not problem:
            raise HTTPException(status_code=404, detail="问题记录不存在")
        
        # 格式化日期
        if problem.get('occur_date') and isinstance(problem['occur_date'], (date, datetime)):
            problem['occur_date'] = problem['occur_date'].isoformat() if hasattr(problem['occur_date'], 'isoformat') else str(problem['occur_date'])
        if problem.get('discovery_date') and isinstance(problem['discovery_date'], datetime):
            problem['discovery_date'] = problem['discovery_date'].isoformat()
        if problem.get('create_time') and isinstance(problem['create_time'], datetime):
            problem['create_time'] = problem['create_time'].isoformat()
        if problem.get('update_time') and isinstance(problem['update_time'], datetime):
            problem['update_time'] = problem['update_time'].isoformat()
        
        return problem
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.delete("/problem/batch-delete", response_model=Dict)
async def batch_delete_problems(delete_request: Dict):
    """批量删除质量问题记录"""
    ids = delete_request.get('ids', [])
    
    if not ids or not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="请提供要删除的 ID 列表")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor()
        
        # 构建动态 SQL，使用参数化查询防止 SQL 注入
        placeholders = ','.join(['%s'] * len(ids))
        sql = f"DELETE FROM customer_quality WHERE id IN ({placeholders})"
        
        cursor.execute(sql, ids)
        deleted_count = cursor.rowcount
        
        conn.commit()
        
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="未找到要删除的记录")
        
        return {
            "success": True,
            "message": f"成功删除 {deleted_count} 条记录",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除失败：{str(e)}")
    finally:
        conn.close()


@router.post("/problem/", response_model=Dict)
async def create_problem(problem_data: Dict):
    """创建新的质量问题记录"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor()
        
        # 构建 INSERT SQL
        sql = """
        INSERT INTO customer_quality (
            serial_number, oa_number, month, market_category, occurrence_date,
            occurrence_unit, vehicle_model, vehicle_number, product_name,
            drawing_number, product_quantity, product_category, problem_description,
            problem_category_1, supplement_category_2, problem_category,
            problem_nature, cause_analysis, corrective_measures,
            measure_implementation, assessment_form, assessment_amount,
            workshop, quality_engineer, inspector, responsible_team,
            supplier, responsible_person, qrcode_import_status, is_closed,
            closing_date, remark, other1, other2,
            created_time, updated_time
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, NOW(), NOW()
        )
        """
        
        # 准备数据，处理日期格式
        occur_date = problem_data.get('occur_date')
        if occur_date and isinstance(occur_date, str):
            from datetime import datetime
            try:
                occur_date = datetime.strptime(occur_date, '%Y-%m-%d')
            except ValueError:
                occur_date = None
        
        closing_date = problem_data.get('closing_date')
        if closing_date and isinstance(closing_date, str):
            from datetime import datetime
            try:
                closing_date = datetime.strptime(closing_date, '%Y-%m-%d')
            except ValueError:
                closing_date = None
        
        # 提取所有字段值
        values = (
            problem_data.get('serial_number', 0),  # serial_number
            problem_data.get('oa_number', ''),  # oa_number
            problem_data.get('month', ''),  # month
            problem_data.get('market_category', '国内'),  # market_category
            occur_date,  # occurrence_date
            problem_data.get('occurrence_unit', '') or problem_data.get('customer_name', ''),  # occurrence_unit
            problem_data.get('vehicle_model', ''),  # vehicle_model
            problem_data.get('vehicle_number', ''),  # vehicle_number
            problem_data.get('product_name', ''),  # product_name
            problem_data.get('drawing_number', ''),  # drawing_number
            problem_data.get('product_quantity', 0),  # product_quantity
            problem_data.get('product_category', '') or problem_data.get('product_type', ''),  # product_category
            problem_data.get('problem_desc', '') or problem_data.get('problem_description', ''),  # problem_description
            problem_data.get('problem_category_1', ''),  # problem_category_1
            problem_data.get('supplement_category_2', ''),  # supplement_category_2
            problem_data.get('problem_category', '') or problem_data.get('severity', ''),  # problem_category
            problem_data.get('problem_nature', '') or problem_data.get('problem_type', ''),  # problem_nature
            problem_data.get('cause_analysis', ''),  # cause_analysis
            problem_data.get('corrective_measures', '') or problem_data.get('solution', ''),  # corrective_measures
            problem_data.get('measure_implementation', '') or problem_data.get('priority', ''),  # measure_implementation
            problem_data.get('assessment_form', ''),  # assessment_form
            int(problem_data.get('assessment_amount', 0) or 0),  # assessment_amount
            problem_data.get('workshop', ''),  # workshop
            problem_data.get('quality_engineer', ''),  # quality_engineer
            problem_data.get('inspector', ''),  # inspector
            problem_data.get('responsible_team', '') or problem_data.get('department', ''),  # responsible_team
            problem_data.get('supplier', ''),  # supplier
            problem_data.get('responsible_person', '') or problem_data.get('handler', ''),  # responsible_person
            problem_data.get('qrcode_import_status', ''),  # qrcode_import_status
            problem_data.get('is_closed', '') or (problem_data.get('status', '') == '已关闭' and '是' or '否'),  # is_closed
            closing_date,  # closing_date
            problem_data.get('remark', '') or problem_data.get('remarks', ''),  # remark
            problem_data.get('other1', ''),  # other1
            problem_data.get('other2', '')  # other2
        )
        
        cursor.execute(sql, values)
        conn.commit()
        problem_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "质量问题创建成功",
            "problem_id": problem_id
        }
        
    except Exception as e:
        conn.rollback()
        print(f"创建质量问题失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")
    finally:
        conn.close()


@router.get("/problem/filters", response_model=Dict)
async def get_problem_filters():
    """获取质量问题筛选条件选项（从 customer_quality 表提取）"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有月份（去重）- 使用 month 字段
        month_sql = """
        SELECT DISTINCT month
        FROM customer_quality
        WHERE month IS NOT NULL AND month != ''
        ORDER BY month DESC
        """
        cursor.execute(month_sql)
        months = [item['month'] for item in cursor.fetchall()]
        
        # 获取所有车型（去重）- 使用 vehicle_model 字段
        vehicle_model_sql = """
        SELECT DISTINCT vehicle_model as product_type
        FROM customer_quality
        WHERE vehicle_model IS NOT NULL AND vehicle_model != ''
        ORDER BY vehicle_model
        """
        cursor.execute(vehicle_model_sql)
        product_types = [item['product_type'] for item in cursor.fetchall()]
        
        # 获取所有新责任班组（去重）- 使用 responsible_team 字段
        responsible_team_sql = """
        SELECT DISTINCT responsible_team as new_responsible_team
        FROM customer_quality
        WHERE responsible_team IS NOT NULL AND responsible_team != ''
        ORDER BY responsible_team
        """
        cursor.execute(responsible_team_sql)
        new_responsible_teams = [item['new_responsible_team'] for item in cursor.fetchall()]
        
        # 获取所有问题定性（去重）- 使用 problem_nature 字段
        problem_nature_sql = """
        SELECT DISTINCT problem_nature
        FROM customer_quality
        WHERE problem_nature IS NOT NULL AND problem_nature != ''
        ORDER BY problem_nature
        """
        cursor.execute(problem_nature_sql)
        problem_natures = [item['problem_nature'] for item in cursor.fetchall()]
        
        # 获取所有周数（从 occurrence_date 计算）
        week_sql = """
        SELECT DISTINCT 
            CONCAT(YEAR(occurrence_date), '年第', WEEK(occurrence_date, 1), '周') as week_label
        FROM customer_quality
        WHERE occurrence_date IS NOT NULL
        ORDER BY occurrence_date DESC
        """
        cursor.execute(week_sql)
        weeks = [item['week_label'] for item in cursor.fetchall()]
        
        # 获取所有市场分类（去重）
        market_category_sql = """
        SELECT DISTINCT market_category
        FROM customer_quality
        WHERE market_category IS NOT NULL AND market_category != ''
        ORDER BY market_category
        """
        cursor.execute(market_category_sql)
        market_categories = [item['market_category'] for item in cursor.fetchall()]
        
        # 获取所有发生单位（去重）
        occurrence_unit_sql = """
        SELECT DISTINCT occurrence_unit
        FROM customer_quality
        WHERE occurrence_unit IS NOT NULL AND occurrence_unit != ''
        ORDER BY occurrence_unit
        """
        cursor.execute(occurrence_unit_sql)
        occurrence_units = [item['occurrence_unit'] for item in cursor.fetchall()]
        
        # 获取所有车型（去重）
        vehicle_model_filter_sql = """
        SELECT DISTINCT vehicle_model
        FROM customer_quality
        WHERE vehicle_model IS NOT NULL AND vehicle_model != ''
        ORDER BY vehicle_model
        """
        cursor.execute(vehicle_model_filter_sql)
        vehicle_models = [item['vehicle_model'] for item in cursor.fetchall()]
        
        # 获取所有新造/检修类型（production_repair_type字段，去重）
        repair_type_sql = """
        SELECT DISTINCT production_repair_type as repair_type
        FROM customer_quality
        WHERE production_repair_type IS NOT NULL AND production_repair_type != ''
        ORDER BY production_repair_type
        """
        cursor.execute(repair_type_sql)
        repair_types = [item['repair_type'] for item in cursor.fetchall()]
        
        # 获取所有问题分类（去重）
        problem_category_sql = """
        SELECT DISTINCT problem_category
        FROM customer_quality
        WHERE problem_category IS NOT NULL AND problem_category != ''
        ORDER BY problem_category
        """
        cursor.execute(problem_category_sql)
        problem_categories = [item['problem_category'] for item in cursor.fetchall()]
        
        # 获取所有问题分类1（去重）
        problem_category_1_sql = """
        SELECT DISTINCT problem_category_1
        FROM customer_quality
        WHERE problem_category_1 IS NOT NULL AND problem_category_1 != ''
        ORDER BY problem_category_1
        """
        cursor.execute(problem_category_1_sql)
        problem_category_1_list = [item['problem_category_1'] for item in cursor.fetchall()]
        
        # 获取所有补充分类2（去重）
        supplement_category_2_sql = """
        SELECT DISTINCT supplement_category_2
        FROM customer_quality
        WHERE supplement_category_2 IS NOT NULL AND supplement_category_2 != ''
        ORDER BY supplement_category_2
        """
        cursor.execute(supplement_category_2_sql)
        supplement_category_2_list = [item['supplement_category_2'] for item in cursor.fetchall()]
        
        filters = {
            'months': months,
            'weeks': weeks,  # 周数选项
            'product_types': product_types,
            'new_responsible_teams': new_responsible_teams,
            'problem_natures': problem_natures,  # 问题定性选项
            'market_categories': market_categories,  # 市场分类选项
            'occurrence_units': occurrence_units,  # 发生单位选项
            'vehicle_models': vehicle_models,  # 车型选项
            'repair_types': repair_types,  # 新造/检修类型选项
            'problem_categories': problem_categories,  # 问题分类选项
            'problem_category_1_list': problem_category_1_list,  # 问题分类1选项
            'supplement_category_2_list': supplement_category_2_list  # 补充分类2选项
        }
        
        return {"success": True, "data": filters}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        conn.close()


@router.post("/import-quality", response_model=Dict)
async def import_customer_quality(
    file: UploadFile = File(..., description="Excel 文件"),
    overwrite: bool = Form(False, description="是否覆盖现有数据")
):
    """批量导入客户质量反馈数据（从 Excel 文件）- 使用 data.py 脚本"""
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xls', '.xlsx')):
            raise HTTPException(status_code=400, detail="仅支持 Excel 文件格式（.xls 或 .xlsx）")
        
        # 保存上传的文件到临时目录
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"quality_import_{file.filename}")
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 调用 data.py 的导入逻辑
        # 直接使用绝对路径，避免路径计算错误
        kehu_dir = r"D:\desktop\项目管理\project manage\project-dashboard\src\views\kehu"
        if kehu_dir not in sys.path:
            sys.path.insert(0, kehu_dir)
        
        # 直接导入函数，避免模块命名冲突
        import importlib.util
        spec = importlib.util.spec_from_file_location("data_module", os.path.join(kehu_dir, "data.py"))
        data_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(data_module)
        
        read_excel_data = data_module.read_excel_data
        batch_import_to_db = data_module.batch_import_to_db
        init_db = data_module.init_db
        CustomerQualityIssue = data_module.CustomerQualityIssue
        
        # 读取 Excel 数据
        print(f"开始读取 Excel 文件：{temp_file_path}")
        
        # 临时修改 EXCEL_CONFIG 的文件路径
        original_file_path = data_module.EXCEL_CONFIG["file_path"]
        data_module.EXCEL_CONFIG["file_path"] = temp_file_path
        
        # 读取数据（使用动态加载的模块中的函数，直接传入文件路径）
        df = data_module.read_excel_data(temp_file_path)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=400, detail="无法读取 Excel 文件数据或数据为空")
        
        # 检查是否已有数据
        engine, session = init_db()
        try:
            existing_count = session.query(CustomerQualityIssue).count()
            
            if existing_count > 0 and not overwrite:
                # 清理临时文件
                try:
                    os.remove(temp_file_path)
                except:
                    pass
                return {
                    "success": False,
                    "message": f"表中已有 {existing_count} 条数据，如需覆盖请勾选'清除已有数据后导入'选项",
                    "existing_count": existing_count
                }
            elif existing_count > 0 and overwrite:
                # 删除所有现有数据
                session.query(CustomerQualityIssue).delete()
                session.commit()
                print(f"已清空 {existing_count} 条旧数据")
        finally:
            session.close()

        # 重新初始化会话进行导入
        engine, session = init_db()
        
        try:
            # 批量导入数据
            batch_import_to_db(session, df)
            imported_count = len(df)
            
            # 清理临时文件
            try:
                os.remove(temp_file_path)
            except:
                pass
            
            return {
                "success": True,
                "message": "数据导入成功",
                "imported_count": imported_count
            }
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"数据导入失败：{str(e)}")
        finally:
            session.close()
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误：{e}")
        print(f"错误类型：{type(e).__name__}")
        import traceback
        print("完整堆栈跟踪:")
        traceback.print_exc()
        print()
        raise HTTPException(status_code=500, detail=f"导入失败：{str(e)}")
