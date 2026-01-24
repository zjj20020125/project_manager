import mysql.connector
from mysql.connector import Error

# 从配置文件导入数据库连接信息
import sys
sys.path.append('./project-backend/config')
from config import DB_CONFIG

def check_database_data():
    try:
        # 连接到数据库
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # 检查 project_tasks 表是否存在
            cursor.execute("SHOW TABLES LIKE 'project_tasks'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("错误: project_tasks 表不存在")
                return
            
            print("project_tasks 表存在")
            
            # 检查表结构
            cursor.execute("DESCRIBE project_tasks")
            columns = cursor.fetchall()
            print("\nproject_tasks 表结构:")
            for col in columns:
                print(f"  {col['Field']} - {col['Type']} - {col['Null']} - {col['Key']}")
            
            # 检查数据总量
            cursor.execute("SELECT COUNT(*) as total FROM project_tasks")
            total_count = cursor.fetchone()['total']
            print(f"\n总任务数: {total_count}")
            
            # 检查一些样本数据
            cursor.execute("SELECT * FROM project_tasks LIMIT 5")
            sample_data = cursor.fetchall()
            print(f"\n前5条样本数据:")
            for i, row in enumerate(sample_data):
                print(f"  样本 {i+1}: {row}")
                
            # 检查 WBS 编码的模式
            cursor.execute("SELECT DISTINCT wbs_code FROM project_tasks WHERE wbs_code IS NOT NULL LIMIT 10")
            wbs_codes = cursor.fetchall()
            print(f"\nWBS 编码样本 (最多10个):")
            for wbs in wbs_codes:
                print(f"  {wbs['wbs_code']}")
                
            # 检查任务状态
            cursor.execute("SELECT DISTINCT task_status FROM project_tasks WHERE task_status IS NOT NULL")
            statuses = cursor.fetchall()
            print(f"\n任务状态:")
            for status in statuses:
                print(f"  {status['task_status']}")
                
            # 检查各种类型任务的数量
            print(f"\n各类任务数量:")
            
            # 里程碑任务数量 (wbs_code为纯数字)
            cursor.execute("SELECT COUNT(*) as count FROM project_tasks WHERE wbs_code REGEXP '^[0-9]+$'")
            milestone_count = cursor.fetchone()['count']
            print(f"  里程碑任务数: {milestone_count}")
            
            # 子任务数量 (wbs_code包含小数点)
            cursor.execute("SELECT COUNT(*) as count FROM project_tasks WHERE wbs_code NOT REGEXP '^[0-9]+$' AND wbs_code IS NOT NULL")
            subtask_count = cursor.fetchone()['count']
            print(f"  子任务数: {subtask_count}")
            
            # 已完成任务数量
            cursor.execute("SELECT COUNT(*) as count FROM project_tasks WHERE task_status = '完成'")
            completed_count = cursor.fetchone()['count']
            print(f"  已完成任务数: {completed_count}")
            
            # 已验收任务数量 (有实际开始和结束时间)
            cursor.execute("SELECT COUNT(*) as count FROM project_tasks WHERE actual_start_date IS NOT NULL AND actual_end_date IS NOT NULL")
            accepted_count = cursor.fetchone()['count']
            print(f"  已验收任务数: {accepted_count}")

    except Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_database_data()