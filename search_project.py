"""搜索包含关键词的项目"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project-backend'))
from database.database import execute_query

def search_projects(keyword):
    """搜索项目"""
    sql = """
    SELECT project_id, project_name, actual_end_date, project_status
    FROM projects
    WHERE project_name LIKE %s
    """
    
    projects = execute_query(sql, (f"%{keyword}%",), fetch_all=True)
    
    if not projects:
        print(f"❌ 未找到包含关键词 '{keyword}' 的项目")
        return
    
    print(f"找到 {len(projects)} 个项目:")
    print("-" * 80)
    for p in projects:
        print(f"ID: {p['project_id']}")
        print(f"  名称：{p['project_name']}")
        print(f"  实际完成时间：{p['actual_end_date']}")
        print(f"  状态：{p['project_status']}")
        print("-" * 80)

if __name__ == "__main__":
    keyword = "阿塞拜疆"
    search_projects(keyword)
