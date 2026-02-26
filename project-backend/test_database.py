import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import execute_query

def test_database_connection():
    print("=== 测试数据库连接 ===")
    
    # 测试基本连接
    try:
        result = execute_query("SELECT 1 as test")
        print(f"基础连接测试: {'成功' if result else '失败'}")
        if result:
            print(f"测试结果: {result}")
    except Exception as e:
        print(f"基础连接失败: {e}")
        return False
    
    # 检查数据库
    try:
        result = execute_query("SELECT DATABASE() as current_db")
        print(f"当前数据库: {result['current_db'] if result else '未知'}")
    except Exception as e:
        print(f"获取当前数据库失败: {e}")
    
    # 检查project_tasks表
    print("\n=== 检查project_tasks表 ===")
    try:
        table_check = execute_query("SHOW TABLES LIKE 'project_tasks'")
        print(f"project_tasks表存在: {bool(table_check)}")
        
        if table_check:
            # 查看表结构
            describe_result = execute_query("DESCRIBE project_tasks", fetch_all=True)
            print("表结构:")
            for col in describe_result:
                print(f"  {col['Field']}: {col['Type']}")
            
            # 查看数据量
            count_result = execute_query("SELECT COUNT(*) as count FROM project_tasks")
            print(f"数据总量: {count_result['count'] if count_result else 0}")
            
            # 查看示例数据
            sample_result = execute_query("""
                SELECT project_name, task_name, task_owner, 
                       planned_start_date, planned_end_date 
                FROM project_tasks 
                LIMIT 3
            """, fetch_all=True)
            print("示例数据:")
            for row in sample_result:
                print(f"  {row}")
        else:
            print("project_tasks表不存在")
            
    except Exception as e:
        print(f"检查project_tasks表失败: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    test_database_connection()