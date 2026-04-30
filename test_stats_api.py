"""测试问题统计 API"""
import requests

url = "http://localhost:8001/v1/feedback/problem/stats"

try:
    response = requests.get(url)
    print(f"状态码：{response.status_code}")
    print(f"\n响应内容：")
    print(response.json())
except Exception as e:
    print(f"请求失败：{e}")
