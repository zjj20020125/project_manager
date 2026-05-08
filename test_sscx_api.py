"""
测试SSCX API接口是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_sscx_apis():
    """测试所有SSCX相关的API"""
    
    print("=" * 80)
    print("开始测试SSCX API接口")
    print("=" * 80)
    
    # 1. 测试基础健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return
    
    # 2. 测试 SSCX Statistics API
    print("\n2. 测试 /v1/ncr/sscx-statistics...")
    try:
        response = requests.get(f"{BASE_URL}/v1/ncr/sscx-statistics", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   数据类型: {type(data)}")
            if isinstance(data, list):
                print(f"   数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"   前3条数据:")
                    for i, item in enumerate(data[:3], 1):
                        print(f"      {i}. {item}")
                else:
                    print("   ⚠️ 返回空数组")
            else:
                print(f"   响应数据: {data}")
        else:
            print(f"   ❌ 错误响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 3. 测试 SSCX Trend API
    print("\n3. 测试 /v1/ncr/sscx-trend...")
    try:
        response = requests.get(f"{BASE_URL}/v1/ncr/sscx-trend", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   数据类型: {type(data)}")
            if isinstance(data, list):
                print(f"   数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"   前2条数据:")
                    for i, item in enumerate(data[:2], 1):
                        print(f"      {i}. {item}")
                else:
                    print("   ⚠️ 返回空数组")
            else:
                print(f"   响应数据: {data}")
        else:
            print(f"   ❌ 错误响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 4. 测试 SSCX Yearly Stats API
    print("\n4. 测试 /v1/ncr/sscx-yearly-stats...")
    try:
        response = requests.get(f"{BASE_URL}/v1/ncr/sscx-yearly-stats", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   数据类型: {type(data)}")
            if isinstance(data, list):
                print(f"   数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"   前5条数据:")
                    for i, item in enumerate(data[:5], 1):
                        print(f"      {i}. {item}")
                else:
                    print("   ⚠️ 返回空数组")
            else:
                print(f"   响应数据: {data}")
        else:
            print(f"   ❌ 错误响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 5. 测试 Problem Hierarchy Stats API
    print("\n5. 测试 /v1/ncr/problem-hierarchy-stats...")
    try:
        response = requests.get(f"{BASE_URL}/v1/ncr/problem-hierarchy-stats", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   数据类型: {type(data)}")
            if isinstance(data, list):
                print(f"   数据条数: {len(data)}")
                if len(data) > 0:
                    print(f"   前2条数据（简化）:")
                    for i, item in enumerate(data[:2], 1):
                        print(f"      {i}. name={item.get('name')}, value={item.get('value')}, children_count={len(item.get('children', []))}")
                else:
                    print("   ⚠️ 返回空数组")
            else:
                print(f"   响应数据: {data}")
        else:
            print(f"   ❌ 错误响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 80)
    print("API测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_sscx_apis()
