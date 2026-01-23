#!/usr/bin/env python3
"""
Diagnostics dialog for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QProgressBar, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor
from core.server_diagnostics import ServerDiagnostics

class DiagnosticsWorker(QThread):
    """Worker thread for running diagnostics"""
    progress_updated = Signal(int, str)
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, dns_server, database):
        super().__init__()
        self.dns_server = dns_server
        self.database = database
        self.diagnostics = ServerDiagnostics()
    
    def run(self):
        """Run diagnostics in background thread"""
        try:
            self.progress_updated.emit(10, "Initializing diagnostics...")
            
            # Generate full report
            self.progress_updated.emit(30, "Collecting system information...")
            report = self.diagnostics.generate_full_report(self.dns_server, self.database)
            
            self.progress_updated.emit(100, "Diagnostics completed")
            self.finished.emit(report)
            
        except Exception as e:
            self.error.emit(f"Error running diagnostics: {str(e)}")

class DiagnosticsDialog(QDialog):
    """Diagnostics dialog window"""
    
    def __init__(self, parent=None, dns_server=None, database=None):
        super().__init__(parent)
        self.dns_server = dns_server
        self.database = database
        self.diagnostics = ServerDiagnostics()
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("Server Diagnostics")
        self.setModal(True)
        self.resize(900, 700)
        
        self._setup_ui()
        self._run_diagnostics()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("DNS Server Diagnostics")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Report tab
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.report_text, "Full Report")
        
        # Summary tab
        self.summary_tree = QTreeWidget()
        self.summary_tree.setHeaderLabels(["Category", "Item", "Value/Status"])
        self.tab_widget.addTab(self.summary_tree, "Summary")
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._run_diagnostics)
        button_layout.addWidget(self.refresh_button)
        
        # Export button
        self.export_button = QPushButton("Export Report")
        self.export_button.clicked.connect(self._export_report)
        button_layout.addWidget(self.export_button)
        
        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _run_diagnostics(self):
        """Run diagnostics"""
        # Disable buttons during run
        self.refresh_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)
        self.status_label.setText("Starting diagnostics...")
        
        # Clear previous results
        self.report_text.clear()
        self.summary_tree.clear()
        
        # Start worker thread
        self.worker = DiagnosticsWorker(self.dns_server, self.database)
        self.worker.progress_updated.connect(self._update_progress)
        self.worker.finished.connect(self._on_diagnostics_finished)
        self.worker.error.connect(self._on_diagnostics_error)
        self.worker.start()
    
    def _update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def _on_diagnostics_finished(self, report):
        """Handle diagnostics completion"""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Enable buttons
        self.refresh_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        
        # Display report
        self.report_text.setPlainText(report)
        
        # Populate summary tree
        self._populate_summary()
        
        self.logger.info("Diagnostics completed successfully")
    
    def _on_diagnostics_error(self, error_message):
        """Handle diagnostics error"""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        # Enable buttons
        self.refresh_button.setEnabled(True)
        self.export_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        
        # Show error
        self.report_text.setPlainText(f"Error running diagnostics:\n\n{error_message}")
        
        self.logger.error(f"Diagnostics error: {error_message}")
        QMessageBox.critical(self, "Diagnostics Error", f"Failed to run diagnostics:\n{error_message}")
    
    def _populate_summary(self):
        """Populate summary tree widget"""
        try:
            # System Information
            sys_item = QTreeWidgetItem(self.summary_tree, ["System Information", "", ""])
            sys_info = self.diagnostics.get_system_info()
            for key, value in sys_info.items():
                if key != "error":
                    QTreeWidgetItem(sys_item, ["", key.replace("_", " ").title(), str(value)])
            
            # Network Information
            net_item = QTreeWidgetItem(self.summary_tree, ["Network Information", "", ""])
            net_info = self.diagnostics.get_network_info()
            for key, value in net_info.items():
                if key != "error" and key != "interfaces":
                    QTreeWidgetItem(net_item, ["", key.replace("_", " ").title(), str(value)])
            
            # DNS Server Information
            dns_item = QTreeWidgetItem(self.summary_tree, ["DNS Server", "", ""])
            dns_info = self.diagnostics.get_dns_server_info(self.dns_server)
            for key, value in dns_info.items():
                if key != "error":
                    QTreeWidgetItem(dns_item, ["", key.replace("_", " ").title(), str(value)])
            
            # Database Information
            db_item = QTreeWidgetItem(self.summary_tree, ["Database", "", ""])
            db_info = self.diagnostics.get_database_info(self.database)
            for key, value in db_info.items():
                if key != "error":
                    QTreeWidgetItem(db_item, ["", key.replace("_", " ").title(), str(value)])
            
            # Connectivity Tests
            test_item = QTreeWidgetItem(self.summary_tree, ["Connectivity Tests", "", ""])
            tests = self.diagnostics.run_connectivity_tests()
            for test_name, result in tests.items():
                status = result.get("status", "UNKNOWN")
                QTreeWidgetItem(test_item, ["", test_name.replace("_", " ").title(), status])
            
            # Expand all items
            self.summary_tree.expandAll()
            
        except Exception as e:
            self.logger.error(f"Error populating summary: {e}")
    
    def _export_report(self):
        """Export diagnostics report to file"""
        try:
            from PySide6.QtWidgets import QFileDialog
            from datetime import datetime
            
            # Get file name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"diagnostics_report_{timestamp}.txt"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Diagnostics Report", default_name, "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                # Save report
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.report_text.toPlainText())
                
                QMessageBox.information(self, "Export Successful", f"Report exported to:\n{file_path}")
                self.logger.info(f"Diagnostics report exported to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export report:\n{str(e)}")
    
    def _copy_to_clipboard(self):
        """Copy report to clipboard"""
        try:
            from PySide6.QtWidgets import QApplication
            
            clipboard = QApplication.clipboard()
            clipboard.setText(self.report_text.toPlainText())
            
            QMessageBox.information(self, "Copy Successful", "Report copied to clipboard")
            self.logger.info("Diagnostics report copied to clipboard")
            
        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {e}")
            QMessageBox.critical(self, "Copy Error", f"Failed to copy report:\n{str(e)}")
