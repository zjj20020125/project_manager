import requests

# 测试问题列表API
url = "http://localhost:8001/v1/feedback/problem/list"
params = {
    "page": 1,
    "limit": 2
}

print(f"🧪 测试API: {url}")
print(f"参数: {params}\n")

try:
    response = requests.get(url, params=params)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功!")
        print(f"总数: {data.get('total', 0)}")
        print(f"返回记录数: {len(data.get('list', []))}")
        
        if data.get('list'):
            print(f"\n第一条记录:")
            for key, value in list(data['list'][0].items())[:5]:
                print(f"  {key}: {value}")
    else:
        print(f"❌ 失败: {response.text}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
