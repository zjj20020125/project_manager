# 项目管理及NCR系统 局域网部署指南

## 部署说明

要让其他人通过局域网访问您的项目管理及NCR系统，请按以下步骤操作：

## 1. 启动后端服务（双端口模式）

### 启动项目管理API服务（端口8001）：
```bash
cd "D:/desktop/项目管理/project manage"
python -c "
import sys
sys.path.insert(0, './project-backend')
from project-backend.main.main import app
import config.config
config.config.SERVER_PORT = 8001
import uvicorn
uvicorn.run(app, host='172.16.33.192', port=8001)
"
```

### 启动NCR管理API服务（端口8002）：
```bash
cd "D:/desktop/项目管理/project manage"
python -c "
import sys
sys.path.insert(0, './project-backend')
from project-backend.main.main import app
import config.config
config.config.SERVER_PORT = 8002
import uvicorn
uvicorn.run(app, host='172.16.33.192', port=8002)
"
```

## 2. 启动前端服务

### 启动项目管理前端（端口3000）：
```bash
cd "D:/desktop/项目管理/project manage/project-dashboard"
npx vite --host 172.16.33.192 --port 3000
```

### 启动NCR管理前端（端口3001）：
```bash
cd "D:/desktop/项目管理/project manage/project-dashboard"
npx vite --host 172.16.33.192 --port 3001 --config vite.config.ncr.js
```

## 3. 访问地址

启动完成后，其他用户可通过以下地址访问：

- **项目管理界面**: http://172.16.33.192:3000
- **NCR管理界面**: http://172.16.33.192:3001

## 4. 快速访问页面

您可以分享以下HTML页面给其他用户，让他们一键访问：

打开 `access_page.html` 文件即可。

## 5. 注意事项

1. 确保防火墙允许对应端口通信
2. 确保所有设备在同一个局域网内
3. 如遇到连接问题，请检查网络配置
4. 确保数据库服务正常运行

## 6. 防火墙设置（Windows）

如需开放端口，请以管理员身份运行PowerShell并执行：
```powershell
netsh advfirewall firewall add rule name="Project Management Port 3000" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="NCR Management Port 3001" dir=in action=allow protocol=TCP localport=3001
netsh advfirewall firewall add rule name="Project API Port 8001" dir=in action=allow protocol=TCP localport=8001
netsh advfirewall firewall add rule name="NCR API Port 8002" dir=in action=allow protocol=TCP localport=8002
```