"""
创建客户质量反馈数据表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import get_db_connection


def create_customer_quality_table():
    """创建客户质量反馈表"""
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return
    
    try:
        cursor = conn.cursor()
        
        # 创建客户质量反馈表的 SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `customer_quality` (
          `quality_id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '质量反馈 ID（主键）',
          `customer_name` VARCHAR(100) NOT NULL COMMENT '客户姓名',
          `contact_info` VARCHAR(200) DEFAULT NULL COMMENT '联系方式（电话/邮箱）',
          `company_name` VARCHAR(500) DEFAULT NULL COMMENT '公司名称',
          `product_name` VARCHAR(500) DEFAULT NULL COMMENT '产品名称',
          `project_name` VARCHAR(500) DEFAULT NULL COMMENT '项目名称',
          `quality_issue_type` VARCHAR(50) NOT NULL DEFAULT '其他' COMMENT '质量问题类型（质量投诉/技术建议/售后服务/其他）',
          `issue_description` TEXT NOT NULL COMMENT '问题描述',
          `occurrence_date` DATE DEFAULT NULL COMMENT '发生日期',
          `discovery_date` DATE DEFAULT NULL COMMENT '发现日期',
          `severity` VARCHAR(20) NOT NULL DEFAULT '一般' COMMENT '严重程度（严重/一般/轻微）',
          `priority` VARCHAR(20) NOT NULL DEFAULT '中' COMMENT '优先级（高/中/低）',
          `expected_solution` TEXT DEFAULT NULL COMMENT '期望解决方案',
          `remarks` TEXT DEFAULT NULL COMMENT '备注',
          `status` VARCHAR(20) NOT NULL DEFAULT '待处理' COMMENT '状态（待处理/处理中/已解决/已关闭）',
          `handler` VARCHAR(100) DEFAULT NULL COMMENT '处理人',
          `process_record` TEXT DEFAULT NULL COMMENT '处理记录',
          `solution` TEXT DEFAULT NULL COMMENT '解决方案',
          `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
          INDEX `idx_quality_type` (`quality_issue_type`),
          INDEX `idx_severity` (`severity`),
          INDEX `idx_priority` (`priority`),
          INDEX `idx_status` (`status`),
          INDEX `idx_create_time` (`create_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户质量反馈信息表';
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("✅ 客户质量反馈表创建成功！")
        print("\n表结构说明:")
        print("-" * 80)
        print("主键：quality_id")
        print("主要字段:")
        print("  - customer_name: 客户姓名")
        print("  - contact_info: 联系方式")
        print("  - company_name: 公司名称")
        print("  - product_name: 产品名称")
        print("  - project_name: 项目名称")
        print("  - quality_issue_type: 质量问题类型")
        print("  - issue_description: 问题描述")
        print("  - occurrence_date: 发生日期")
        print("  - discovery_date: 发现日期")
        print("  - severity: 严重程度")
        print("  - priority: 优先级")
        print("  - expected_solution: 期望解决方案")
        print("  - status: 处理状态")
        print("  - handler: 处理人")
        print("  - solution: 解决方案")
        print("索引:")
        print("  - idx_quality_type: 类型索引")
        print("  - idx_severity: 严重程度索引")
        print("  - idx_priority: 优先级索引")
        print("  - idx_status: 状态索引")
        print("  - idx_create_time: 创建时间索引")
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ 创建表失败：{e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("开始创建客户质量反馈数据表")
    print("=" * 80)
    create_customer_quality_table()
    print("\n完成！")
