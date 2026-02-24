#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def test_apis():
    base_url = "http://localhost:8001"
    
    print("=== 测试异常任务相关API ===\n")
    
    # 测试1: 获取异常任务负责人统计
    print("1. 测试异常任务负责人统计 API:")
    try:
        response = requests.get(f"{base_url}/v1/abnormal-task-owner-stats")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print(f"   数据条数: {len(data)}")
        else:
            print(f"   错误响应: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试2: 获取特定负责人的异常任务详情
    print("2. 测试特定负责人异常任务详情 API:")
    test_owners = ["申洋华", "李建平", "刘财", "朱剑文", "熊超", "陈丰"]
    
    for owner in test_owners:
        try:
            response = requests.get(f"{base_url}/v1/owner-abnormal-tasks/{owner}")
            print(f"   负责人 '{owner}': 状态码 {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"     任务数量: {len(data)}")
                if data:
                    print(f"     示例任务: {data[0].get('taskName', 'N/A')}")
            else:
                print(f"     错误: {response.text}")
        except Exception as e:
            print(f"     请求失败: {e}")
        print()

if __name__ == "__main__":
    test_apis()