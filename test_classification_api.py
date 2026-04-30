"""
测试问题分类 1 和补充分类 2 统计 API
"""
import requests
import json

# 后端服务地址
BASE_URL = "http://localhost:8000/api/v1"

def test_classification_stats():
    """测试问题分类统计接口"""
    print("=" * 60)
    print("测试问题分类 1 和补充分类 2 统计 API")
    print("=" * 60)
    
    try:
        # 调用质量问题统计 API
        response = requests.get(f"{BASE_URL}/feedback/problem/stats")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ API 调用成功")
            
            if data.get("success"):
                stats = data.get("data", {})
                
                # 检查问题分类 1 统计数据
                category_1_dist = stats.get("category_1_distribution", {})
                print(f"\n📊 问题分类 1 统计:")
                if category_1_dist:
                    for category, count in list(category_1_dist.items())[:5]:  # 只显示前 5 个
                        print(f"  - {category}: {count} 条")
                else:
                    print("  (暂无数据)")
                
                # 检查补充分类 2 统计数据
                supplement_2_dist = stats.get("supplement_category_2_distribution", {})
                print(f"\n📊 补充分类 2 统计:")
                if supplement_2_dist:
                    for category, count in list(supplement_2_dist.items())[:5]:  # 只显示前 5 个
                        print(f"  - {category}: {count} 条")
                else:
                    print("  (暂无数据)")
                
                # 显示其他统计信息
                print(f"\n📈 总体统计:")
                print(f"  - 问题总数：{stats.get('total', 0)} 条")
                print(f"  - 平均考核金额：¥{stats.get('average_amount', 0):.2f}")
                print(f"  - 已关闭问题数：{stats.get('closed', 0)} 条")
                
                print("\n✓ 测试完成!")
                
            else:
                print(f"\n✗ API 返回失败：{data}")
        else:
            print(f"\n✗ HTTP 错误：{response.status_code}")
            print(f"响应内容：{response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到后端服务，请确保后端服务正在运行")
        print(f"服务地址：{BASE_URL}")
    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_classification_stats()
