-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `jgj-project`;

-- 使用数据库
USE `jgj-project`;

-- 创建项目表
CREATE TABLE IF NOT EXISTS projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '项目ID',
    project_name VARCHAR(255) NOT NULL COMMENT '项目名称',
    project_manager VARCHAR(100) COMMENT '项目经理',
    planned_start_date DATE COMMENT '预计开始时间',
    planned_end_date DATE COMMENT '预计完成时间',
    project_serial_number VARCHAR(50) COMMENT '项目序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目信息表';