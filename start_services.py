import subprocess
import threading
import time
import requests
import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

def check_port_availability(host, port):
    """检查端口是否可用"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # 如果连接失败，则端口可用
    except:
        return True

def start_backend_server(port, service_name):
    """启动后端服务器"""
    try:
        # 修改配置文件中的端口
        config_path = os.path.join(current_dir, "project-backend", "config", "config.py")
        
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 替换端口
        import re
        config_content = re.sub(r'SERVER_PORT = \d+', f'SERVER_PORT = {port}', config_content)
        
        # 写回配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"正在启动{service_name}服务 (端口 {port})...")
        
        # 启动后端服务
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "project-backend.main.main:app",
            "--host", "172.16.33.192",
            "--port", str(port),
            "--reload"
        ]
        
        # 在Windows上使用subprocess.Popen并设置适当的参数
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 等待服务启动
        time.sleep(5)
        
        # 检查服务是否正常运行
        try:
            response = requests.get(f"http://172.16.33.192:{port}{os.environ.get('API_PREFIX', '/v1')}/project/stats", timeout=10)
            if response.status_code == 200:
                print(f"{service_name}服务已在 http://172.16.33.192:{port} 上成功启动")
            else:
                print(f"{service_name}服务启动可能有问题，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"{service_name}服务可能未正常启动: {e}")
        
        # 等待进程结束
        proc.wait()
        
    except Exception as e:
        print(f"启动{service_name}服务时出错: {e}")

def start_frontend_server(port, config_file, service_name):
    """启动前端服务器"""
    try:
        print(f"正在启动{service_name}前端 (端口 {port})...")
        
        cmd = [
            "npx", "vite", 
            "--host", "172.16.33.192", 
            "--port", str(port)
        ]
        
        # 如果指定了配置文件，则使用它
        if config_file:
            cmd.extend(["--config", config_file])
        
        proc = subprocess.Popen(cmd, cwd=os.path.join(current_dir, "project-dashboard"), 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # 等待服务启动
        time.sleep(3)
        
        # 检查服务是否正常运行
        try:
            response = requests.get(f"http://172.16.33.192:{port}", timeout=10)
            if response.status_code in [200, 404]:  # 200是正常，404表示服务器运行但页面不存在
                print(f"{service_name}前端已在 http://172.16.33.192:{port} 上成功启动")
            else:
                print(f"{service_name}前端启动可能有问题，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"{service_name}前端可能未正常启动: {e}")
        
        # 等待进程结束
        proc.wait()
        
    except Exception as e:
        print(f"启动{service_name}前端时出错: {e}")

def main():
    print("正在启动项目管理及NCR管理系统...")
    print("项目管理界面: http://172.16.33.192:3000")
    print("NCR管理界面: http://172.16.33.192:3001")
    print("项目管理API: http://172.16.33.192:8001")
    print("NCR管理API: http://172.16.33.192:8002")
    
    # 检查端口可用性
    ports_to_check = [(8001, "项目管理API"), (8002, "NCR管理API"), 
                      (3000, "项目管理前端"), (3001, "NCR管理前端")]
    
    for port, name in ports_to_check:
        if not check_port_availability("172.16.33.192", port):
            print(f"错误: 端口 {port} ({name}) 已被占用，请先停止占用该端口的程序")
            return
    
    # 创建线程运行服务
    threads = []
    
    # 启动项目管理后端 (端口8001)
    backend1_thread = threading.Thread(
        target=start_backend_server, 
        args=(8001, "项目管理API"),
        daemon=True
    )
    threads.append(backend1_thread)
    
    # 启动NCR管理后端 (端口8002)
    backend2_thread = threading.Thread(
        target=start_backend_server, 
        args=(8002, "NCR管理API"),
        daemon=True
    )
    threads.append(backend2_thread)
    
    # 启动项目管理前端 (端口3000)
    frontend1_thread = threading.Thread(
        target=start_frontend_server, 
        args=(3000, None, "项目管理前端"),
        daemon=True
    )
    threads.append(frontend1_thread)
    
    # 启动NCR管理前端 (端口3001)
    frontend2_thread = threading.Thread(
        target=start_frontend_server, 
        args=(3001, "vite.config.ncr.js", "NCR管理前端"),
        daemon=True
    )
    threads.append(frontend2_thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    print("\n所有服务已启动!")
    print("请在浏览器中访问:")
    print("- 项目管理界面: http://172.16.33.192:3000")
    print("- NCR管理界面: http://172.16.33.192:3001")
    
    try:
        # 等待所有线程结束
        for thread in threads:
            thread.join(timeout=1)  # 使用短超时以响应中断
    except KeyboardInterrupt:
        print("\n正在关闭服务...")

if __name__ == "__main__":
    main()