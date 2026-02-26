import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import urllib.parse

def test_gantt_api():
    # 测试URL编码的项目名称
    project_name = "DF4B-NG7583型新能源机车5#车主辅一体变流器柜"
    encoded_name = urllib.parse.quote(project_name)
    print(f"原始项目名称: {project_name}")
    print(f"URL编码后: {encoded_name}")
    
    # 构造完整的URL
    base_url = "http://localhost:8001"
    endpoint = f"/v1/task-gantt-data?project_name={encoded_name}"
    full_url = base_url + endpoint
    
    print(f"完整URL: {full_url}")
    
    try:
        # 发送GET请求
        response = requests.get(full_url, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据条数: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print("前几条数据示例:")
                for i, item in enumerate(data[:3]):
                    print(f"  {i+1}. {item}")
        else:
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_gantt_api()