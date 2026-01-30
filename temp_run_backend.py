import subprocess
import threading
import time

def run_project_management_server():
    """启动项目管理界面服务 (端口8001)"""
    cmd = [
        "python", "-m", "uvicorn", 
        "project-backend.main.main:app",
        "--host", "172.16.33.192",
        "--port", "8001",
        "--reload"
    ]
    subprocess.run(cmd)

def run_ncr_management_server():
    """启动NCR管理界面服务 (端口8002)"""
    cmd = [
        "python", "-m", "uvicorn", 
        "project-backend.main.main:app", 
        "--host", "172.16.33.192",
        "--port", "8002",
        "--reload"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    print("正在启动项目管理界面服务 (端口8001)...")
    print("正在启动NCR管理界面服务 (端口8002)...")
    
    # 创建线程运行两个服务
    project_thread = threading.Thread(target=run_project_management_server)
    ncr_thread = threading.Thread(target=run_ncr_management_server)
    
    project_thread.start()
    ncr_thread.start()
    
    try:
        project_thread.join()
        ncr_thread.join()
    except KeyboardInterrupt:
        print("\n正在关闭服务...")