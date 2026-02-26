import requests
import json
from datetime import datetime

def diagnose_backend_apis():
    base_url = "http://localhost:8002"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"=== NCR后端API诊断报告 ({timestamp}) ===\n")
    
    # 测试的核心API列表
    apis_to_test = [
        ("/v1/ncr/type-distribution", "NCR类型分布"),
        ("/v1/ncr/stage-distribution", "NCR阶段分布"),
        ("/v1/dqjd-wczz-data", "DQJD/WCZZ数据"),
        ("/v1/ncr/responsibility-analysis", "责任人员分析"),
        ("/v1/ncr/unreviewed-stage-responsibility", "未评审阶段责任"),
        ("/v1/ncr/list?page=1&limit=5", "NCR列表"),
        ("/v1/ncr/sscx-statistics", "SSCX统计"),
        ("/v1/ncr/sscx-trend", "SSCX趋势")
    ]
    
    working_apis = []
    failed_apis = []
    
    for endpoint, description in apis_to_test:
        try:
            print(f"测试 {description} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                data_length = len(data) if isinstance(data, list) else "N/A"
                print(f"  ✅ 成功 - 状态码: {response.status_code}, 数据量: {data_length}")
                working_apis.append((endpoint, description, data_length))
                
                # 显示部分数据样本（前2条）
                if isinstance(data, list) and len(data) > 0:
                    print(f"  📊 数据样本: {json.dumps(data[:2], ensure_ascii=False, indent=4)}")
                    
            else:
                print(f"  ❌ 失败 - 状态码: {response.status_code}")
                print(f"  💥 错误详情: {response.text[:200]}...")
                failed_apis.append((endpoint, description, response.status_code, response.text[:100]))
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ 连接失败 - 无法连接到后端服务")
            failed_apis.append((endpoint, description, "Connection Error", "无法连接到后端"))
            
        except requests.exceptions.Timeout:
            print(f"  ❌ 超时 - 请求超时")
            failed_apis.append((endpoint, description, "Timeout", "请求超时"))
            
        except Exception as e:
            print(f"  ❌ 异常 - {str(e)}")
            failed_apis.append((endpoint, description, "Exception", str(e)))
        
        print()
    
    # 输出总结报告
    print("=" * 60)
    print("📊 诊断总结:")
    print(f"✅ 正常接口: {len(working_apis)} 个")
    print(f"❌ 异常接口: {len(failed_apis)} 个")
    print()
    
    if working_apis:
        print("🟢 正常接口列表:")
        for endpoint, desc, data_len in working_apis:
            print(f"  • {desc}: {endpoint} (数据量: {data_len})")
        print()
    
    if failed_apis:
        print("🔴 异常接口列表:")
        for endpoint, desc, status, error in failed_apis:
            print(f"  • {desc}: {endpoint}")
            print(f"    状态: {status}")
            print(f"    错误: {error}")
        print()
    
    # 提供修复建议
    if len(failed_apis) > 0:
        print("🔧 建议修复步骤:")
        print("1. 检查数据库连接是否正常")
        print("2. 确认相关数据表是否存在")
        print("3. 检查后端服务日志获取详细错误信息")
        print("4. 重启后端服务")
        print("5. 验证数据库中是否有测试数据")

if __name__ == "__main__":
    diagnose_backend_apis()