import subprocess
import sys
import os
import threading
import time
import webbrowser

def start_backend_service(port):
    """启动后端服务"""
    os.chdir("project-backend")
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main.main:app",
        "--host", "172.16.33.192",
        "--port", str(port),
        "--reload"
    ]
    subprocess.run(cmd)

def start_frontend_service(port, config=None):
    """启动前端服务"""
    os.chdir("project-dashboard")
    cmd = [sys.executable, "-m", "subprocess", "call", 
           "npx", "vite", "--host", "172.16.33.192", "--port", str(port)]
    
    if config:
        cmd.extend(["--config", config])
    
    subprocess.run(["npx", "vite", "--host", "172.16.33.192", "--port", str(port)] + (["--config", config] if config else []), shell=True)

def main():
    print("="*60)
    print("项目管理及NCR系统 局域网部署工具")
    print("="*60)
    print("服务将在以下地址运行：")
    print("- 项目管理界面: http://172.16.33.192:3000")
    print("- NCR管理界面: http://172.16.33.192:3001")
    print("- 项目管理API: http://172.16.33.192:8001")
    print("- NCR管理API: http://172.16.33.192:8002")
    print("="*60)
    
    print("\n正在启动服务，请稍候...")
    
    # 启动后端服务
    print("\n启动项目管理API服务 (端口8001)...")
    backend1 = threading.Thread(target=start_backend_service, args=(8001,))
    backend1.daemon = True
    backend1.start()
    
    time.sleep(2)  # 等待第一个服务启动
    
    print("启动NCR管理API服务 (端口8002)...")
    backend2 = threading.Thread(target=start_backend_service, args=(8002,))
    backend2.daemon = True
    backend2.start()
    
    time.sleep(2)  # 等待后端服务启动
    
    print("启动项目管理前端 (端口3000)...")
    frontend1 = threading.Thread(target=start_frontend_service, args=(3000,))
    frontend1.daemon = True
    frontend1.start()
    
    time.sleep(2)  # 等待前端服务启动
    
    print("启动NCR管理前端 (端口3001)...")
    frontend2 = threading.Thread(target=start_frontend_service, args=(3001, "vite.config.ncr.js"))
    frontend2.daemon = True
    frontend2.start()
    
    print("\n所有服务已启动！")
    print("\n其他用户可通过以下地址访问：")
    print("📋 项目管理界面: http://172.16.33.192:3000")
    print("📊 NCR管理界面: http://172.16.33.192:3001")
    
    print("\n按 Ctrl+C 停止服务")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")

if __name__ == "__main__":
    main()