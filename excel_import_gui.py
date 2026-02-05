#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件导入GUI界面
使用PySide6创建可视化界面，支持用户选择任意位置的Excel文件进行导入
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QCheckBox, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QFont

# 添加项目路径以便导入数据处理模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from datadeal.simple_datadeal import process_single_file, read_excel_data
    IMPORT_AVAILABLE = True
except ImportError as e:
    print(f"导入数据处理模块失败: {e}")
    IMPORT_AVAILABLE = False

class ImportWorker(QThread):
    """导入工作线程"""
    progress_updated = Signal(int)  # 进度更新信号
    log_message = Signal(str)       # 日志消息信号
    import_finished = Signal(dict)  # 导入完成信号
    
    def __init__(self, file_path, overwrite=False):
        super().__init__()
        self.file_path = file_path
        self.overwrite = overwrite
    
    def run(self):
        try:
            self.log_message.emit(f"开始处理文件: {os.path.basename(self.file_path)}")
            self.progress_updated.emit(20)
            
            # 调用数据处理函数
            result = process_single_file(self.file_path, self.overwrite)
            
            self.progress_updated.emit(80)
            self.log_message.emit(f"处理完成: {result.get('message', '导入完成')}")
            self.progress_updated.emit(100)
            
            self.import_finished.emit(result)
            
        except Exception as e:
            error_msg = f"导入过程中发生错误: {str(e)}\n{traceback.format_exc()}"
            self.log_message.emit(error_msg)
            self.import_finished.emit({"success": False, "message": str(e)})

class PreviewWorker(QThread):
    """文件预览工作线程"""
    preview_ready = Signal(list, dict)  # 预览数据准备就绪信号
    error_occurred = Signal(str)        # 错误信号
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        try:
            # 读取文件数据
            data = read_excel_data(self.file_path)
            if not data:
                self.error_occurred.emit("无法读取文件数据")
                return
            
            # 分析文件信息
            file_info = {
                'filename': os.path.basename(self.file_path),
                'rows': len(data),
                'columns': len(data[0]) if data else 0,
                'size': os.path.getsize(self.file_path)
            }
            
            self.preview_ready.emit(data[:20], file_info)  # 只预览前20行
            
        except Exception as e:
            self.error_occurred.emit(f"预览文件时出错: {str(e)}")

