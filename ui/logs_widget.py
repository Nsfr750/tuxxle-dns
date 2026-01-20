"""
Logs widget for displaying DNS server logs
"""

import logging
from datetime import datetime
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox,
    QPushButton, QLabel, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor, QColor

class LogMonitorThread(QThread):
    """Thread for monitoring log file changes"""
    new_log_entry = Signal(str, str)  # level, message
    
    def __init__(self, log_file: str):
        super().__init__()
        self.log_file = log_file
        self.running = False
        self.last_position = 0
    
    def run(self):
        """Monitor log file for changes"""
        self.running = True
        
        while self.running:
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()
                    
                    for line in new_lines:
                        if line.strip():
                            # Parse log level from line
                            level = "INFO"
                            if "DEBUG" in line:
                                level = "DEBUG"
                            elif "WARNING" in line:
                                level = "WARNING"
                            elif "ERROR" in line:
                                level = "ERROR"
                            elif "CRITICAL" in line:
                                level = "CRITICAL"
                            
                            self.new_log_entry.emit(level, line.strip())
                    
                    self.last_position = f.tell()
                
                self.msleep(500)  # Check every 500ms
                
            except FileNotFoundError:
                self.msleep(1000)  # Wait longer if file doesn't exist
            except Exception:
                self.msleep(1000)
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.wait()

class LogsWidget(QWidget):
    """Widget for displaying DNS server logs"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.log_entries: List[tuple] = []  # List of (timestamp, level, message)
        self.max_entries = 1000
        
        self._setup_ui()
        self._setup_log_monitor()
    
    def _setup_ui(self):
        """Setup the logs widget UI"""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("Server Logs")
        title_label.setFont(QFont("", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Log level filter
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.setCurrentText("INFO")
        self.level_filter.currentTextChanged.connect(self._filter_logs)
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self.level_filter)
        
        # Auto-scroll checkbox
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        header_layout.addWidget(self.autoscroll_check)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_logs)
        header_layout.addWidget(self.clear_button)
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._export_logs)
        header_layout.addWidget(self.export_button)
        
        layout.addWidget(header_frame)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.log_display)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.entry_count_label = QLabel("0 entries")
        status_layout.addWidget(self.entry_count_label)
        
        layout.addLayout(status_layout)
    
    def _setup_log_monitor(self):
        """Setup log file monitoring"""
        self.log_monitor = LogMonitorThread("dns_server.log")
        self.log_monitor.new_log_entry.connect(self._add_log_entry)
        self.log_monitor.start()
    
    def _add_log_entry(self, level: str, message: str):
        """Add a log entry to the display"""
        # Store entry
        timestamp = datetime.now()
        self.log_entries.append((timestamp, level, message))
        
        # Limit entries
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop(0)
        
        # Update display if not filtered out
        if self._should_show_level(level):
            self._append_log_display(timestamp, level, message)
        
        # Update status
        self.entry_count_label.setText(f"{len(self.log_entries)} entries")
    
    def _append_log_display(self, timestamp, level: str, message: str):
        """Append log entry to display"""
        # Format timestamp
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Color based on level
        color = {
            "DEBUG": "#888888",
            "INFO": "#00ff00",
            "WARNING": "#ffff00",
            "ERROR": "#ff6600",
            "CRITICAL": "#ff0000"
        }.get(level, "#ffffff")
        
        # Format message
        formatted_message = f'<span style="color: #888888">[{time_str}]</span> <span style="color: {color}; font-weight: bold;">{level}:</span> {message}<br>'
        
        # Add to display
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(formatted_message)
        
        # Auto-scroll if enabled
        if self.autoscroll_check.isChecked():
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _should_show_level(self, level: str) -> bool:
        """Check if log level should be shown based on filter"""
        filter_level = self.level_filter.currentText()
        if filter_level == "ALL":
            return True
        
        level_priority = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }
        
        return level_priority.get(level, 1) >= level_priority.get(filter_level, 1)
    
    def _filter_logs(self):
        """Filter logs based on selected level"""
        self.log_display.clear()
        
        for timestamp, level, message in self.log_entries:
            if self._should_show_level(level):
                self._append_log_display(timestamp, level, message)
    
    def _clear_logs(self):
        """Clear all log entries"""
        self.log_entries.clear()
        self.log_display.clear()
        self.entry_count_label.setText("0 entries")
        self.status_label.setText("Logs cleared")
    
    def _export_logs(self):
        """Export logs to file"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", f"dns_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for timestamp, level, message in self.log_entries:
                        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{time_str}] {level}: {message}\n")
                
                self.status_label.setText(f"Logs exported to {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            self.status_label.setText(f"Export failed: {e}")
    
    def add_log(self, level: str, message: str):
        """Manually add a log entry"""
        self._add_log_entry(level, message)
    
    def closeEvent(self, event):
        """Handle widget close event"""
        if hasattr(self, 'log_monitor'):
            self.log_monitor.stop()
        event.accept()
