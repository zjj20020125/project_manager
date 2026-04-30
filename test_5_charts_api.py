"""测试质量问题统计 API"""
import requests

BASE_URL = "http://localhost:8001"

def test_problem_stats():
    """测试质量问题统计接口"""
    url = f"{BASE_URL}/v1/feedback/problem/stats"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 调用成功！\n")
        
        if data.get('success'):
            stats = data['data']
            
            print("=" * 60)
            print("📊 质量问题统计数据")
            print("=" * 60)
            
            # 基础指标
            print(f"\n1️⃣ 问题总数：{stats.get('total', 0)}")
            print(f"   平均考核金额：¥{stats.get('average_amount', 0)}")
            
            # KPI 指标
            kpi = stats.get('kpi_metrics', {})
            print(f"\n2️⃣ 已关闭问题数：{kpi.get('closed_count', 0)}")
            print(f"   累计考核金额：¥{kpi.get('total_amount', 0)}")
            
            # 5 个图表数据
            print("\n3️⃣ 问题定性统计（饼图）:")
            type_dist = stats.get('type_distribution', {})
            for name, count in type_dist.items():
                print(f"   - {name}: {count}")
            
            print("\n4️⃣ 责任主体统计（柱状图）:")
            subject_dist = stats.get('responsible_subject_distribution', {})
            for name, count in subject_dist.items():
                print(f"   - {name}: {count}")
            
            print("\n5️⃣ 产品类型统计（饼图）:")
            product_dist = stats.get('product_category_distribution', {})
            for name, count in product_dist.items():
                print(f"   - {name}: {count}")
            
            print("\n6️⃣ 问题分类统计（柱状图）:")
            issue_dist = stats.get('issue_category_distribution', {})
            for name, count in issue_dist.items():
                print(f"   - {name}: {count}")
            
            print("\n" + "=" * 60)
            print("✅ 所有统计数据获取成功！")
            print("=" * 60)
        else:
            print(f"❌ API 返回失败：{data}")
    else:
        print(f"❌ HTTP 错误：{response.status_code}")
        print(f"响应内容：{response.text}")

if __name__ == "__main__":
    try:
        test_problem_stats()
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        print("请确保后端服务正在运行 (http://localhost:8001)")
