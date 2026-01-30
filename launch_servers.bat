@echo off
echo ========================================
echo 项目管理及NCR系统 局域网部署工具
echo ========================================
echo.
echo 正在启动服务...
echo.

echo 启动项目管理API服务 (端口8001)...
start "Project Management API" cmd /k "cd /d "D:\desktop\项目管理\project manage\project-backend" && python -m uvicorn main.main:app --host 172.16.33.192 --port 8001"

timeout /t 3 /nobreak >nul

echo 启动NCR管理API服务 (端口8002)...
start "NCR Management API" cmd /k "cd /d "D:\desktop\项目管理\project manage\project-backend" && python -m uvicorn main.main:app --host 172.16.33.192 --port 8002"

timeout /t 3 /nobreak >nul

echo 启动项目管理前端 (端口3000)...
start "Project Management Frontend" cmd /k "cd /d "D:\desktop\项目管理\project manage\project-dashboard" && npx vite --host 172.16.33.192 --port 3000"

timeout /t 3 /nobreak >nul

echo 启动NCR管理前端 (端口3001)...
start "NCR Management Frontend" cmd /k "cd /d "D:\desktop\项目管理\project manage\project-dashboard" && npx vite --host 172.16.33.192 --port 3001 --config vite.config.ncr.js"

echo.
echo ========================================
echo 所有服务已启动！
echo ========================================
echo.
echo 其他用户可通过以下地址访问：
echo 📋 项目管理界面: http://172.16.33.192:3000
echo 📊 NCR管理界面: http://172.16.33.192:3001
echo.
echo 每个服务将在独立的命令行窗口中运行
echo 关闭服务：关闭相应的命令行窗口
echo ========================================
pause