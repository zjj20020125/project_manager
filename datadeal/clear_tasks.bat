@echo off
setlocal

python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password='zjj520111314', database='jgj-project'); cursor = conn.cursor(); cursor.execute('DELETE FROM project_tasks;'); conn.commit(); print('成功删除', cursor.rowcount, '条任务记录'); cursor.close(); conn.close();"
pause