#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查API路由注册情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main.modular_main import app
    
    print("=== 已注册的API路由 ===")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"{list(methods)} {route.path}")
    
    print("\n=== 查找异常任务相关路由 ===")
    abnormal_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'abnormal' in route.path.lower():
            methods = getattr(route, 'methods', ['GET'])
            abnormal_routes.append((list(methods), route.path))
    
    if abnormal_routes:
        print("找到异常任务相关路由:")
        for methods, path in abnormal_routes:
            print(f"  {methods} {path}")
    else:
        print("未找到异常任务相关路由!")
        
except Exception as e:
    print(f"检查路由时出错: {e}")
    import traceback
    traceback.print_exc()
