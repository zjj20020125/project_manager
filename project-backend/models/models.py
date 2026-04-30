from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict

# 项目统计数据模型
class ProjectStats(BaseModel):
    total_projects: int = Field(description="已立项项目数")
    unstarted_projects: int = Field(description="未开始项目数")
    ongoing_projects: int = Field(description="进行中项目数")
    completed_projects: int = Field(description="已结项项目数")

# 任务统计数据模型
class TaskStats(BaseModel):
    total_milestones: int = Field(description="里程碑任务数")
    completed_milestones: int = Field(description="已完成里程碑数")
    total_subtasks: int = Field(description="子任务总数")
    accepted_subtasks: int = Field(description="已验收子任务数")
    completed_tasks: int = Field(description="已验收任务数")

# 任务列表数据模型
class TaskItem(BaseModel):
    projectNo: str
    projectName: str
    wbsNo: str
    taskName: str
    owner: Optional[str]
    taskType: str
    priority: str
    status: str
    planStart: str
    planEnd: str
    progress: str

# 图表数据模型
class ChartData(BaseModel):
    type_pie: List[Dict]  # 项目类型饼图数据
    source_bar: List[Dict]  # 项目来源柱状图数据
    load_bar: List[Dict]  # 项目经理负载数据
    gantt_data: List[Dict]  # 甘特图数据

# 客户反馈数据模型
class CustomerFeedback(BaseModel):
    feedback_id: Optional[int] = Field(description="反馈 ID")
    customer_name: str = Field(description="客户姓名")
    contact_info: str = Field(description="联系方式")
    project_name: Optional[str] = Field(default=None, description="关联项目名称")
    feedback_type: str = Field(description="反馈类型")
    priority: str = Field(description="优先级")
    title: str = Field(description="反馈标题")
    description: str = Field(description="详细描述")
    expected_solution: Optional[str] = Field(default=None, description="期望解决方案")
    status: str = Field(default="待处理", description="状态")
    handler: Optional[str] = Field(default=None, description="处理人")
    process_record: Optional[str] = Field(default=None, description="处理记录")
    solution: Optional[str] = Field(default=None, description="解决方案")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remarks: Optional[str] = Field(default=None, description="备注")

# 客户质量反馈数据模型（用于数据导入）
class CustomerQualityImport(BaseModel):
    customer_name: str = Field(description="客户姓名")
    contact_info: Optional[str] = Field(default=None, description="联系方式")
    company_name: Optional[str] = Field(default=None, description="公司名称")
    product_name: Optional[str] = Field(default=None, description="产品名称")
    project_name: Optional[str] = Field(default=None, description="项目名称")
    quality_issue_type: str = Field(description="质量问题类型")
    issue_description: str = Field(description="问题描述")
    occurrence_date: Optional[date] = Field(default=None, description="发生日期")
    discovery_date: Optional[date] = Field(default=None, description="发现日期")
    severity: str = Field(default="一般", description="严重程度")
    priority: str = Field(default="中", description="优先级")
    expected_solution: Optional[str] = Field(default=None, description="期望解决方案")
    remarks: Optional[str] = Field(default=None, description="备注")