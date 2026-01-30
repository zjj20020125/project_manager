#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目backend目录到模块搜索路径
backend_path = os.path.join(os.path.dirname(__file__), 'project-backend')
sys.path.append(backend_path)

def test_responsibility_analysis():
    """测试责任分析API函数"""
    try:
        # 导入后端函数
        from main.main import get_responsibility_analysis
        
        print("正在测试责任分析API...")
        result = get_responsibility_analysis()
        print(f"责任分析结果: {result}")
        
        if result:
            print("✓ API调用成功，返回了数据")
            print(f"  数据条数: {len(result)}")
            for item in result[:5]:  # 只打印前5个
                print(f"  - {item['name']}: {item['value']}次")
        else:
            print("○ API调用成功，但没有返回数据（可能数据库中没有符合条件的记录）")
        
        return result
    
    except ImportError as e:
        print(f"导入错误: {e}")
        return None
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_responsibility_analysis()