#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修改后的异常任务统计功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_service_method():
    """测试服务层方法"""
    print("=== 测试服务层方法 ===")
    try:
        from main.services.task_service import TaskService
        result = TaskService.get_abnormal_task_owner_stats()
        print(f"服务层返回结果: {result}")
        print(f"结果类型: {type(result)}")
        print(f"结果长度: {len(result)}")
        if result:
            print("前3个结果:")
            for i, item in enumerate(result[:3]):
                print(f"  {i+1}. {item}")
        return True
    except Exception as e:
        print(f"服务层测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_query():
    """直接测试数据库查询"""
    print("\n=== 直接数据库查询测试 ===")
    try:
        from database.database import execute_query
        
        # 测试新的查询逻辑
        sql = """
        SELECT 
            task_owner,
            COUNT(*) as task_count
        FROM project_tasks
        WHERE task_status = '异常'
          AND task_owner IS NOT NULL 
          AND task_owner != ''
          AND task_owner != 'nan'
          AND task_owner != 'NaN'
          AND task_owner != 'null'
          AND task_owner != 'NULL'
          AND task_owner != '<NULL>'
          AND task_owner != 'None'
          AND TRIM(task_owner) != ''
        GROUP BY task_owner
        ORDER BY task_count DESC
        LIMIT 10
        """
        
        results = execute_query(sql, fetch_all=True)
        print(f"直接查询结果: {results}")
        print(f"结果数量: {len(results) if results else 0}")
        
        if results:
            total_count = sum(r.get('task_count', 0) for r in results)
            print(f"总异常任务数: {total_count}")
            
        return True
    except Exception as e:
        print(f"直接查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试异常任务统计功能...")
    
    service_ok = test_service_method()
    query_ok = test_direct_query()
    
    if service_ok and query_ok:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败！")
