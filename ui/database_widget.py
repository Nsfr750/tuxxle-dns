"""
Database management widget for DNS Server
"""

import logging
from pathlib import Path
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QPushButton, QLabel, QMessageBox, QProgressBar, QTextEdit,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core.dns_server import DNSServer
from core.dns_records import DNSRecord, DNSRecordType

class DatabaseWidget(QWidget):
    """Widget for database management and statistics"""
    
    def __init__(self, dns_server: DNSServer):
        super().__init__()
        self.dns_server = dns_server
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._refresh_database_info()
        self._setup_timer()
    
    def _setup_ui(self):
        """Setup the database widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Database Management")
        title_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Statistics and controls
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Records table
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with statistics and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Database statistics
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QFormLayout(stats_group)
        
        self.total_records_label = QLabel("0")
        stats_layout.addRow("Total Records:", self.total_records_label)
        
        self.database_size_label = QLabel("0 KB")
        stats_layout.addRow("Database Size:", self.database_size_label)
        
        self.latest_record_label = QLabel("None")
        stats_layout.addRow("Latest Record:", self.latest_record_label)
        
        layout.addWidget(stats_group)
        
        # Records by type
        type_stats_group = QGroupBox("Records by Type")
        type_stats_layout = QVBoxLayout(type_stats_group)
        
        self.type_stats_text = QTextEdit()
        self.type_stats_text.setReadOnly(True)
        self.type_stats_text.setMaximumHeight(150)
        type_stats_layout.addWidget(self.type_stats_text)
        
        layout.addWidget(type_stats_group)
        
        # Database operations
        operations_group = QGroupBox("Database Operations")
        operations_layout = QVBoxLayout(operations_group)
        
        # Backup button
        self.backup_button = QPushButton("Backup Database")
        self.backup_button.clicked.connect(self._backup_database)
        operations_layout.addWidget(self.backup_button)
        
        # Restore button
        self.restore_button = QPushButton("Restore Database")
        self.restore_button.clicked.connect(self._restore_database)
        operations_layout.addWidget(self.restore_button)
        
        # Clear all button
        self.clear_button = QPushButton("Clear All Records")
        self.clear_button.clicked.connect(self._clear_database)
        self.clear_button.setStyleSheet("background-color: #ff6b6b; color: white;")
        operations_layout.addWidget(self.clear_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_database_info)
        operations_layout.addWidget(self.refresh_button)
        
        layout.addWidget(operations_group)
        
        layout.addStretch()
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with records table"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Search controls
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or value...")
        self.search_edit.textChanged.connect(self._search_records)
        search_layout.addWidget(self.search_edit)
        
        # Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types"] + [t.name for t in DNSRecordType])
        self.type_filter.currentTextChanged.connect(self._filter_by_type)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # Records table
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels([
            "Domain Name", "Type", "Value", "TTL", "Updated"
        ])
        
        # Setup table properties
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.records_table)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)
        
        return panel
    
    def _setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._refresh_database_info)
        self.update_timer.start(10000)  # Update every 10 seconds
    
    def _refresh_database_info(self):
        """Refresh database statistics and records"""
        try:
            # Get statistics
            stats = self.dns_server.database.get_statistics()
            
            # Update statistics labels
            self.total_records_label.setText(str(stats.get('total_records', 0)))
            
            # Database size
            size_bytes = stats.get('database_size', 0)
            if size_bytes > 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            elif size_bytes > 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            else:
                size_str = f"{size_bytes} bytes"
            self.database_size_label.setText(size_str)
            
            # Latest record
            latest = stats.get('latest_record')
            if latest:
                self.latest_record_label.setText(f"{latest[0]} ({latest[1]})")
            else:
                self.latest_record_label.setText("None")
            
            # Records by type
            records_by_type = stats.get('records_by_type', {})
            type_text = ""
            for record_type, count in records_by_type.items():
                type_text += f"{record_type}: {count}\n"
            self.type_stats_text.setText(type_text or "No records")
            
            # Load records table
            self._load_records_table()
            
        except Exception as e:
            self.logger.error(f"Error refreshing database info: {e}")
            self.status_label.setText(f"Error: {e}")
    
    def _load_records_table(self, records: List[DNSRecord] = None):
        """Load records into table"""
        try:
            if records is None:
                records = self.dns_server.database.list_records()
            
            self.records_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                # Domain name
                self.records_table.setItem(row, 0, QTableWidgetItem(record.name))
                
                # Record type
                self.records_table.setItem(row, 1, QTableWidgetItem(record.record_type.name))
                
                # Value
                self.records_table.setItem(row, 2, QTableWidgetItem(record.value))
                
                # TTL
                self.records_table.setItem(row, 3, QTableWidgetItem(str(record.ttl)))
                
                # Updated time (placeholder - would need to add timestamp to database)
                self.records_table.setItem(row, 4, QTableWidgetItem("N/A"))
            
            self.status_label.setText(f"Showing {len(records)} records")
            
        except Exception as e:
            self.logger.error(f"Error loading records table: {e}")
            self.status_label.setText(f"Error loading records: {e}")
    
    def _search_records(self):
        """Search records"""
        query = self.search_edit.text().strip()
        if not query:
            self._load_records_table()
        else:
            try:
                records = self.dns_server.database.search_records(query)
                self._load_records_table(records)
            except Exception as e:
                self.logger.error(f"Error searching records: {e}")
                self.status_label.setText(f"Search error: {e}")
    
    def _filter_by_type(self):
        """Filter records by type"""
        type_text = self.type_filter.currentText()
        if type_text == "All Types":
            self._load_records_table()
        else:
            try:
                record_type = DNSRecordType[type_text]
                records = self.dns_server.database.get_records_by_type(record_type)
                self._load_records_table(records)
            except Exception as e:
                self.logger.error(f"Error filtering by type: {e}")
                self.status_label.setText(f"Filter error: {e}")
    
    def _backup_database(self):
        """Backup database"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Backup Database", f"dns_backup_{Path().cwd().name}.db",
                "SQLite Database (*.db);;All Files (*)"
            )
            
            if file_path:
                if self.dns_server.database.backup_database(file_path):
                    QMessageBox.information(self, "Success", f"Database backed up to:\n{file_path}")
                    self.status_label.setText(f"Backup created: {Path(file_path).name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to backup database")
                    
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")
    
    def _restore_database(self):
        """Restore database from backup"""
        try:
            reply = QMessageBox.question(
                self, 'Confirm Restore',
                'This will replace all current records. Continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                file_path, _ = QFileDialog.getOpenFileName(
                    self, "Restore Database", "",
                    "SQLite Database (*.db);;All Files (*)"
                )
                
                if file_path:
                    if self.dns_server.database.restore_database(file_path):
                        # Reload records from database
                        self.dns_server._load_records_from_database()
                        self._refresh_database_info()
                        
                        QMessageBox.information(self, "Success", f"Database restored from:\n{file_path}")
                        self.status_label.setText(f"Database restored: {Path(file_path).name}")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to restore database")
                        
        except Exception as e:
            self.logger.error(f"Error restoring database: {e}")
            QMessageBox.critical(self, "Error", f"Restore failed: {e}")
    
    def _clear_database(self):
        """Clear all records from database"""
        try:
            reply = QMessageBox.question(
                self, 'Confirm Clear',
                'This will delete ALL DNS records permanently. Continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.dns_server.database.clear_all_records():
                    # Clear in-memory cache
                    self.dns_server.records.clear()
                    
                    # Reload default records
                    self.dns_server._load_default_records()
                    
                    self._refresh_database_info()
                    
                    QMessageBox.information(self, "Success", "All records cleared from database")
                    self.status_label.setText("Database cleared")
                else:
                    QMessageBox.critical(self, "Error", "Failed to clear database")
                    
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")
            QMessageBox.critical(self, "Error", f"Clear failed: {e}")
