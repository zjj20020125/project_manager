#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SSCX统计API接口
验证新添加的SSCX字段统计功能
"""

import sys
import os
# 添加项目根目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://127.0.0.1:8001"

def test_sscx_statistics():
    """测试SSCX统计接口"""
    print("=" * 50)
    print("测试SSCX字段统计接口")
    print("=" * 50)
    
    try:
        # 测试SSCX统计接口
        response = requests.get(f"{BASE_URL}/v1/ncr/sscx-statistics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接口调用成功")
            print(f"📊 返回数据条数: {len(data)}")
            
            if data:
                print("\n详细统计结果:")
                for item in data:
                    print(f"  - {item['name']}: {item['value']} 项")
            else:
                print("⚠️  没有返回统计数据")
        else:
            print(f"❌ 接口调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_sscx_trend():
    """测试SSCX趋势统计接口"""
    print("\n" + "=" * 50)
    print("测试SSCX时间趋势统计接口")
    print("=" * 50)
    
    try:
        # 测试SSCX趋势统计接口
        response = requests.get(f"{BASE_URL}/v1/ncr/sscx-trend")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接口调用成功")
            print(f"📊 返回数据条数: {len(data)}")
            
            if data:
                print("\n趋势统计结果:")
                for item in data:
                    print(f"\n月份: {item['month']}")
                    print(f"  总计: {item['total']} 项")
                    # 显示各SSCX类型的统计
                    for key, value in item.items():
                        if key not in ['month', 'total']:
                            print(f"  - {key}: {value} 项")
            else:
                print("⚠️  没有返回趋势数据")
        else:
            print(f"❌ 接口调用失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_existing_ncr_apis():
    """测试现有的NCR接口确保没有被影响"""
    print("\n" + "=" * 50)
    print("测试现有NCR接口兼容性")
    print("=" * 50)
    
    test_urls = [
        "/v1/ncr/type-distribution",
        "/v1/ncr/stage-distribution", 
        "/v1/ncr/responsibility-analysis"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code == 200:
                print(f"✅ {url} - 正常")
            else:
                print(f"❌ {url} - 失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")

if __name__ == "__main__":
    print(f"开始测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试新接口
    test_sscx_statistics()
    test_sscx_trend()
    
    # 测试现有接口兼容性
    test_existing_ncr_apis()
    
    print(f"\n测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")