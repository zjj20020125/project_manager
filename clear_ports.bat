@echo off
chcp 65001 >nul
title 端口清理工具

echo ========================================
echo 端口清理工具
echo 目标端口: 3000, 3001, 3002, 3003
echo ========================================

:: 需要清理的端口列表
set PORTS=3000 3001 3002 3003

echo 检查并清理指定端口...

for %%p in (%PORTS%) do (
    echo.
    echo --- 检查端口 %%p ---
    
    :: 检查端口是否被占用
    netstat -an | findstr :%%p | findstr LISTENING >nul
    if !errorlevel! equ 0 (
        echo 端口 %%p 被占用，正在查找占用进程...
        
        :: 查找占用端口的进程ID
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do (
            echo 找到占用进程 PID: %%a
            
            :: 获取进程信息
            tasklist /fi "PID eq %%a" | findstr "node.exe" >nul
            if !errorlevel! equ 0 (
                echo 进程类型: Node.js 前端服务
            ) else (
                tasklist /fi "PID eq %%a" | findstr "python.exe" >nul
                if !errorlevel! equ 0 (
                    echo 进程类型: Python 后端服务
                ) else (
                    echo 进程类型: 其他服务
                )
            )
            
            :: 终止进程
            echo 正在终止进程 %%a ...
            taskkill /F /PID %%a >nul 2>&1
            if !errorlevel! equ 0 (
                echo ✓ 端口 %%p 已清理完成
            ) else (
                echo ✗ 端口 %%p 清理失败
            )
        )
    ) else (
        echo ✓ 端口 %%p 未被占用
    )
)

echo.
echo ========================================
echo 端口清理完成
echo ========================================

:: 验证清理结果
echo 验证清理结果:
for %%p in (%PORTS%) do (
    netstat -an | findstr :%%p | findstr LISTENING >nul
    if !errorlevel! equ 0 (
        echo ✗ 端口 %%p 仍有服务运行
    ) else (
        echo ✓ 端口 %%p 已成功清理
    )
)

echo.
echo 现在可以安全启动3000端口服务
pause