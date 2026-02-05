#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导入GUI工具启动脚本
检查依赖并启动图形界面
"""

import sys
import subprocess
import os

def check_pyside6():
    """检查PySide6是否已安装"""
    try:
        import PySide6
        print("✓ PySide6 已安装")
        return True
    except ImportError:
        print("✗ PySide6 未安装")
        return False

def install_pyside6():
    """安装PySide6"""
    print("正在安装 PySide6...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
        print("✓ PySide6 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PySide6 安装失败")
        return False

def main():
    print("=" * 50)
    print("Excel导入GUI工具启动器")
    print("=" * 50)
    
    # 检查PySide6
    if not check_pyside6():
        print("\n需要安装PySide6才能运行GUI界面")
        choice = input("是否现在安装PySide6? (y/n): ").lower().strip()
        if choice == 'y':
            if not install_pyside6():
                print("安装失败，请手动安装: pip install PySide6")
                return
        else:
            print("取消启动")
            return
    
    # 检查数据处理模块
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from datadeal.simple_datadeal import process_single_file
        print("✓ 数据处理模块可用")
    except ImportError as e:
        print(f"✗ 数据处理模块不可用: {e}")
        print("请确保 datadeal/simple_datadeal.py 文件存在且可导入")
        return
    
    # 启动GUI
    print("\n正在启动GUI界面...")
    try:
        from excel_import_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"启动GUI失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()