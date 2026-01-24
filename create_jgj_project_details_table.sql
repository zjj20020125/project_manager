-- 使用数据库
USE `jgj-project`;

-- 创建项目详情表（子表）
CREATE TABLE IF NOT EXISTS project_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '详情ID',
    project_serial_number VARCHAR(50) COMMENT '项目编号',
    project_name VARCHAR(255) NOT NULL COMMENT '项目名称',
    project_manager VARCHAR(100) COMMENT '项目经理',
    task_info JSON COMMENT '任务信息（以JSON格式存储原Excel中的详细数据）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (project_serial_number) REFERENCES projects(project_serial_number) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目详情表';

-- 另一种设计：如果需要更结构化的数据，可以创建包含Excel原始列的表
-- 注意：这个表的设计假设Excel文件有一些常见的列名
CREATE TABLE IF NOT EXISTS project_tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
    project_serial_number VARCHAR(50) COMMENT '项目编号',
    project_name VARCHAR(255) NOT NULL COMMENT '项目名称',
    project_manager VARCHAR(100) COMMENT '项目经理',
    task_name VARCHAR(255) COMMENT '任务名称',
    wbs_code VARCHAR(100) COMMENT 'WBS编码',
    planned_start_date DATE COMMENT '计划开始日期',
    planned_end_date DATE COMMENT '计划结束日期',
    actual_start_date DATE COMMENT '实际开始日期',
    actual_end_date DATE COMMENT '实际结束日期',
    progress DECIMAL(5,2) COMMENT '进度',
    task_owner VARCHAR(100) COMMENT '任务负责人',
    task_status VARCHAR(50) COMMENT '任务状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (project_serial_number) REFERENCES projects(project_serial_number) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目任务表';