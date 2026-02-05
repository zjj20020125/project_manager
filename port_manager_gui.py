#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端口管理工具 - 图形化界面
支持批量关闭指定端口
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import psutil
from datetime import datetime

class PortManager:
    def __init__(self, root):
        self.root = root
        self.root.title("端口管理工具")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # 默认端口列表
        self.target_ports = [3000, 3001, 3002, 3003]
        
        self.setup_ui()
        
    def setup_ui(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="端口管理工具", 
            font=("微软雅黑", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # 端口选择框架
        port_frame = tk.Frame(self.root)
        port_frame.pack(pady=10)
        
        tk.Label(
            port_frame, 
            text="目标端口: ", 
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT)
        
        # 端口复选框
        self.port_vars = {}
        for port in self.target_ports:
            var = tk.BooleanVar(value=True)
            self.port_vars[port] = var
            cb = tk.Checkbutton(
                port_frame,
                text=str(port),
                variable=var,
                font=("微软雅黑", 11)
            )
            cb.pack(side=tk.LEFT, padx=10)
        
        # 自定义端口输入
        custom_frame = tk.Frame(self.root)
        custom_frame.pack(pady=10)
        
        tk.Label(
            custom_frame, 
            text="自定义端口: ", 
            font=("微软雅黑", 12)
        ).pack(side=tk.LEFT)
        
        self.custom_port = tk.Entry(
            custom_frame,
            width=10,
            font=("微软雅黑", 11)
        )
        self.custom_port.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            custom_frame,
            text="添加",
            command=self.add_custom_port,
            font=("微软雅黑", 10),
            bg="#3498db",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # 控制按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="检查端口状态",
            command=self.check_ports,
            font=("微软雅黑", 12),
            bg="#f39c12",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="关闭选中端口",
            command=self.close_selected_ports,
            font=("微软雅黑", 12),
            bg="#e74c3c",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="全部关闭",
            command=self.close_all_ports,
            font=("微软雅黑", 12),
            bg="#c0392b",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        # 状态显示区域
        status_label = tk.Label(
            self.root, 
            text="端口状态:", 
            font=("微软雅黑", 12, "bold")
        )
        status_label.pack(pady=(20, 5))
        
        # 创建Treeview显示端口状态
        columns = ("端口", "状态", "进程ID", "进程名", "占用程序")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=8)
        
        # 设置列标题和宽度
        self.tree.heading("端口", text="端口")
        self.tree.heading("状态", text="状态")
        self.tree.heading("进程ID", text="进程ID")
        self.tree.heading("进程名", text="进程名")
        self.tree.heading("占用程序", text="占用程序")
        
        self.tree.column("端口", width=80, anchor="center")
        self.tree.column("状态", width=100, anchor="center")
        self.tree.column("进程ID", width=80, anchor="center")
        self.tree.column("进程名", width=120, anchor="center")
        self.tree.column("占用程序", width=200, anchor="w")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(pady=5, padx=20, side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 20))
        
        # 日志区域
        log_label = tk.Label(
            self.root, 
            text="操作日志:", 
            font=("微软雅黑", 12, "bold")
        )
        log_label.pack(pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            width=80,
            height=8,
            font=("Consolas", 9),
            bg="#f8f9fa"
        )
        self.log_text.pack(pady=5, padx=20)
        
        # 初始化端口状态
        self.refresh_port_status()
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
        
    def get_port_processes(self, port):
        """获取占用指定端口的进程信息"""
        processes = []
        try:
            # 使用netstat获取端口信息
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, 
                text=True, 
                encoding='gbk'
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                process = psutil.Process(int(pid))
                                processes.append({
                                    'pid': pid,
                                    'name': process.name(),
                                    'exe': process.exe() if process.exe() else '未知'
                                })
                            except (psutil.NoSuchProcess, ValueError):
                                processes.append({
                                    'pid': pid,
                                    'name': '未知',
                                    'exe': '未知'
                                })
        except Exception as e:
            self.log_message(f"检查端口 {port} 时出错: {str(e)}")
            
        return processes
        
    def refresh_port_status(self):
        """刷新端口状态显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 检查每个端口
        for port in self.target_ports:
            processes = self.get_port_processes(port)
            
            if processes:
                for proc in processes:
                    status = "占用中"
                    self.tree.insert("", "end", values=(
                        port, 
                        status, 
                        proc['pid'], 
                        proc['name'], 
                        proc['exe']
                    ))
            else:
                self.tree.insert("", "end", values=(port, "空闲", "-", "-", "-"))
                
    def check_ports(self):
        """检查端口状态"""
        self.log_message("正在检查端口状态...")
        self.refresh_port_status()
        self.log_message("端口状态检查完成")
        
    def close_port_process(self, pid):
        """关闭指定PID的进程"""
        try:
            process = psutil.Process(int(pid))
            process_name = process.name()
            process.terminate()
            
            # 等待进程优雅退出
            try:
                process.wait(timeout=3)
                self.log_message(f"✓ 已终止进程 {pid} ({process_name})")
                return True
            except psutil.TimeoutExpired:
                # 强制杀死进程
                process.kill()
                self.log_message(f"✓ 强制终止进程 {pid} ({process_name})")
                return True
                
        except psutil.NoSuchProcess:
            self.log_message(f"✗ 进程 {pid} 不存在")
            return False
        except Exception as e:
            self.log_message(f"✗ 终止进程 {pid} 失败: {str(e)}")
            return False
            
    def close_selected_ports(self):
        """关闭选中的端口"""
        selected_ports = [port for port, var in self.port_vars.items() if var.get()]
        
        if not selected_ports:
            messagebox.showwarning("警告", "请至少选择一个端口")
            return
            
        if not messagebox.askyesno("确认", f"确定要关闭端口 {selected_ports} 吗？"):
            return
            
        self.log_message(f"开始关闭端口: {selected_ports}")
        
        closed_count = 0
        for port in selected_ports:
            processes = self.get_port_processes(port)
            if processes:
                for proc in processes:
                    if self.close_port_process(proc['pid']):
                        closed_count += 1
            else:
                self.log_message(f"端口 {port} 未被占用")
                
        self.log_message(f"关闭完成，共终止 {closed_count} 个进程")
        self.refresh_port_status()
        
    def close_all_ports(self):
        """关闭所有目标端口"""
        if not messagebox.askyesno("确认", "确定要关闭所有目标端口吗？"):
            return
            
        self.log_message("开始关闭所有目标端口...")
        closed_count = 0
        
        for port in self.target_ports:
            processes = self.get_port_processes(port)
            if processes:
                for proc in processes:
                    if self.close_port_process(proc['pid']):
                        closed_count += 1
                        
        self.log_message(f"全部关闭完成，共终止 {closed_count} 个进程")
        self.refresh_port_status()
        
    def add_custom_port(self):
        """添加自定义端口"""
        port_str = self.custom_port.get().strip()
        if not port_str:
            messagebox.showwarning("警告", "请输入端口号")
            return
            
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError("端口号超出范围")
                
            if port in self.target_ports:
                messagebox.showinfo("提示", f"端口 {port} 已存在")
                return
                
            self.target_ports.append(port)
            
            # 添加新的复选框
            var = tk.BooleanVar(value=True)
            self.port_vars[port] = var
            cb = tk.Checkbutton(
                self.root.nametowidget(self.root.winfo_children()[2]),  # port_frame
                text=str(port),
                variable=var,
                font=("微软雅黑", 11)
            )
            cb.pack(side=tk.LEFT, padx=10)
            
            self.custom_port.delete(0, tk.END)
            self.log_message(f"已添加自定义端口: {port}")
            self.refresh_port_status()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的端口号(1-65535)")

def main():
    root = tk.Tk()
    app = PortManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()