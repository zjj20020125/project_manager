#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查project-subtasks路由是否存在
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main.modular_main import app
    
    print("=== 检查project-subtasks路由 ===")
    found = False
    for route in app.routes:
        if hasattr(route, 'path') and 'project-subtasks' in route.path:
            methods = getattr(route, 'methods', ['GET'])
            print(f"找到路由: {list(methods)} {route.path}")
            found = True
    
    if not found:
        print("❌ 未找到project-subtasks路由!")
        print("\n=== 所有路由 ===")
        for route in app.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', ['GET'])
                print(f"{list(methods)} {route.path}")
    else:
        print("✅ 找到project-subtasks路由")
        
except Exception as e:
    print(f"检查路由时出错: {e}")
    import traceback
    traceback.print_exc()
