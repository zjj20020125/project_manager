#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试异常子任务数据查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import execute_query

def test_abnormal_tasks():
    """测试异常子任务查询"""
    print("=== 测试异常子任务数据 ===")
    
    # 检查表是否存在
    check_table_sql = "SHOW TABLES LIKE 'project_tasks'"
    table_exists = execute_query(check_table_sql)
    print(f"project_tasks表是否存在: {bool(table_exists)}")
    
    if not table_exists:
        print("project_tasks表不存在")
        return
    
    # 检查表结构
    describe_sql = "DESCRIBE project_tasks"
    columns_result = execute_query(describe_sql, fetch_all=True)
    if columns_result:
        print("表字段:")
        for col in columns_result:
            print(f"  {col['Field']}: {col['Type']}")
    
    # 查询所有任务状态分布
    status_dist_sql = "SELECT task_status, COUNT(*) as count FROM project_tasks GROUP BY task_status"
    status_results = execute_query(status_dist_sql, fetch_all=True) or []
    print("\n任务状态分布:")
    for result in status_results:
        print(f"  {result['task_status']}: {result['count']} 个")
    
    # 查询所有异常状态的任务
    abnormal_all_sql = "SELECT task_id, task_name, task_owner, wbs_code, task_status FROM project_tasks WHERE task_status = '异常'"
    abnormal_all_results = execute_query(abnormal_all_sql, fetch_all=True) or []
    print(f"\n所有异常状态任务数量: {len(abnormal_all_results)}")
    
    if abnormal_all_results:
        print("异常任务详情:")
        for i, task in enumerate(abnormal_all_results[:10]):  # 只显示前10个
            print(f"  {i+1}. {task['task_name']} - 负责人: '{task['task_owner']}' - WBS: {task['wbs_code']}")
    
    # 查询异常子任务（排除里程碑）
    abnormal_sub_sql = """
    SELECT task_id, task_name, task_owner, wbs_code, task_status 
    FROM project_tasks 
    WHERE task_status = '异常' 
      AND wbs_code NOT REGEXP '^[0-9]+$'
    """
    abnormal_sub_results = execute_query(abnormal_sub_sql, fetch_all=True) or []
    print(f"\n异常子任务数量: {len(abnormal_sub_results)}")
    
    if abnormal_sub_results:
        print("异常子任务详情:")
        for i, task in enumerate(abnormal_sub_results):
            print(f"  {i+1}. {task['task_name']} - 负责人: '{task['task_owner']}' - WBS: {task['wbs_code']}")
            
            # 检查负责人字段的有效性
            owner = task['task_owner']
            print(f"     负责人字段分析: '{owner}'")
            print(f"     - 是否为None: {owner is None}")
            print(f"     - 是否为空字符串: {owner == ''}")
            print(f"     - strip后是否为空: {str(owner).strip() == '' if owner else True}")
            print(f"     - 类型: {type(owner)}")
    
    # 查询带有各种无效值的负责人
    invalid_owner_sql = """
    SELECT task_id, task_name, task_owner, wbs_code, task_status 
    FROM project_tasks 
    WHERE task_status = '异常' 
      AND wbs_code NOT REGEXP '^[0-9]+$'
      AND (task_owner IS NULL 
           OR task_owner = '' 
           OR task_owner = 'nan'
           OR task_owner = 'NaN'
           OR task_owner = 'null'
           OR task_owner = 'NULL'
           OR task_owner = '<NULL>'
           OR task_owner = 'None'
           OR TRIM(task_owner) = '')
    """
    invalid_owner_results = execute_query(invalid_owner_sql, fetch_all=True) or []
    print(f"\n含有无效负责人字段的异常子任务数量: {len(invalid_owner_results)}")
    
    if invalid_owner_results:
        print("无效负责人任务详情:")
        for i, task in enumerate(invalid_owner_results):
            print(f"  {i+1}. {task['task_name']} - 负责人: '{task['task_owner']}' - WBS: {task['wbs_code']}")

if __name__ == "__main__":
    test_abnormal_tasks()