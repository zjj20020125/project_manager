#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量修改NCR API路由路径
"""

import re
import os

def fix_ncr_routes():
    file_path = 'main/ncr_apis.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要修改的路由映射
    route_mappings = [
        ('"/ncr/stage-distribution"', '"/v1/ncr/stage-distribution"'),
        ('"/ncr/responsibility-analysis"', '"/v1/ncr/responsibility-analysis"'),
        ('"/ncr/by-stage"', '"/v1/ncr/by-stage"'),
        ('"/ncr/detail/"', '"/v1/ncr/detail/"'),
        ('"/ncr/list"', '"/v1/ncr/list"'),
        ('"/dqjd-wczz-data"', '"/v1/dqjd-wczz-data"'),
        ('"/ncr/unreviewed-stage-responsibility"', '"/v1/ncr/unreviewed-stage-responsibility"'),
        ('"/ncr/unreviewed-responsibility"', '"/v1/ncr/unreviewed-responsibility"'),
        ('"/ncr/sscx-statistics"', '"/v1/ncr/sscx-statistics"'),
        ('"/ncr/sscx-trend"', '"/v1/ncr/sscx-trend"')
    ]
    
    # 批量替换
    for old_route, new_route in route_mappings:
        content = content.replace(old_route, new_route)
        print(f"替换: {old_route} -> {new_route}")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("路由路径修改完成!")

if __name__ == "__main__":
    fix_ncr_routes()