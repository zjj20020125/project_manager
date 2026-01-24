/*
 Navicat Premium Data Transfer

 Source Server         : lcoa
 Source Server Type    : MySQL
 Source Server Version : 80013 (8.0.13)
 Source Host           : localhost:3306
 Source Schema         : jgjncr

 Target Server Type    : MySQL
 Target Server Version : 80013 (8.0.13)
 File Encoding         : 65001

 Date: 21/01/2026 18:15:41
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for jgjncr
-- ----------------------------
DROP TABLE IF EXISTS `jgjncr`;
CREATE TABLE `jgjncr`  (
  `create_date` date NULL DEFAULT NULL COMMENT '创建日期 - 记录创建的日期',
  `distribute_date` date NULL DEFAULT NULL COMMENT '分发日期 - 记录分发流转的日期',
  `current_node` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '当前节点 - 流程当前所处的处理节点（如：待审核、处理中）',
  `pending_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '未操作者 - 未完成操作的责任人姓名',
  `archive_date` date NULL DEFAULT NULL COMMENT '归档日期 - 记录最终归档的日期',
  `process_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '流程编号 - 唯一标识流程的编号（非空，核心字段）',
  `project_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '项目号 - 关联的项目编号',
  `vehicle_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '车号 - 关联的车辆编号（如适用）',
  `creator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '创建人 - 记录创建者姓名',
  `create_division` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '创建分部 - 创建人所属的分部',
  `create_department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '创建部门 - 创建人所属的部门',
  `occurrence_division` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '发生分部 - 不合格品发生的分部',
  `occurrence_department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '发生部门 - 不合格品发生的部门',
  `responsibility_division` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '责任分部 - 承担责任的分部',
  `responsibility_department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '责任部门 - 承担责任的部门',
  `review_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '评审级别 - 不合格品评审的级别（如：一级、二级）',
  `defective_product_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '不合格品名称 - 不合格品的具体名称',
  `product_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '产品编号 - 不合格品对应的产品编号',
  `occurrence_date` date NULL DEFAULT NULL COMMENT '发生日期 - 不合格品发现的日期',
  `quantity` int(11) NULL DEFAULT 0 COMMENT '数量 - 不合格品的数量（默认0，非负整数）',
  `vehicle_model` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所属车型 - 关联的车型（如适用）',
  `drawing_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '图号 - 产品对应的图纸编号',
  `occurrence_stage` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '发生阶段 - 不合格品发生的生产/使用阶段（如：生产中、安装后）',
  `finished_product_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所属成品名称 - 不合格品所属的成品名称',
  `defective_status_desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '产品不合格状态描述 - 详细描述不合格的具体情况（长文本）',
  `disposal_rework` tinyint(1) NULL DEFAULT 0 COMMENT '处置意见返工 - 是否选择返工处置（0=否，1=是）',
  `disposal_repair` tinyint(1) NULL DEFAULT 0 COMMENT '处置意见返修 - 是否选择返修处置（0=否，1=是）',
  `disposal_concession` tinyint(1) NULL DEFAULT 0 COMMENT '处置意见让步 - 是否选择让步接收（0=否，1=是）',
  `disposal_scrap` tinyint(1) NULL DEFAULT 0 COMMENT '处置意见报废 - 是否选择报废处置（0=否，1=是）',
  `disposal_reject` tinyint(1) NULL DEFAULT 0 COMMENT '处置意见拒收 - 是否选择拒收处置（0=否，1=是）',
  `require_corrective_action` tinyint(1) NULL DEFAULT 0 COMMENT '是否要求制定纠正措施 - 是否需要制定纠正措施（0=否，1=是）',
  `rework_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '返工处理人 - 负责返工的操作人员',
  `repair_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '返修处理人 - 负责返修的操作人员',
  `concession_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '让步处理人 - 负责让步流程的处理人',
  `scrap_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '报废处理人 - 负责报废流程的处理人',
  `reject_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '拒收处理人 - 负责拒收流程的处理人',
  `concession_approver` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '让步审批领导 - 审批让步申请的领导',
  `corrective_action_operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '纠正措施处理人 - 负责制定/执行纠正措施的人',
  `corrective_action_complete_date` date NULL DEFAULT NULL COMMENT '纠正措施完成时间 - 纠正措施执行完成的日期',
  `rework_result` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '返工处置结果 - 返工后的结果（如：合格、仍不合格）',
  `rework_others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '返工其他 - 返工相关的补充说明（长文本）',
  `repair_result` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '返修处置结果 - 返修后的结果',
  `repair_others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '返修其他 - 返修相关的补充说明',
  `concession_result` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '让步处置结果 - 让步申请的处理结果',
  `concession_others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '让步其他 - 让步相关的补充说明',
  `scrap_result` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '报废处置结果 - 报废流程的处理结果',
  `scrap_others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '报废其他 - 报废相关的补充说明',
  `reject_result` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '拒收处置结果 - 拒收流程的处理结果',
  `reject_others` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '拒收其他 - 拒收相关的补充说明',
  `problem_qualification` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '问题定性 - 对不合格问题的定性（如：严重、一般、轻微）',
  `supplier_full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '供应商全称 - 关联供应商的完整名称（如为外购件）',
  `problem_category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '问题分类 - 不合格问题的大类（如：质量问题、工艺问题）',
  `problem_subcategory` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '问题分类细分 - 问题分类的细分项（如：尺寸偏差、表面缺陷）',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '物料编码 - 不合格品对应的物料编码',
  `remarks` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '备注 - 其他需要补充的说明信息（长文本）',
  `quality_staff` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '质量人员 - 负责质量检查的人员',
  `problem_responsible_person` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '问题责任人 - 对不合格问题承担主要责任的人',
  `disposal_summary` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '处置意见汇总 - 所有处置意见的汇总说明',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间 - 自动生成，无需手动填写',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间 - 自动更新，无需手动填写',
  PRIMARY KEY (`process_no`) USING BTREE,
  INDEX `idx_project_no`(`project_no` ASC) USING BTREE,
  INDEX `idx_vehicle_no`(`vehicle_no` ASC) USING BTREE,
  INDEX `idx_occurrence_date`(`occurrence_date` ASC) USING BTREE,
  INDEX `idx_supplier_full_name`(`supplier_full_name` ASC) USING BTREE,
  INDEX `idx_create_date`(`create_date` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '不合格品处理记录表（jgjncr）- 基于Excel Sheet2字段创建，用于记录不合格品的发现、处置、跟踪全流程信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of jgjncr
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
