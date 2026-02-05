"""
项目管理系统启动脚本
支持在传统版本和模块化版本之间切换
"""

import os
import sys
import subprocess
import argparse

def start_traditional():
    """启动传统版本"""
    print("启动传统版本项目管理系统...")
    os.chdir("project-backend/main")
    subprocess.run([sys.executable, "main.py"])

def start_modular():
    """启动模块化版本"""
    print("启动模块化版本项目管理系统...")
    os.chdir("project-backend/main")
    subprocess.run([sys.executable, "modular_main.py"])

def main():
    parser = argparse.ArgumentParser(description="项目管理系统启动器")
    parser.add_argument(
        "--mode", 
        choices=["traditional", "modular"], 
        default="traditional",
        help="选择启动模式: traditional(传统) 或 modular(模块化)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "traditional":
        print("=== 传统版本 ===")
        print("特点:")
        print("- 单一主文件包含所有API接口")
        print("- 适合小型项目或快速开发")
        print("- 代码集中，便于快速修改")
        start_traditional()
    else:
        print("=== 模块化版本 ===")
        print("特点:")
        print("- 按功能模块分离代码")
        print("- 项目管理模块: project_apis.py")
        print("- NCR管理模块: ncr_apis.py")
        print("- 甘特图模块: gantt_api.py")
        print("- 更好的代码组织和可维护性")
        start_modular()

if __name__ == "__main__":
    main()