import requests

# 测试后端API
url = "http://localhost:8001/v1/task-gantt-data"
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")  # 只打印前500个字符
except Exception as e:
    print(f"请求失败: {e}")

# 测试带API前缀的URL
url_with_prefix = "http://localhost:8001/api/v1/task-gantt-data"
try:
    response = requests.get(url_with_prefix)
    print(f"\n带API前缀的URL Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"\n带API前缀的URL请求失败: {e}")