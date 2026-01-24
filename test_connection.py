#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import requests

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'project-backend', 'main'))

print("Testing backend API connection...")

try:
    # 测试项目统计数据API - 现在应该使用8000端口
    response = requests.get('http://localhost:8000/v1/project/stats', timeout=5)
    print(f"Project stats API response: {response.status_code}")
    print(f"Response body: {response.text[:500]}...")
    
    if response.status_code == 200:
        print("✓ Backend API is working correctly!")
    else:
        print("✗ Backend API returned error")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend. The backend service might not be running.")
    print("Please start the backend service first using:")
    print("cd \"D:\\desktop\\项目管理\\project manage\\project-backend\\main\"")
    print("python -c \"import uvicorn; import main; uvicorn.run(main.app, host='0.0.0.0', port=8000)\"")
    
except requests.exceptions.Timeout:
    print("✗ Request timed out. Backend might be slow to respond.")
    
except Exception as e:
    print(f"✗ Error occurred: {e}")

print("\nChecking if backend is running...")
try:
    import urllib.request
    req = urllib.request.Request('http://localhost:8000/v1/project/stats')
    req.add_header('User-Agent', 'Mozilla/5.0')
    response = urllib.request.urlopen(req, timeout=5)
    print(f"✓ Backend is responding with status: {response.getcode()}")
except Exception as e:
    print(f"✗ Backend is not accessible: {e}")