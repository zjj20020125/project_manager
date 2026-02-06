#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入功能调试脚本
用于诊断项目名称和负责人识别问题
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "datadeal"))

try:
    from simple_datadeal import (
        parse_filename,
        extract_project_info_from_excel,
        process_single_file
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的目录下运行此脚本")
    sys.exit(1)

def test_filename_parsing():
    """测试文件名解析功能"""
    print("=== 文件名解析测试 ===")
    
    test_filenames = [
        "tmpkz105vf_",  # 临时文件名
        "tmp5nop4ka3",  # 临时文件名
        "项目A_张三.xlsx",
        "项目B_李四_2024.xlsx",
        "test_project_wangwu.xls",
        "项目管理_赵六_报告.xlsx"
    ]
    
    for filename in test_filenames:
        print(f"\n测试文件名: {filename}")
        project_name, manager = parse_filename(filename)
        print(f"  解析结果: 项目名称='{project_name}', 负责人='{manager}'")

def test_excel_extraction(excel_file_path=None):
    """测试Excel内容提取功能"""
    print("\n=== Excel内容提取测试 ===")
    
    if excel_file_path and os.path.exists(excel_file_path):
        print(f"测试文件: {excel_file_path}")
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_file_path)
            print(f"文件形状: {df.shape}")
            print("列名:", list(df.columns))
            print("前几行数据:")
            print(df.head(3))
            
            # 测试提取功能
            project_name, manager = extract_project_info_from_excel(df, excel_file_path)
            print(f"\n提取结果: 项目名称='{project_name}', 负责人='{manager}'")
            
        except Exception as e:
            print(f"读取Excel文件出错: {e}")
    else:
        print("未提供有效的Excel文件路径，跳过测试")

def test_process_single_file(file_path):
    """测试完整的文件处理流程"""
    print(f"\n=== 完整处理流程测试 ===")
    print(f"处理文件: {file_path}")
    
    if not os.path.exists(file_path):
        print("文件不存在!")
        return
    
    try:
        result = process_single_file(file_path)
        print("处理结果:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()

def create_test_excel():
    """创建测试用的Excel文件"""
    print("\n=== 创建测试Excel文件 ===")
    
    # 创建测试数据
    test_data = {
        '项目名称': ['测试项目A', '测试项目B'],
        '负责人': ['张三', '李四'],
        '开始日期': ['2024-01-01', '2024-02-01'],
        '结束日期': ['2024-12-31', '2024-11-30'],
        '预算': [100000, 200000]
    }
    
    df = pd.DataFrame(test_data)
    
    # 保存为不同的文件名格式进行测试
    test_files = [
        ('test_项目测试_王五.xlsx', '项目测试'),
        ('temp_file_123.xlsx', 'temp_file_123'),  # 临时文件名
        ('项目管理_赵六_报告.xlsx', '项目管理')
    ]
    
    created_files = []
    
    for filename, expected_name in test_files:
        filepath = os.path.join(os.getcwd(), filename)
        df.to_excel(filepath, index=False)
        created_files.append((filepath, expected_name))
        print(f"创建测试文件: {filename}")
    
    return created_files

def main():
    """主函数"""
    print("项目导入功能调试工具")
    print("=" * 50)
    
    # 1. 测试文件名解析
    test_filename_parsing()
    
    # 2. 创建测试文件
    test_files = create_test_excel()
    
    # 3. 测试完整处理流程
    print("\n" + "=" * 50)
    print("测试完整处理流程:")
    
    for file_path, expected_name in test_files:
        test_process_single_file(file_path)
        
        # 清理测试文件
        try:
            os.remove(file_path)
            print(f"清理测试文件: {os.path.basename(file_path)}")
        except:
            pass
    
    print("\n调试完成!")

if __name__ == "__main__":
    main()