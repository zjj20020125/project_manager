import sys
import os
import importlib.util

# 设置正确的编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到模块搜索路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project-backend')
sys.path.insert(0, project_root)

# 动态加载模块，指定UTF-8编码
spec = importlib.util.spec_from_file_location("main", 
    os.path.join(project_root, "main", "main.py"), 
    loader=None)
main_module = importlib.util.module_from_spec(spec)

# 执行模块
spec.loader.exec_module(main_module)

# 启动服务
if hasattr(main_module, 'app'):
    import uvicorn
    # 从配置文件读取端口设置
    import config.config
    port = config.config.SERVER_PORT
    uvicorn.run(main_module.app, host="0.0.0.0", port=port, reload=False)
else:
    print("Error: Could not find 'app' in main module")