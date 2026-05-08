import sys
sys.path.insert(0, 'project-backend')
from database.database import execute_query

result = execute_query('DESCRIBE customer_quality', fetch_all=True)
print("customer_quality 表结构:")
print("=" * 80)
for row in result:
    if 'Field' in row:
        print(f"{row['Field']:30s} {row['Type']:20s}")
