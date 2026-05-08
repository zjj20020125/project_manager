import requests

base_url = "http://localhost:8001"

apis_to_test = [
    ("/v1/feedback/problem/filters", "GET", {}),
    ("/v1/feedback/problem/stats", "GET", {"month": "2026-01"}),
    ("/v1/feedback/problem/list", "GET", {"page": 1, "limit": 2}),
]

print("=" * 80)
print("🧪 测试 CustomerFeedback 相关 API")
print("=" * 80)

for path, method, params in apis_to_test:
    url = f"{base_url}{path}"
    print(f"\n📡 测试: {method} {path}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        
        status_icon = "✅" if response.status_code == 200 else "❌"
        print(f"   {status_icon} 状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   错误信息: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 异常: {e}")

print("\n" + "=" * 80)
