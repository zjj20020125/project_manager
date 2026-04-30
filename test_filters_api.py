"""测试问题筛选条件 API"""
import requests

# 测试获取筛选条件（直接访问后端）
response = requests.get("http://localhost:8001/v1/feedback/problem/filters")

print(f"状态码：{response.status_code}\n")

if response.ok:
    data = response.json()
    print(f"完整响应数据：\n{data}\n")
    
    if 'data' in data:
        filters = data['data']
        print(f"\n=== 筛选条件数据 ===")
        print(f"月份数量：{len(filters.get('months', []))}")
        print(f"月份列表：{filters.get('months', [])[:5]}...")  # 只显示前 5 个
        
        print(f"\n新责任班组数量：{len(filters.get('new_responsible_teams', []))}")
        print(f"新责任班组列表：{filters.get('new_responsible_teams', [])}")
        
        print(f"\n产品类型数量：{len(filters.get('product_types', []))}")
        print(f"产品类型列表：{filters.get('product_types', [])[:5]}...")  # 只显示前 5 个
    else:
        print("响应中没有 'data' 字段")
else:
    print(f"请求失败：{response.text}")
