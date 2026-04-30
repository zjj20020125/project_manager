from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 基础模型类（所有表模型继承此类）
Base = declarative_base()

class CustomerQualityIssue(Base):
    """
    客户处反馈问题表（对应 customer_quality 表）
    字段说明：与 Excel 表二字段一一对应，补充自增主键和时间戳字段
    """
    __tablename__ = "customer_quality"  # 数据库表名

    # 1. 系统字段（自增主键+时间戳）
    id = Column(Integer, primary_key=True, autoincrement=True, comment="唯一标识，自增主键")
    created_time = Column(DateTime, default=datetime.now, comment="记录创建时间")
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="记录更新时间")

    # 2. Excel 表二业务字段（按顺序对应，字段类型适配数据特征）
    serial_number = Column(Integer, nullable=False, comment="序号")  # 序号（非空）
    oa_number = Column(String(50), comment="OA 编号（OA 系统编号）")  # OA 编号
    month = Column(String(10), nullable=False, comment="月份（如：2026-01）")  # 月份
    market_category = Column(String(10), nullable=False, comment="市场分类（如：国内/海外）")  # 市场分类
    occurrence_date = Column(DateTime, nullable=False, comment="发生日期")  # 发生日期
    occurrence_unit = Column(String(50), nullable=False, comment="发生单位（客户/部门）")  # 发生单位
    vehicle_model = Column(String(50), comment="车型（可为空）")  # 车型
    vehicle_number = Column(String(50), comment="车号（可为空）")  # 车号
    product_name = Column(String(50), nullable=False, comment="产品名称（如：油箱/箱盖）")  # 产品名称
    drawing_number = Column(String(50), comment="图号（可为空）")  # 图号
    product_quantity = Column(Integer, comment="产品数量（可为空）")  # 产品数量
    product_category = Column(String(50), comment="产品归类（可为空）")  # 产品归类
    production_repair_type = Column(String(10), comment="新造/检修类型（如：新造/检修）")  # 新造/检修类型
    problem_description = Column(Text, comment="问题描述（长文本，可为空）")  # 问题描述
    problem_category_1 = Column(String(100), comment="问题分类 1（如：设计问题/工艺问题）")  # 问题分类 1
    supplement_category_2 = Column(String(100), comment="补充分类 2（如：原材料/外协加工）")  # 补充分类 2
    problem_category = Column(String(50), comment="问题分类（如：外观问题/尺寸超差）")  # 问题分类
    problem_nature = Column(String(50), nullable=False, comment="问题定性（如：制造问题/采购问题）")  # 问题定性
    cause_analysis = Column(Text, comment="原因分析（逐条分析，长文本）")  # 原因分析
    corrective_measures = Column(Text, comment="纠正措施（长文本）")  # 纠正措施
    measure_implementation = Column(String(50), comment="措施执行情况（如：已完成/进行中）")  # 措施执行情况
    assessment_form = Column(String(50), comment="考核单（编号，可为空）")  # 考核单 - 数据库中为 assessment_form_number
    assessment_amount = Column(Integer, comment="考核金额（数值，可为空）")  # 考核金额 - 数据库中为 int 类型
    workshop = Column(String(50), comment="所属车间（可为空）")  # 所属车间
    quality_engineer = Column(String(50), comment="质量工程师（姓名，可为空）")  # 质量工程师
    inspector = Column(String(50), comment="检验员（姓名，可为空）")  # 检验员
    responsible_team = Column(String(50), comment="责任班组（可为空）")  # 责任班组
    supplier = Column(String(50), comment="供应商（名称，可为空）")  # 供应商
    responsible_person = Column(String(50), comment="责任人（姓名，可为空）")  # 责任人
    qrcode_import_status = Column(String(20), comment="二维码导入状态（如：已导入/未导入）")  # 二维码导入状态 - 数据库中为 qrcode_imported
    is_closed = Column(String(10), nullable=False, comment="是否关闭（是/否，可为空）")  # 是否关闭
    closing_date = Column(DateTime, comment="关闭日期（可为空）")  # 关闭日期
    remark = Column(Text, comment="备注（长文本，可为空）")  # 备注
    other1 = Column(String(50), comment="预留字段 1（Excel 表中未命名字段）")  # 预留字段 1
    other2 = Column(String(50), comment="预留字段 2（Excel 表中未命名字段）")  # 预留字段 2

    def __repr__(self):
        """打印模型实例时显示的格式（便于调试）"""
        return f"<CustomerQualityIssue(serial_number={self.serial_number}, product_name={self.product_name})>"