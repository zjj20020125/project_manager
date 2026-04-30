"""
定时刷新任务状态
定期检查并更新所有项目的任务状态
"""

from datetime import datetime, timedelta
import schedule
import time
import threading
from database.database import execute_query, get_db_connection
from main.common_utils import determine_task_status_import

class TaskStatusRefresher:
    """任务状态刷新器"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self, interval_minutes=5):
        """启动定时刷新任务
        
        Args:
            interval_minutes: 刷新间隔 (分钟),默认 5 分钟
        """
        if self.running:
            print("⚠️ 任务状态刷新已在运行")
            return
        
        self.running = True
        
        # 安排定时任务
        schedule.every(interval_minutes).minutes.do(self.refresh_all_tasks_status)
        
        # 在后台线程中运行
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print(f"✅ 任务状态定时刷新已启动，每 {interval_minutes} 分钟执行一次")
    
    def stop(self):
        """停止定时刷新"""
        self.running = False
        schedule.clear()
        print("⏹️ 任务状态定时刷新已停止")
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def refresh_all_tasks_status(self):
        """刷新所有任务的状态"""
        try:
            print(f"\n🔄 [{datetime.now()}] 开始刷新所有任务状态...")
            
            connection = get_db_connection()
            if not connection:
                print("❌ 无法获取数据库连接")
                return
            
            cursor = connection.cursor(dictionary=True)
            
            # 查询所有子任务
            select_sql = """
            SELECT task_id, planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, task_status
            FROM project_tasks
            """
            cursor.execute(select_sql)
            tasks = cursor.fetchall()
            
            updated_count = 0
            for task in tasks:
                # 计算新的状态
                new_status = determine_task_status_import(
                    task['planned_start_date'],
                    task['planned_end_date'],
                    task['actual_start_date'],
                    task['actual_end_date'],
                    0  # lag_days
                )
                
                # 如果状态发生变化，更新数据库
                if new_status != task['task_status']:
                    update_sql = """
                    UPDATE project_tasks 
                    SET task_status = %s 
                    WHERE task_id = %s
                    """
                    cursor.execute(update_sql, (new_status, task['task_id']))
                    updated_count += 1
                    
                    print(f"  ✓ 任务 ID={task['task_id']}: {task['task_status']} → {new_status}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"✅ 刷新完成！更新了 {updated_count}/{len(tasks)} 个任务的状态")
            
        except Exception as e:
            print(f"❌ 刷新任务状态时出错：{e}")
            import traceback
            traceback.print_exc()
    
    def refresh_single_task(self, task_id):
        """刷新单个任务的状态
        
        Args:
            task_id: 任务 ID
        """
        try:
            connection = get_db_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            
            # 查询任务信息
            select_sql = """
            SELECT planned_start_date, planned_end_date, 
                   actual_start_date, actual_end_date, task_status
            FROM project_tasks 
            WHERE task_id = %s
            """
            cursor.execute(select_sql, (task_id,))
            task = cursor.fetchone()
            
            if not task:
                cursor.close()
                connection.close()
                return None
            
            # 计算新的状态
            new_status = determine_task_status_import(
                task['planned_start_date'],
                task['planned_end_date'],
                task['actual_start_date'],
                task['actual_end_date'],
                0
            )
            
            # 如果状态发生变化，更新数据库
            if new_status != task['task_status']:
                update_sql = """
                UPDATE project_tasks 
                SET task_status = %s 
                WHERE task_id = %s
                """
                cursor.execute(update_sql, (new_status, task_id))
                connection.commit()
                print(f"✓ 任务 ID={task_id}: {task['task_status']} → {new_status}")
            
            cursor.close()
            connection.close()
            
            return new_status
            
        except Exception as e:
            print(f"❌ 刷新单个任务状态时出错：{e}")
            return None


# 创建全局实例
task_status_refresher = TaskStatusRefresher()


def start_auto_refresh():
    """启动自动刷新 (在应用启动时调用)"""
    # 每 5 分钟刷新一次
    task_status_refresher.start(interval_minutes=5)


def stop_auto_refresh():
    """停止自动刷新 (在应用关闭时调用)"""
    task_status_refresher.stop()


def get_refresher_instance():
    """获取刷新器实例（用于 API 调用）"""
    return task_status_refresher
