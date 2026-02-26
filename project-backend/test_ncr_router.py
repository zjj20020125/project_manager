#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试NCR路由注册
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi import FastAPI
import uvicorn

# 导入NCR路由
from main.ncr_apis import router as ncr_router

# 创建测试应用
app = FastAPI(title="NCR测试应用")

# 注册NCR路由
app.include_router(ncr_router)

@app.get("/")
async def root():
    return {"message": "NCR测试应用", "routes": [route.path for route in app.routes if hasattr(route, 'path')]}

if __name__ == "__main__":
    print("启动NCR测试应用...")
    uvicorn.run("test_ncr_router:app", host="127.0.0.1", port=8002, reload=True)