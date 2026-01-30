/*
 Navicat Premium Data Transfer

 Source Server         : lcoa
 Source Server Type    : MySQL
 Source Server Version : 80013 (8.0.13)
 Source Host           : localhost:3306
 Source Schema         : jgj-project

 Target Server Type    : MySQL
 Target Server Version : 80013 (8.0.13)
 File Encoding         : 65001

 Date: 28/01/2026 08:23:28
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for projects
-- ----------------------------
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects`  (
  `project_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  `project_serial_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '项目序号',
  `project_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目名称',
  `project_manager` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '项目经理',
  `planned_start_date` date NULL DEFAULT NULL COMMENT '预计开始时间',
  `planned_end_date` date NULL DEFAULT NULL COMMENT '预计完成时间',
  `actual_start_date` datetime NULL DEFAULT NULL COMMENT '实际开始时间',
  `actual_end_date` datetime NULL DEFAULT NULL COMMENT '实际完成时间',
  `project_status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '项目状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`project_id`) USING BTREE,
  INDEX `idx_project_serial`(`project_serial_number` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '项目信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of projects
-- ----------------------------
INSERT INTO `projects` VALUES (1, NULL, '1', '阳绪文', '2026-01-04', '2026-02-10', '2026-01-04 00:00:00', '2026-01-18 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (2, NULL, '川藏制动柜项目计划', '阳绪文', '2025-12-26', '2026-01-15', '2025-12-26 00:00:00', '2026-01-06 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (3, NULL, '川藏线动力电池柜项目计划', '张俊杰', '2025-12-20', '2026-01-15', '2025-12-20 00:00:00', '2026-01-04 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (4, NULL, '川藏线网侧柜项目计划', '张俊杰', '2025-12-05', '2026-01-08', '2025-12-05 00:00:00', '2026-01-14 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (5, NULL, '川藏线蓄电池柜项目计划', '阳绪文', '2025-12-09', '2026-01-15', '2025-12-09 00:00:00', '2026-01-10 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (6, NULL, '川藏线风源柜项目计划', '张俊杰', '2025-12-26', '2026-01-20', '2025-12-26 00:00:00', '2026-01-14 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (7, NULL, '朔黄制动柜项目计划', '阳绪文', '2025-12-29', '2026-01-20', '2025-12-29 00:00:00', '2026-01-06 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (8, NULL, '马来西亚3CS蓄电池箱项目计划', '阳绪文', '2025-12-01', '2025-12-31', '2025-12-01 00:00:00', '2026-01-09 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');
INSERT INTO `projects` VALUES (9, NULL, '马来西亚3CS锂电池柜项目计划', '阳绪文', '2025-12-12', '2025-12-31', '2025-12-12 00:00:00', '2026-01-19 00:00:00', '已完成', '2026-01-21 15:58:50', '2026-01-21 15:58:50');

SET FOREIGN_KEY_CHECKS = 1;
