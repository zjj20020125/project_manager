#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database.database import execute_query

# 查询所有异常任务的WBS代码
sql = 'SELECT task_name, wbs_code, task_status FROM project_tasks WHERE task_status = "异常"'
results = execute_query(sql, fetch_all=True) or []

print("异常任务WBS代码分析:")
for task in results:
    wbs = str(task['wbs_code'])
    # 直接用Python正则表达式判断
    import re
    is_milestone = bool(re.match(r'^[0-9]+$', wbs))
    print(f'{task["task_name"]}: WBS={wbs}, 是里程碑: {is_milestone}')