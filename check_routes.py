#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.routers import project_router, data_router, task_router, chart_router
import main.project_apis as project_apis

routers = {
    'project_router': project_router.router,
    'data_router': data_router.router,
    'task_router': task_router.router,
    'chart_router': chart_router.router,
    'project_apis': project_apis.router
}

print("检查各路由器中的路由:")

for name, router in routers.items():
    routes = [route.path for route in router.routes]
    projects_list_routes = [route for route in routes if 'projects-list' in route]
    if projects_list_routes:
        print(f'{name} 包含 projects-list 路由: {projects_list_routes}')
    else:
        print(f'{name} 不包含 projects-list 路由')
    
    # 显示所有路由的一部分
    if len(routes) > 0:
        print(f'  {name} 的前5个路由: {routes[:5]}')
    print()