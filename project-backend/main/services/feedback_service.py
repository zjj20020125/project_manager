"""
客户反馈管理服务模块
"""
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db_connection


class FeedbackService:
    """客户反馈服务类"""
    
    @staticmethod
    def get_feedback_stats():
        """获取客户反馈统计数据"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 总反馈数
            cursor.execute("SELECT COUNT(*) as count FROM customer_feedback")
            total = cursor.fetchone()['count']
            
            # 各状态统计
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM customer_feedback 
                GROUP BY status
            """)
            status_list = cursor.fetchall()
            
            # 各类型统计
            cursor.execute("""
                SELECT feedback_type, COUNT(*) as count 
                FROM customer_feedback 
                GROUP BY feedback_type
            """)
            type_list = cursor.fetchall()
            
            # 优先级统计
            cursor.execute("""
                SELECT priority, COUNT(*) as count 
                FROM customer_feedback 
                GROUP BY priority
            """)
            priority_list = cursor.fetchall()
            
            # 本月新增
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM customer_feedback 
                WHERE MONTH(create_time) = MONTH(CURDATE()) 
                AND YEAR(create_time) = YEAR(CURDATE())
            """)
            month_count = cursor.fetchone()['count']
            
            return {
                'total': total,
                'status_distribution': {item['status']: item['count'] for item in status_list},
                'type_distribution': {item['feedback_type']: item['count'] for item in type_list},
                'priority_distribution': {item['priority']: item['count'] for item in priority_list},
                'new_this_month': month_count
            }
            
        except Exception as e:
            print(f"获取反馈统计失败：{e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_feedback_by_conditions(
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        priority: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ):
        """根据条件查询客户反馈列表"""
        conn = get_db_connection()
        if not conn:
            return None
        
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
            return cursor.fetchall()
            
        except Exception as e:
            print(f"查询反馈列表失败：{e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create_feedback(
        customer_name: str,
        contact_info: str,
        feedback_type: str,
        priority: str,
        title: str,
        description: str,
        project_name: Optional[str] = None,
        expected_solution: Optional[str] = None
    ):
        """创建客户反馈"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            sql = """
            INSERT INTO customer_feedback 
            (customer_name, contact_info, project_name, feedback_type, priority, 
             title, description, expected_solution, status, create_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '待处理', NOW())
            """
            
            cursor.execute(sql, (
                customer_name,
                contact_info,
                project_name,
                feedback_type,
                priority,
                title,
                description,
                expected_solution
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            print(f"创建反馈失败：{e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def update_feedback_status(feedback_id: int, status: str, handler: Optional[str] = None):
        """更新反馈状态"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            if handler:
                sql = """
                UPDATE customer_feedback 
                SET status = %s, handler = %s, update_time = NOW()
                WHERE feedback_id = %s
                """
                cursor.execute(sql, (status, handler, feedback_id))
            else:
                sql = """
                UPDATE customer_feedback 
                SET status = %s, update_time = NOW()
                WHERE feedback_id = %s
                """
                cursor.execute(sql, (status, feedback_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"更新反馈状态失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_feedback_solution(feedback_id: int, solution: str, process_record: Optional[str] = None):
        """更新反馈解决方案"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            if process_record:
                sql = """
                UPDATE customer_feedback 
                SET solution = %s, process_record = %s, status = '已解决', update_time = NOW()
                WHERE feedback_id = %s
                """
                cursor.execute(sql, (solution, process_record, feedback_id))
            else:
                sql = """
                UPDATE customer_feedback 
                SET solution = %s, status = '已解决', update_time = NOW()
                WHERE feedback_id = %s
                """
                cursor.execute(sql, (solution, feedback_id))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"更新反馈解决方案失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()


# 使用示例
if __name__ == "__main__":
    # 获取统计数据
    stats = FeedbackService.get_feedback_stats()
    if stats:
        print("=== 客户反馈统计 ===")
        print(f"总反馈数：{stats['total']}")
        print(f"本月新增：{stats['new_this_month']}")
        print(f"状态分布：{stats['status_distribution']}")
        print(f"类型分布：{stats['type_distribution']}")
        print(f"优先级分布：{stats['priority_distribution']}")