class ExcelImportGUI(QMainWindow):
    """Excel导入图形界面主窗口"""
    
    def __init__(self):
        super().__init__()
        self.selected_files = []  # 选中的文件列表
        self.current_preview_data = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("项目管理系统 - Excel数据导入工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 导入标签页
        import_tab = self.create_import_tab()
        tab_widget.addTab(import_tab, "文件导入")
        
        # 预览标签页
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "数据预览")
        
        # 日志标签页
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "导入日志")
        
        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
    def create_import_tab(self):
        """创建导入标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        # 文件选择按钮和显示
        file_select_layout = QHBoxLayout()
        self.select_files_btn = QPushButton("选择Excel文件")
        self.select_files_btn.setIcon(QIcon())  # 可以添加图标
        self.clear_files_btn = QPushButton("清空列表")
        self.files_label = QLabel("未选择文件")
        self.files_label.setStyleSheet("color: gray;")
        
        file_select_layout.addWidget(self.select_files_btn)
        file_select_layout.addWidget(self.clear_files_btn)
        file_select_layout.addStretch()
        file_select_layout.addWidget(self.files_label)
        
        file_layout.addLayout(file_select_layout)
        
        # 文件列表显示
        self.files_list = QTextEdit()
        self.files_list.setMaximumHeight(100)
        self.files_list.setReadOnly(True)
        file_layout.addWidget(self.files_list)
        
        layout.addWidget(file_group)
        
        # 导入选项区域
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout(options_group)
        
        # 覆盖选项
        self.overwrite_checkbox = QCheckBox("覆盖已有数据")
        self.overwrite_checkbox.setChecked(False)
        options_layout.addWidget(self.overwrite_checkbox)
        
        # 导入按钮
        self.import_btn = QPushButton("开始导入")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.import_btn.setMinimumHeight(40)
        options_layout.addWidget(self.import_btn)
        
        layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.file_count_label = QLabel("文件数量: 0")
        self.success_count_label = QLabel("成功: 0")
        self.failed_count_label = QLabel("失败: 0")
        
        stats_layout.addWidget(self.file_count_label)
        stats_layout.addWidget(self.success_count_label)
        stats_layout.addWidget(self.failed_count_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return widget
    
    def create_preview_tab(self):
        """创建预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 预览控制区域
        control_layout = QHBoxLayout()
        self.preview_file_btn = QPushButton("预览选中文件")
        self.refresh_preview_btn = QPushButton("刷新预览")
        
        control_layout.addWidget(self.preview_file_btn)
        control_layout.addWidget(self.refresh_preview_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 文件信息显示
        info_layout = QHBoxLayout()
        self.file_info_label = QLabel("请选择文件进行预览")
        info_layout.addWidget(self.file_info_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # 数据表格
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f0f0f0;
                background-color: white;
            }
        """)
        
        layout.addWidget(self.preview_table)
        
        return widget
    
    def create_log_tab(self):
        """创建日志标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志控制按钮
        log_control_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("清空日志")
        self.save_log_btn = QPushButton("保存日志")
        self.auto_scroll_checkbox = QCheckBox("自动滚动")
        self.auto_scroll_checkbox.setChecked(True)
        
        log_control_layout.addWidget(self.clear_log_btn)
        log_control_layout.addWidget(self.save_log_btn)
        log_control_layout.addWidget(self.auto_scroll_checkbox)
        log_control_layout.addStretch()
        
        layout.addLayout(log_control_layout)
        
        # 日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        
        # 设置日志显示样式
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        
        layout.addWidget(self.log_display)
        
        return widget
    
    def setup_connections(self):
        """设置信号连接"""
        # 文件选择按钮
        self.select_files_btn.clicked.connect(self.select_files)
        self.clear_files_btn.clicked.connect(self.clear_files)
        
        # 导入按钮
        self.import_btn.clicked.connect(self.start_import)
        
        # 预览按钮
        self.preview_file_btn.clicked.connect(self.preview_selected_file)
        self.refresh_preview_btn.clicked.connect(self.refresh_preview)
        
        # 日志按钮
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)
    
    def select_files(self):
        """选择Excel文件"""
        file_filter = "Excel Files (*.xlsx *.xls *.csv);;All Files (*)"
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择Excel文件",
            "",
            file_filter
        )
        
        if files:
            self.selected_files = files
            self.update_files_display()
            self.log_message(f"选择了 {len(files)} 个文件")
    
    def clear_files(self):
        """清空文件列表"""
        self.selected_files = []
        self.files_list.clear()
        self.files_label.setText("未选择文件")
        self.files_label.setStyleSheet("color: gray;")
        self.log_message("已清空文件列表")
    
    def update_files_display(self):
        """更新文件显示"""
        if self.selected_files:
            file_text = "\n".join([f"• {os.path.basename(f)}" for f in self.selected_files])
            self.files_list.setPlainText(file_text)
            self.files_label.setText(f"已选择 {len(self.selected_files)} 个文件")
            self.files_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.files_list.clear()
            self.files_label.setText("未选择文件")
            self.files_label.setStyleSheet("color: gray;")
    
    def start_import(self):
        """开始导入"""
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择要导入的文件！")
            return
        
        if not IMPORT_AVAILABLE:
            QMessageBox.critical(self, "错误", "数据处理模块不可用，请检查依赖！")
            return
        
        # 确认导入
        reply = QMessageBox.question(
            self,
            "确认导入",
            f"确定要导入 {len(self.selected_files)} 个文件吗？\n"
            f"覆盖模式: {'开启' if self.overwrite_checkbox.isChecked() else '关闭'}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.import_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 重置统计
            self.success_count = 0
            self.failed_count = 0
            self.update_stats()
            
            # 开始导入第一个文件
            self.current_file_index = 0
            self.import_next_file()
    
    def import_next_file(self):
        """导入下一个文件"""
        if self.current_file_index >= len(self.selected_files):
            # 所有文件导入完成
            self.import_completed()
            return
        
        file_path = self.selected_files[self.current_file_index]
        self.log_message(f"[{self.current_file_index + 1}/{len(self.selected_files)}] "
                        f"开始导入: {os.path.basename(file_path)}")
        
        # 创建并启动导入工作线程
        self.worker = ImportWorker(file_path, self.overwrite_checkbox.isChecked())
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.log_message)
        self.worker.import_finished.connect(self.on_import_finished)
        self.worker.start()
    
    def on_import_finished(self, result):
        """导入完成回调"""
        if result.get('success', False):
            self.success_count += 1
            self.log_message(f"✓ 导入成功: {result.get('message', '完成')}")
        else:
            self.failed_count += 1
            self.log_message(f"✗ 导入失败: {result.get('message', '未知错误')}")
        
        self.update_stats()
        self.current_file_index += 1
        self.import_next_file()
    
    def import_completed(self):
        """所有文件导入完成"""
        self.import_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 显示完成消息
        msg = f"导入完成！\n成功: {self.success_count} 个文件\n失败: {self.failed_count} 个文件"
        if self.failed_count == 0:
            QMessageBox.information(self, "导入完成", msg)
        else:
            QMessageBox.warning(self, "导入完成", msg)
        
        self.log_message("=" * 50)
        self.log_message(msg)
        self.log_message("=" * 50)
    
    def preview_selected_file(self):
        """预览选中的文件"""
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择要预览的文件！")
            return
        
        # 预览第一个选中的文件
        file_path = self.selected_files[0]
        self.preview_file(file_path)
    
    def preview_file(self, file_path):
        """预览指定文件"""
        self.log_message(f"正在预览文件: {os.path.basename(file_path)}")
        
        # 创建并启动预览工作线程
        self.preview_worker = PreviewWorker(file_path)
        self.preview_worker.preview_ready.connect(self.display_preview)
        self.preview_worker.error_occurred.connect(self.preview_error)
        self.preview_worker.start()
    
    def display_preview(self, data, file_info):
        """显示预览数据"""
        # 更新文件信息
        size_mb = file_info['size'] / (1024 * 1024)
        info_text = (f"文件: {file_info['filename']} | "
                    f"行数: {file_info['rows']} | "
                    f"列数: {file_info['columns']} | "
                    f"大小: {size_mb:.2f} MB")
        self.file_info_label.setText(info_text)
        
        # 显示数据表格
        if data:
            # 获取列名
            columns = list(data[0].keys()) if data else []
            
            # 设置表格行列数
            self.preview_table.setRowCount(len(data))
            self.preview_table.setColumnCount(len(columns))
            self.preview_table.setHorizontalHeaderLabels(columns)
            
            # 填充数据
            for row, record in enumerate(data):
                for col, key in enumerate(columns):
                    value = record.get(key, "")
                    item = QTableWidgetItem(str(value))
                    self.preview_table.setItem(row, col, item)
            
            # 调整列宽
            self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
            self.log_message(f"预览完成: 显示 {len(data)} 行数据，{len(columns)} 列")
        else:
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.log_message("预览数据为空")
    
    def preview_error(self, error_msg):
        """预览错误处理"""
        QMessageBox.critical(self, "预览错误", error_msg)
        self.log_message(f"预览错误: {error_msg}")
    
    def refresh_preview(self):
        """刷新预览"""
        if self.selected_files:
            self.preview_selected_file()
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.selected_files)
        self.file_count_label.setText(f"文件数量: {total}")
        self.success_count_label.setText(f"成功: {self.success_count}")
        self.failed_count_label.setText(f"失败: {self.failed_count}")
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.log_display.append(formatted_message)
        
        # 自动滚动到底部
        if self.auto_scroll_checkbox.isChecked():
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        # 更新状态栏
        self.status_bar.showMessage(message[:50] + "..." if len(message) > 50 else message)
    
    def clear_log(self):
        """清空日志"""
        self.log_display.clear()
        self.status_bar.showMessage("日志已清空")
    
    def save_log(self):
        """保存日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存日志文件",
            f"import_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "成功", f"日志已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Excel导入工具")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("项目管理系统")
    
    # 创建并显示主窗口
    window = ExcelImportGUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()