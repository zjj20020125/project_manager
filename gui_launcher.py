#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目管理前端服务图形化启动器
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from datetime import datetime

class FrontendLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("项目管理前端启动器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 服务状态
        self.process = None
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="项目管理前端服务启动器", 
            font=("微软雅黑", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # 端口信息框架
        port_frame = tk.Frame(self.root)
        port_frame.pack(pady=10)
        
        tk.Label(
            port_frame, 
            text="前端端口: ", 
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT)
        
        self.port_label = tk.Label(
            port_frame, 
            text="3000", 
            font=("微软雅黑", 12, "bold"),
            fg="#e74c3c"
        )
        self.port_label.pack(side=tk.LEFT)
        
        # 状态显示
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        tk.Label(
            status_frame, 
            text="服务状态: ", 
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            status_frame, 
            text="未启动", 
            font=("微软雅黑", 12, "bold"),
            fg="#7f8c8d"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 控制按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="启动服务",
            command=self.start_service,
            font=("微软雅黑", 12),
            bg="#27ae60",
            fg="white",
            width=12,
            height=2
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="停止服务",
            command=self.stop_service,
            font=("微软雅黑", 12),
            bg="#e74c3c",
            fg="white",
            width=12,
            height=2,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 访问链接
        link_frame = tk.Frame(self.root)
        link_frame.pack(pady=10)
        
        tk.Label(
            link_frame, 
            text="访问地址: ", 
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT)
        
        self.link_label = tk.Label(
            link_frame, 
            text="http://localhost:3000", 
            font=("微软雅黑", 12, "underline"),
            fg="#3498db",
            cursor="hand2"
        )
        self.link_label.pack(side=tk.LEFT)
        self.link_label.bind("<Button-1>", self.open_browser)
        
        # 日志显示区域
        log_label = tk.Label(
            self.root, 
            text="服务日志:", 
            font=("微软雅黑", 12, "bold")
        )
        log_label.pack(pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            width=70,
            height=15,
            font=("Consolas", 10),
            bg="#f8f9fa"
        )
        self.log_text.pack(pady=5, padx=20)
        
        # 底部信息
        footer_frame = tk.Frame(self.root)
        footer_frame.pack(pady=10)
        
        tk.Label(
            footer_frame, 
            text="© 2024 项目管理系统", 
            font=("微软雅黑", 9),
            fg="#95a5a6"
        ).pack()
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_service(self):
        if self.is_running:
            return
            
        try:
            # 更新UI状态
            self.status_label.config(text="启动中...", fg="#f39c12")
            self.start_button.config(state="disabled")
            self.log_message("正在启动前端服务...")
            
            # 设置工作目录
            project_dir = r"D:\desktop\项目管理\project manage\project-dashboard"
            if not os.path.exists(project_dir):
                raise FileNotFoundError("项目目录不存在")
                
            # 启动进程
            self.process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            
            # 更新UI
            self.status_label.config(text="运行中", fg="#27ae60")
            self.stop_button.config(state="normal")
            self.log_message("✓ 服务启动成功!")
            self.log_message("✓ 访问地址: http://localhost:3000")
            
            # 启动日志监控线程
            threading.Thread(target=self.monitor_process, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"✗ 启动失败: {str(e)}")
            self.status_label.config(text="启动失败", fg="#e74c3c")
            self.start_button.config(state="normal")
            messagebox.showerror("错误", f"启动失败:\n{str(e)}")
            
    def stop_service(self):
        if not self.is_running or not self.process:
            return
            
        try:
            self.log_message("正在停止服务...")
            self.process.terminate()
            self.process.wait(timeout=5)
            
            self.cleanup()
            self.log_message("✓ 服务已停止")
            
        except subprocess.TimeoutExpired:
            self.log_message("强制终止服务...")
            self.process.kill()
            self.cleanup()
            self.log_message("✓ 服务已强制停止")
        except Exception as e:
            self.log_message(f"✗ 停止服务时出错: {str(e)}")
            
    def cleanup(self):
        self.is_running = False
        self.process = None
        self.status_label.config(text="已停止", fg="#7f8c8d")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def monitor_process(self):
        """监控进程输出"""
        if not self.process:
            return
            
        try:
            # 监控标准输出
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_message(f"STDOUT: {line.strip()}")
                    
            # 监控错误输出
            for line in iter(self.process.stderr.readline, ''):
                if line:
                    self.log_message(f"STDERR: {line.strip()}")
                    
        except Exception as e:
            self.log_message(f"监控进程时出错: {str(e)}")
            
        # 进程结束后清理
        if self.is_running:
            self.cleanup()
            self.log_message("服务进程已结束")
            
    def open_browser(self, event=None):
        """打开浏览器访问前端"""
        import webbrowser
        try:
            webbrowser.open("http://localhost:3000")
            self.log_message("已在浏览器中打开前端页面")
        except Exception as e:
            self.log_message(f"打开浏览器失败: {str(e)}")

def main():
    root = tk.Tk()
    app = FrontendLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()