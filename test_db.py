import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend'))

try:
    from database.database import get_db_connection, execute_query
    print("成功导入数据库模块")
    
    # 测试数据库连接
    conn = get_db_connection()
    if conn:
        print("✅ 数据库连接成功")
        conn.close()
        
        # 测试查询一些基本数据
        print("\n=== 测试数据查询 ===")
        
        # 查询项目表
        projects = execute_query("SELECT COUNT(*) as count FROM projects", fetch_one=True)
        if projects:
            print(f"项目表记录数: {projects['count']}")
        
        # 查询任务表
        tasks = execute_query("SELECT COUNT(*) as count FROM tasks", fetch_one=True)
        if tasks:
            print(f"任务表记录数: {tasks['count']}")
            
        # 查询项目状态分布
        status_stats = execute_query("""
            SELECT project_status, COUNT(*) as count 
            FROM projects 
            GROUP BY project_status
        """, fetch_all=True)
        if status_stats:
            print("\n项目状态分布:")
            for stat in status_stats:
                print(f"  {stat['project_status']}: {stat['count']}个")
                
    else:
        print("❌ 数据库连接失败")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()