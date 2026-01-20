"""
Statistics widget for DNS Server
"""

import time
from typing import Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QGridLayout, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core.dns_server import DNSServer

class StatsWidget(QWidget):
    """Widget for displaying DNS server statistics"""
    
    def __init__(self, dns_server: DNSServer):
        super().__init__()
        self.dns_server = dns_server
        self.start_time = time.time()
        
        self._setup_ui()
        self._setup_timer()
    
    def _setup_ui(self):
        """Setup the statistics widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Server Statistics")
        title_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Main stats grid
        main_stats_group = QGroupBox("Server Status")
        main_stats_layout = QGridLayout(main_stats_group)
        
        # Server status
        self.server_status_label = QLabel("Stopped")
        self.server_status_label.setStyleSheet("font-weight: bold; color: red;")
        main_stats_layout.addWidget(QLabel("Server Status:"), 0, 0)
        main_stats_layout.addWidget(self.server_status_label, 0, 1)
        
        # Uptime
        self.uptime_label = QLabel("00:00:00")
        main_stats_layout.addWidget(QLabel("Uptime:"), 1, 0)
        main_stats_layout.addWidget(self.uptime_label, 1, 1)
        
        # Queries received
        self.queries_label = QLabel("0")
        main_stats_layout.addWidget(QLabel("Queries Received:"), 2, 0)
        main_stats_layout.addWidget(self.queries_label, 2, 1)
        
        # Responses sent
        self.responses_label = QLabel("0")
        main_stats_layout.addWidget(QLabel("Responses Sent:"), 3, 0)
        main_stats_layout.addWidget(self.responses_label, 3, 1)
        
        # Error rate
        self.error_rate_label = QLabel("0%")
        main_stats_layout.addWidget(QLabel("Error Rate:"), 4, 0)
        main_stats_layout.addWidget(self.error_rate_label, 4, 1)
        
        layout.addWidget(main_stats_group)
        
        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QGridLayout(perf_group)
        
        # Queries per second
        self.qps_label = QLabel("0.00")
        perf_layout.addWidget(QLabel("Queries/Second:"), 0, 0)
        perf_layout.addWidget(self.qps_label, 0, 1)
        
        # Average response time (placeholder - would need timing implementation)
        self.response_time_label = QLabel("N/A")
        perf_layout.addWidget(QLabel("Avg Response Time:"), 1, 0)
        perf_layout.addWidget(self.response_time_label, 1, 1)
        
        # Success rate
        self.success_rate_label = QLabel("100%")
        perf_layout.addWidget(QLabel("Success Rate:"), 2, 0)
        perf_layout.addWidget(self.success_rate_label, 2, 1)
        
        layout.addWidget(perf_group)
        
        # Progress bars
        progress_group = QGroupBox("Resource Usage")
        progress_layout = QVBoxLayout(progress_group)
        
        # Memory usage (placeholder)
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setFormat("0%")
        memory_layout.addWidget(self.memory_progress)
        progress_layout.addLayout(memory_layout)
        
        # Connection usage
        connections_layout = QHBoxLayout()
        connections_layout.addWidget(QLabel("Active Connections:"))
        self.connections_progress = QProgressBar()
        self.connections_progress.setRange(0, 100)
        self.connections_progress.setValue(0)
        self.connections_progress.setFormat("0/1000")
        connections_layout.addWidget(self.connections_progress)
        progress_layout.addLayout(connections_layout)
        
        layout.addWidget(progress_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_label = QLabel("No recent activity")
        self.activity_label.setWordWrap(True)
        self.activity_label.setStyleSheet("color: gray; font-size: 10px;")
        activity_layout.addWidget(self.activity_label)
        
        layout.addWidget(activity_group)
        
        layout.addStretch()
    
    def _setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
    
    def update_stats(self):
        """Update statistics display"""
        try:
            stats = self.dns_server.get_stats()
            
            # Update server status
            if self.dns_server.running:
                self.server_status_label.setText("Running")
                self.server_status_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.server_status_label.setText("Stopped")
                self.server_status_label.setStyleSheet("font-weight: bold; color: red;")
            
            # Update uptime
            if 'uptime' in stats:
                uptime_seconds = int(stats['uptime'])
                hours = uptime_seconds // 3600
                minutes = (uptime_seconds % 3600) // 60
                seconds = uptime_seconds % 60
                self.uptime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Update query counts
            queries = stats.get('queries_received', 0)
            responses = stats.get('responses_sent', 0)
            errors = stats.get('errors', 0)
            
            self.queries_label.setText(str(queries))
            self.responses_label.setText(str(responses))
            
            # Calculate and update error rate
            if queries > 0:
                error_rate = (errors / queries) * 100
                self.error_rate_label.setText(f"{error_rate:.2f}%")
                
                # Update success rate
                success_rate = ((queries - errors) / queries) * 100
                self.success_rate_label.setText(f"{success_rate:.2f}%")
            else:
                self.error_rate_label.setText("0%")
                self.success_rate_label.setText("100%")
            
            # Calculate queries per second
            if 'uptime' in stats and stats['uptime'] > 0:
                qps = queries / stats['uptime']
                self.qps_label.setText(f"{qps:.2f}")
            else:
                self.qps_label.setText("0.00")
            
            # Update activity log
            if queries > 0:
                self.activity_label.setText(
                    f"Last activity: {queries} queries processed, "
                    f"{responses} responses sent, {errors} errors"
                )
            
        except Exception as e:
            # Silently handle update errors to avoid spam
            pass
