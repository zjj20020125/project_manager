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