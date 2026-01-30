# 项目管理及NCR系统 局域网部署

## 项目概述

这是一个集成了项目管理和NCR（不合格品控制）管理的系统，支持局域网内多用户访问。

## 部署方式

### 方法一：一键启动（推荐）
双击运行 `launch_servers.bat` 文件，会自动启动所有服务。

### 方法二：手动启动
参考 `SETUP_GUIDE.md` 中的详细说明。

## 访问地址

- **项目管理界面**: http://172.16.33.192:3000
- **NCR管理界面**: http://172.16.33.192:3001

## 快速访问

分享 `access_page.html` 文件给团队成员，他们可以直接点击按钮访问系统。

## 系统架构

- **项目管理API**: http://172.16.33.192:8001
- **NCR管理API**: http://172.16.33.192:8002
- **项目管理前端**: http://172.16.33.192:3000
- **NCR管理前端**: http://172.16.33.192:3001

## 防火墙设置

如需开放端口，请以管理员身份运行PowerShell并执行：

```powershell
netsh advfirewall firewall add rule name="Project Management Port 3000" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="NCR Management Port 3001" dir=in action=allow protocol=TCP localport=3001
netsh advfirewall firewall add rule name="Project API Port 8001" dir=in action=allow protocol=TCP localport=8001
netsh advfirewall firewall add rule name="NCR API Port 8002" dir=in action=allow protocol=TCP localport=8002
```

## 故障排除

1. 如果无法访问，请确认所有服务已成功启动
2. 检查防火墙设置
3. 确认设备在相同局域网内
4. 检查数据库连接是否正常