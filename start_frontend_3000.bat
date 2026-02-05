@echo off
chcp 65001 >nul
title 项目管理前端服务 (端口3000)

echo ========================================
echo 项目管理前端服务启动脚本
echo 端口: 3000
echo ========================================

:: 切换到项目目录
cd /d "D:\desktop\项目管理\project manage\project-dashboard"

:: 检查Node.js是否安装
echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

:: 检查npm是否可用
echo 检查npm环境...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到npm，请检查Node.js安装
    pause
    exit /b 1
)

:: 检查3000端口是否被占用
echo 检查3000端口占用情况...
netstat -an | findstr :3000 >nul
if %errorlevel% equ 0 (
    echo 警告: 3000端口已被占用
    echo 正在终止占用3000端口的进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
        echo 终止进程 PID: %%a
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
    
    :: 再次检查确保端口已释放
    netstat -an | findstr :3000 >nul
    if %errorlevel% equ 0 (
        echo 错误: 无法释放3000端口
        pause
        exit /b 1
    )
)

:: 安装依赖（如果需要）
echo 检查项目依赖...
if not exist "node_modules" (
    echo 安装项目依赖...
    npm install
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

:: 启动开发服务器
echo 启动前端开发服务器 (端口3000)...
echo 访问地址: http://localhost:3000
echo ========================================

npm run dev

:: 如果服务意外退出
echo.
echo 服务已停止
pause