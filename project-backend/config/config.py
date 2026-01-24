import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "zjj520111314"),
    "database": os.getenv("DB_NAME", "jgj-project"),  # 修正：使用jgj-project数据库
    "charset": "utf8mb4"
}

# 服务配置
API_PREFIX = "/v1"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001