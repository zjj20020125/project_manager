import requests
import json

def test_sscx_apis():
    base_url = "http://localhost:8002"
    
    print("测试SSCX统计API...")
    
    # 测试SSCX统计接口
    try:
        response = requests.get(f"{base_url}/v1/ncr/sscx-statistics")
        print(f"SSCX统计接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SSCX统计返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"SSCX统计接口错误: {response.text}")
    except Exception as e:
        print(f"SSCX统计接口调用失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试SSCX趋势接口
    try:
        response = requests.get(f"{base_url}/v1/ncr/sscx-trend")
        print(f"SSCX趋势接口状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SSCX趋势返回数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"SSCX趋势接口错误: {response.text}")
    except Exception as e:
        print(f"SSCX趋势接口调用失败: {e}")

if __name__ == "__main__":
    test_sscx_apis()