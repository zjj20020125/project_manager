import requests

# 测试后端API
base_url = "http://localhost:8001/api/v1"

# 测试不同的状态值
statuses = ["完成", "异常", "延期完成", "已完成", "进行中", "未开始"]

print("测试后端API /tasks-by-status/{status} 接口:")

for status in statuses:
    try:
        url = f"{base_url}/tasks-by-status/{status}"
        print(f"\n请求: GET {url}")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据长度: {len(data)}")
            if len(data) > 0:
                print(f"前3条数据示例:")
                for i, item in enumerate(data[:3]):
                    print(f"  {i+1}. {item.get('task_name', '')[:50]}... - 状态: {item.get('task_status', '')}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

# 额外测试项目状态分布接口
print("\n\n测试项目状态分布接口:")
try:
    url = f"{base_url}/project-status-stats"
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"状态分布: {data}")
except Exception as e:
    print(f"请求失败: {str(e)}")