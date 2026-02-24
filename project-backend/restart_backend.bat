@echo off
cd /d "D:\desktop\项目管理\project manage\project-backend"
echo 正在停止现有Python进程...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo 正在启动后端服务...
start "" python main\modular_main.py
echo 后端服务已启动
timeout /t 3 /nobreak >nul
echo 测试API...
curl -X GET "http://localhost:8001/v1/abnormal-task-owner-stats" -H "accept: application/json"
pause
