#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import requests

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend', 'main'))

print("Comprehensive API testing...")

# 定义要测试的API端点
api_endpoints = [
    '/v1/project/stats',
    '/v1/task/stats', 
    '/v1/chart/data',
    '/v1/projects/detail',
    '/v1/projects/stats',
    '/v1/task/list',
    '/v1/project-status-stats',
    '/v1/task-owner-stats',
    '/v1/projects-list'
]

base_url = 'http://localhost:8000'

for endpoint in api_endpoints:
    try:
        full_url = base_url + endpoint
        print(f"\nTesting: {endpoint}")
        response = requests.get(full_url, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Success - Response length: {len(response.text)} chars")
            # 显示前200个字符作为预览
            preview = response.text[:200]
            print(f"  Preview: {preview}...")
        else:
            print(f"  ✗ Error - {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection error - Backend might not be running")
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout error - Request took too long")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*50)
print("Testing frontend proxy configuration...")

# 测试前端代理配置
frontend_base_url = 'http://localhost:3024'
proxy_endpoints = [
    '/api/v1/project/stats',
    '/api/v1/task/stats'
]

print(f"Frontend is running at: {frontend_base_url}")
for endpoint in proxy_endpoints:
    try:
        full_url = frontend_base_url + endpoint
        print(f"\nTesting proxy: {endpoint}")
        response = requests.get(full_url, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ Proxy working - Response length: {len(response.text)} chars")
        else:
            print(f"  ✗ Proxy error - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection error - Frontend might not be running")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nTest completed!")