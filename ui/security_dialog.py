#!/usr/bin/env python3
"""
Security management dialog for DNS Server Manager
"""

import logging
import time
from typing import Dict, List, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
    QGroupBox, QGridLayout, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QProgressBar, QFrame,
    QSplitter, QFormLayout, QSpinBox, QDoubleSpinBox, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor
from core.dnssec import DNSSECManager, DNSSECKey
from core.security import SecurityManager, SecurityEvent
from core.secure_config import SecureConfigManager

class SecurityWorker(QThread):
    """Worker thread for security operations"""
    progress_updated = Signal(int, str)
    finished = Signal(str, bool)
    error = Signal(str)
    
    def __init__(self, operation: str, manager, **kwargs):
        super().__init__()
        self.operation = operation
        self.manager = manager
        self.kwargs = kwargs
    
    def run(self):
        """Run security operation"""
        try:
            if self.operation == "generate_key":
                result = self._generate_key()
            elif self.operation == "sign_zone":
                result = self._sign_zone()
            elif self.operation == "rotate_keys":
                result = self._rotate_keys()
            elif self.operation == "load_audit_events":
                result = self._load_audit_events()
            else:
                result = "Unknown operation"
            
            self.finished.emit(result, True)
            
        except Exception as e:
            self.error.emit(f"Security operation failed: {str(e)}")
    
    def _generate_key(self):
        """Generate DNSSEC key"""
        self.progress_updated.emit(10, "Initializing key generation...")
        
        zone_name = self.kwargs.get('zone_name', 'example.com')
        key_type = self.kwargs.get('key_type', 'RSA')
        key_size = self.kwargs.get('key_size', 2048)
        
        self.progress_updated.emit(30, "Generating cryptographic key...")
        key_id = self.manager.create_zone_key(zone_name, key_type, key_size)
        
        self.progress_updated.emit(70, "Finalizing key...")
        
        self.progress_updated.emit(100, "Key generation completed")
        return f"DNSSEC key generated successfully: {key_id}"
    
    def _sign_zone(self):
        """Sign DNS zone"""
        self.progress_updated.emit(10, "Preparing zone signing...")
        
        zone_name = self.kwargs.get('zone_name', 'example.com')
        records = self.kwargs.get('records', [])
        
        self.progress_updated.emit(30, "Signing records...")
        signed_records = self.manager.sign_zone(zone_name, records)
        
        self.progress_updated.emit(70, "Creating signatures...")
        
        self.progress_updated.emit(100, "Zone signing completed")
        return f"Zone {zone_name} signed successfully with {len(signed_records)} records"
    
    def _rotate_keys(self):
        """Rotate DNSSEC keys"""
        self.progress_updated.emit(10, "Starting key rotation...")
        
        zone_name = self.kwargs.get('zone_name', 'example.com')
        
        self.progress_updated.emit(50, "Generating new key...")
        success = self.manager.rotate_keys(zone_name)
        
        self.progress_updated.emit(100, "Key rotation completed")
        return f"Key rotation completed for zone {zone_name}" if success else "Key rotation failed"
    
    def _load_audit_events(self):
        """Load audit events"""
        self.progress_updated.emit(10, "Loading audit events...")
        
        days = self.kwargs.get('days', 7)
        events = self.manager.query_events(days=days)
        
        self.progress_updated.emit(100, f"Loaded {len(events)} events")
        return events

class SecurityDialog(QDialog):
    """Security management dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.dnssec_manager = DNSSECManager()
        self.security_manager = SecurityManager()
        self.config_manager = SecureConfigManager()
        
        self.setWindowTitle("Security Management")
        self.setModal(True)
        self.resize(1000, 700)
        
        self._setup_ui()
        self._load_security_status()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_status)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("DNS Server Security Management")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self._setup_overview_tab()
        self._setup_dnssec_tab()
        self._setup_rate_limiting_tab()
        self._setup_ip_filtering_tab()
        self._setup_audit_tab()
        self._setup_config_tab()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Status")
        self.refresh_button.clicked.connect(self._refresh_status)
        button_layout.addWidget(self.refresh_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _setup_overview_tab(self):
        """Setup security overview tab"""
        overview_layout = QVBoxLayout()
        
        # Security status
        status_group = QGroupBox("Security Status")
        status_layout = QFormLayout()
        
        self.dnssec_status_label = QLabel("Disabled")
        self.rate_limiting_status_label = QLabel("Disabled")
        self.ip_filtering_status_label = QLabel("Disabled")
        self.audit_logging_status_label = QLabel("Disabled")
        
        status_layout.addRow("DNSSEC:", self.dnssec_status_label)
        status_layout.addRow("Rate Limiting:", self.rate_limiting_status_label)
        status_layout.addRow("IP Filtering:", self.ip_filtering_status_label)
        status_layout.addRow("Audit Logging:", self.audit_logging_status_label)
        
        status_group.setLayout(status_layout)
        overview_layout.addWidget(status_group)
        
        # Statistics
        stats_group = QGroupBox("Security Statistics")
        stats_layout = QGridLayout()
        
        self.total_queries_label = QLabel("0")
        self.blocked_queries_label = QLabel("0")
        self.active_ips_label = QLabel("0")
        self.blacklisted_ips_label = QLabel("0")
        
        stats_layout.addWidget(QLabel("Total Queries (24h):"), 0, 0)
        stats_layout.addWidget(self.total_queries_label, 0, 1)
        stats_layout.addWidget(QLabel("Blocked Queries (24h):"), 0, 2)
        stats_layout.addWidget(self.blocked_queries_label, 0, 3)
        stats_layout.addWidget(QLabel("Active IPs:"), 1, 0)
        stats_layout.addWidget(self.active_ips_label, 1, 1)
        stats_layout.addWidget(QLabel("Blacklisted IPs:"), 1, 2)
        stats_layout.addWidget(self.blacklisted_ips_label, 1, 3)
        
        stats_group.setLayout(stats_layout)
        overview_layout.addWidget(stats_group)
        
        # Recent events
        events_group = QGroupBox("Recent Security Events")
        events_layout = QVBoxLayout()
        
        self.recent_events_table = QTableWidget()
        self.recent_events_table.setColumnCount(5)
        self.recent_events_table.setHorizontalHeaderLabels(["Time", "Type", "Source IP", "Action", "Details"])
        self.recent_events_table.horizontalHeader().setStretchLastSection(True)
        self.recent_events_table.setMaximumHeight(200)
        events_layout.addWidget(self.recent_events_table)
        
        events_group.setLayout(events_layout)
        overview_layout.addWidget(events_group)
        
        overview_layout.addStretch()
        
        # Create widget for tab
        overview_widget = QFrame()
        overview_widget.setLayout(overview_layout)
        self.tab_widget.addTab(overview_widget, "Overview")
    
    def _setup_dnssec_tab(self):
        """Setup DNSSEC tab"""
        dnssec_layout = QVBoxLayout()
        
        # DNSSEC controls
        controls_group = QGroupBox("DNSSEC Controls")
        controls_layout = QGridLayout()
        
        # Enable/disable
        self.dnssec_enabled_check = QCheckBox("Enable DNSSEC")
        self.dnssec_enabled_check.toggled.connect(self._toggle_dnssec)
        controls_layout.addWidget(self.dnssec_enabled_check, 0, 0, 1, 2)
        
        # Key generation
        controls_layout.addWidget(QLabel("Zone Name:"), 1, 0)
        self.zone_name_edit = QLineEdit("example.com")
        controls_layout.addWidget(self.zone_name_edit, 1, 1)
        
        controls_layout.addWidget(QLabel("Key Type:"), 2, 0)
        self.key_type_combo = QComboBox()
        self.key_type_combo.addItems(["RSA", "ECDSA", "ED25519"])
        controls_layout.addWidget(self.key_type_combo, 2, 1)
        
        controls_layout.addWidget(QLabel("Key Size:"), 3, 0)
        self.key_size_spin = QSpinBox()
        self.key_size_spin.setRange(1024, 4096)
        self.key_size_spin.setValue(2048)
        self.key_size_spin.setSingleStep(512)
        controls_layout.addWidget(self.key_size_spin, 3, 1)
        
        generate_key_button = QPushButton("Generate Key")
        generate_key_button.clicked.connect(self._generate_dnssec_key)
        controls_layout.addWidget(generate_key_button, 4, 0)
        
        sign_zone_button = QPushButton("Sign Zone")
        sign_zone_button.clicked.connect(self._sign_zone)
        controls_layout.addWidget(sign_zone_button, 4, 1)
        
        rotate_keys_button = QPushButton("Rotate Keys")
        rotate_keys_button.clicked.connect(self._rotate_dnssec_keys)
        controls_layout.addWidget(rotate_keys_button, 5, 0, 1, 2)
        
        controls_group.setLayout(controls_layout)
        dnssec_layout.addWidget(controls_group)
        
        # Progress bar
        self.dnssec_progress_bar = QProgressBar()
        self.dnssec_progress_bar.setVisible(False)
        dnssec_layout.addWidget(self.dnssec_progress_bar)
        
        # DNS keys table
        keys_group = QGroupBox("DNSSEC Keys")
        keys_layout = QVBoxLayout()
        
        self.dnssec_keys_table = QTableWidget()
        self.dnssec_keys_table.setColumnCount(4)
        self.dnssec_keys_table.setHorizontalHeaderLabels(["Key ID", "Type", "Size", "Created"])
        self.dnssec_keys_table.horizontalHeader().setStretchLastSection(True)
        keys_layout.addWidget(self.dnssec_keys_table)
        
        keys_group.setLayout(keys_layout)
        dnssec_layout.addWidget(keys_group)
        
        dnssec_layout.addStretch()
        
        # Create widget for tab
        dnssec_widget = QFrame()
        dnssec_widget.setLayout(dnssec_layout)
        self.tab_widget.addTab(dnssec_widget, "DNSSEC")
    
    def _setup_rate_limiting_tab(self):
        """Setup rate limiting tab"""
        rate_layout = QVBoxLayout()
        
        # Rate limiting controls
        controls_group = QGroupBox("Rate Limiting Configuration")
        controls_layout = QFormLayout()
        
        self.rate_limiting_enabled_check = QCheckBox("Enable Rate Limiting")
        self.rate_limiting_enabled_check.toggled.connect(self._toggle_rate_limiting)
        controls_layout.addRow(self.rate_limiting_enabled_check)
        
        self.max_rps_spin = QSpinBox()
        self.max_rps_spin.setRange(1, 1000)
        self.max_rps_spin.setValue(100)
        controls_layout.addRow("Max Requests/Second:", self.max_rps_spin)
        
        self.max_rpm_spin = QSpinBox()
        self.max_rpm_spin.setRange(1, 10000)
        self.max_rpm_spin.setValue(1000)
        controls_layout.addRow("Max Requests/Minute:", self.max_rpm_spin)
        
        apply_rate_button = QPushButton("Apply Rate Limits")
        apply_rate_button.clicked.connect(self._apply_rate_limits)
        controls_layout.addRow("", apply_rate_button)
        
        controls_group.setLayout(controls_layout)
        rate_layout.addWidget(controls_group)
        
        # Rate limiting statistics
        stats_group = QGroupBox("Current Statistics")
        stats_layout = QFormLayout()
        
        self.active_ips_label = QLabel("0")
        self.requests_second_label = QLabel("0")
        self.requests_minute_label = QLabel("0")
        
        stats_layout.addRow("Active IPs:", self.active_ips_label)
        stats_layout.addRow("Requests/Second:", self.requests_second_label)
        stats_layout.addRow("Requests/Minute:", self.requests_minute_label)
        
        stats_group.setLayout(stats_layout)
        rate_layout.addWidget(stats_group)
        
        rate_layout.addStretch()
        
        # Create widget for tab
        rate_widget = QFrame()
        rate_widget.setLayout(rate_layout)
        self.tab_widget.addTab(rate_widget, "Rate Limiting")
    
    def _setup_ip_filtering_tab(self):
        """Setup IP filtering tab"""
        ip_layout = QVBoxLayout()
        
        # IP filtering controls
        controls_group = QGroupBox("IP Filtering Configuration")
        controls_layout = QFormLayout()
        
        self.ip_filtering_enabled_check = QCheckBox("Enable IP Filtering")
        self.ip_filtering_enabled_check.toggled.connect(self._toggle_ip_filtering)
        controls_layout.addRow(self.ip_filtering_enabled_check)
        
        # Whitelist
        whitelist_widget = QWidget()
        whitelist_layout = QHBoxLayout()
        
        self.whitelist_edit = QLineEdit()
        self.whitelist_edit.setPlaceholderText("IP or CIDR (e.g., 192.168.1.0/24)")
        whitelist_layout.addWidget(self.whitelist_edit)
        
        add_whitelist_button = QPushButton("Add to Whitelist")
        add_whitelist_button.clicked.connect(self._add_to_whitelist)
        whitelist_layout.addWidget(add_whitelist_button)
        
        whitelist_widget.setLayout(whitelist_layout)
        controls_layout.addRow("Whitelist:", whitelist_widget)
        
        # Blacklist
        blacklist_widget = QWidget()
        blacklist_layout = QHBoxLayout()
        
        self.blacklist_edit = QLineEdit()
        self.blacklist_edit.setPlaceholderText("IP or CIDR (e.g., 10.0.0.0/8)")
        blacklist_layout.addWidget(self.blacklist_edit)
        
        add_blacklist_button = QPushButton("Add to Blacklist")
        add_blacklist_button.clicked.connect(self._add_to_blacklist)
        blacklist_layout.addWidget(add_blacklist_button)
        
        blacklist_widget.setLayout(blacklist_layout)
        controls_layout.addRow("Blacklist:", blacklist_widget)
        
        controls_group.setLayout(controls_layout)
        ip_layout.addWidget(controls_group)
        
        # IP lists
        lists_splitter = QSplitter(Qt.Horizontal)
        
        # Whitelist table
        whitelist_group = QGroupBox("Whitelist")
        whitelist_table_layout = QVBoxLayout()
        
        self.whitelist_table = QTableWidget()
        self.whitelist_table.setColumnCount(2)
        self.whitelist_table.setHorizontalHeaderLabels(["IP/Range", "Type"])
        self.whitelist_table.horizontalHeader().setStretchLastSection(True)
        whitelist_table_layout.addWidget(self.whitelist_table)
        
        remove_whitelist_button = QPushButton("Remove Selected")
        remove_whitelist_button.clicked.connect(self._remove_from_whitelist)
        whitelist_table_layout.addWidget(remove_whitelist_button)
        
        whitelist_group.setLayout(whitelist_table_layout)
        lists_splitter.addWidget(whitelist_group)
        
        # Blacklist table
        blacklist_group = QGroupBox("Blacklist")
        blacklist_table_layout = QVBoxLayout()
        
        self.blacklist_table = QTableWidget()
        self.blacklist_table.setColumnCount(2)
        self.blacklist_table.setHorizontalHeaderLabels(["IP/Range", "Type"])
        self.blacklist_table.horizontalHeader().setStretchLastSection(True)
        blacklist_table_layout.addWidget(self.blacklist_table)
        
        remove_blacklist_button = QPushButton("Remove Selected")
        remove_blacklist_button.clicked.connect(self._remove_from_blacklist)
        blacklist_table_layout.addWidget(remove_blacklist_button)
        
        blacklist_group.setLayout(blacklist_table_layout)
        lists_splitter.addWidget(blacklist_group)
        
        ip_layout.addWidget(lists_splitter)
        
        # Create widget for tab
        ip_widget = QFrame()
        ip_widget.setLayout(ip_layout)
        self.tab_widget.addTab(ip_widget, "IP Filtering")
    
    def _setup_audit_tab(self):
        """Setup audit logging tab"""
        audit_layout = QVBoxLayout()
        
        # Audit controls
        controls_group = QGroupBox("Audit Logging Configuration")
        controls_layout = QFormLayout()
        
        self.audit_enabled_check = QCheckBox("Enable Audit Logging")
        self.audit_enabled_check.toggled.connect(self._toggle_audit_logging)
        controls_layout.addRow(self.audit_enabled_check)
        
        self.retention_days_spin = QSpinBox()
        self.retention_days_spin.setRange(1, 365)
        self.retention_days_spin.setValue(90)
        controls_layout.addRow("Log Retention (days):", self.retention_days_spin)
        
        apply_audit_button = QPushButton("Apply Settings")
        apply_audit_button.clicked.connect(self._apply_audit_settings)
        controls_layout.addRow("", apply_audit_button)
        
        controls_group.setLayout(controls_layout)
        audit_layout.addWidget(controls_group)
        
        # Audit events table
        events_group = QGroupBox("Security Events")
        events_layout = QVBoxLayout()
        
        # Filter controls
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItems(["All", "query_allowed", "ip_blocked", "rate_limit_exceeded"])
        filter_layout.addWidget(self.event_type_combo)
        
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["All", "INFO", "WARNING", "ERROR", "CRITICAL"])
        filter_layout.addWidget(self.severity_combo)
        
        refresh_events_button = QPushButton("Refresh")
        refresh_events_button.clicked.connect(self._refresh_audit_events)
        filter_layout.addWidget(refresh_events_button)
        
        export_events_button = QPushButton("Export")
        export_events_button.clicked.connect(self._export_audit_events)
        filter_layout.addWidget(export_events_button)
        
        filter_widget.setLayout(filter_layout)
        events_layout.addWidget(filter_widget)
        
        # Events table
        self.audit_events_table = QTableWidget()
        self.audit_events_table.setColumnCount(6)
        self.audit_events_table.setHorizontalHeaderLabels(["Time", "Type", "Source IP", "Query", "Action", "Severity"])
        self.audit_events_table.horizontalHeader().setStretchLastSection(True)
        events_layout.addWidget(self.audit_events_table)
        
        events_group.setLayout(events_layout)
        audit_layout.addWidget(events_group)
        
        # Create widget for tab
        audit_widget = QFrame()
        audit_widget.setLayout(audit_layout)
        self.tab_widget.addTab(audit_widget, "Audit Logging")
    
    def _setup_config_tab(self):
        """Setup secure configuration tab"""
        config_layout = QVBoxLayout()
        
        # Configuration management
        config_group = QGroupBox("Secure Configuration")
        config_layout_inner = QFormLayout()
        
        # Backup/Restore
        backup_button = QPushButton("Backup Configuration")
        backup_button.clicked.connect(self._backup_config)
        config_layout_inner.addRow("", backup_button)
        
        restore_button = QPushButton("Restore Configuration")
        restore_button.clicked.connect(self._restore_config)
        config_layout_inner.addRow("", restore_button)
        
        # Password change
        password_label = QLabel("Change Master Password:")
        config_layout_inner.addRow(password_label)
        
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.Password)
        config_layout_inner.addRow("Current:", self.current_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        config_layout_inner.addRow("New:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        config_layout_inner.addRow("Confirm:", self.confirm_password_edit)
        
        change_password_button = QPushButton("Change Password")
        change_password_button.clicked.connect(self._change_password)
        config_layout_inner.addRow("", change_password_button)
        
        # Integrity check
        integrity_button = QPushButton("Verify Configuration Integrity")
        integrity_button.clicked.connect(self._verify_integrity)
        config_layout_inner.addRow("", integrity_button)
        
        config_group.setLayout(config_layout_inner)
        config_layout.addWidget(config_group)
        
        # Configuration info
        info_group = QGroupBox("Configuration Information")
        info_layout = QFormLayout()
        
        self.config_hash_label = QLabel("")
        info_layout.addRow("Config Hash:", self.config_hash_label)
        
        self.last_backup_label = QLabel("Never")
        info_layout.addRow("Last Backup:", self.last_backup_label)
        
        self.integrity_status_label = QLabel("Unknown")
        info_layout.addRow("Integrity Status:", self.integrity_status_label)
        
        info_group.setLayout(info_layout)
        config_layout.addWidget(info_group)
        
        config_layout.addStretch()
        
        # Create widget for tab
        config_widget = QFrame()
        config_widget.setLayout(config_layout)
        self.tab_widget.addTab(config_widget, "Configuration")
    
    def _load_security_status(self):
        """Load current security status"""
        try:
            status = self.security_manager.get_security_status()
            
            # Update overview
            self.dnssec_status_label.setText("Enabled" if self.dnssec_manager.enabled else "Disabled")
            self.rate_limiting_status_label.setText("Enabled" if status["rate_limiter"]["max_rps"] > 0 else "Disabled")
            self.ip_filtering_status_label.setText("Enabled" if len(status["ip_filter"]["whitelist"]) > 0 or len(status["ip_filter"]["blacklist"]) > 0 else "Disabled")
            self.audit_logging_status_label.setText("Enabled")
            
            # Update statistics
            self.active_ips_label.setText(str(status["rate_limiter"]["active_ips"]))
            self.blacklisted_ips_label.setText(str(status["ip_filter"]["blacklist_count"]))
            
            # Update DNSSEC
            self.dnssec_enabled_check.setChecked(self.dnssec_manager.enabled)
            
            # Update rate limiting
            self.max_rps_spin.setValue(status["rate_limiter"]["max_rps"])
            self.max_rpm_spin.setValue(status["rate_limiter"]["max_rpm"])
            
            # Update IP filtering
            self._update_ip_tables()
            
            # Load recent events
            self._load_recent_events()
            
            # Update config info
            config_hash = self.config_manager.get_config_hash()
            self.config_hash_label.setText(config_hash[:16] + "...")
            
        except Exception as e:
            self.logger.error(f"Error loading security status: {e}")
    
    def _refresh_status(self):
        """Refresh security status"""
        self._load_security_status()
    
    def _update_ip_tables(self):
        """Update IP filtering tables"""
        try:
            stats = self.security_manager.ip_filter.get_stats()
            
            # Update whitelist table
            self.whitelist_table.setRowCount(len(stats["whitelist"]) + len(stats["whitelist_ranges"]))
            
            row = 0
            for ip in stats["whitelist"]:
                self.whitelist_table.setItem(row, 0, QTableWidgetItem(ip))
                self.whitelist_table.setItem(row, 1, QTableWidgetItem("Exact"))
                row += 1
            
            for range_str in stats["whitelist_ranges"]:
                self.whitelist_table.setItem(row, 0, QTableWidgetItem(range_str))
                self.whitelist_table.setItem(row, 1, QTableWidgetItem("Range"))
                row += 1
            
            # Update blacklist table
            self.blacklist_table.setRowCount(len(stats["blacklist"]) + len(stats["blacklist_ranges"]))
            
            row = 0
            for ip in stats["blacklist"]:
                self.blacklist_table.setItem(row, 0, QTableWidgetItem(ip))
                self.blacklist_table.setItem(row, 1, QTableWidgetItem("Exact"))
                row += 1
            
            for range_str in stats["blacklist_ranges"]:
                self.blacklist_table.setItem(row, 0, QTableWidgetItem(range_str))
                self.blacklist_table.setItem(row, 1, QTableWidgetItem("Range"))
                row += 1
            
        except Exception as e:
            self.logger.error(f"Error updating IP tables: {e}")
    
    def _load_recent_events(self):
        """Load recent security events"""
        try:
            events = self.security_manager.audit_logger.query_events(limit=50)
            
            self.recent_events_table.setRowCount(len(events))
            
            for i, event in enumerate(events):
                time_str = time.strftime("%H:%M:%S", time.localtime(event["timestamp"]))
                self.recent_events_table.setItem(i, 0, QTableWidgetItem(time_str))
                self.recent_events_table.setItem(i, 1, QTableWidgetItem(event["event_type"]))
                self.recent_events_table.setItem(i, 2, QTableWidgetItem(event["source_ip"]))
                self.recent_events_table.setItem(i, 3, QTableWidgetItem(event["action"]))
                self.recent_events_table.setItem(i, 4, QTableWidgetItem(str(event["details"])[:50]))
            
        except Exception as e:
            self.logger.error(f"Error loading recent events: {e}")
    
    # DNSSEC methods
    def _toggle_dnssec(self, checked):
        """Toggle DNSSEC"""
        if checked:
            self.dnssec_manager.enable_dnssec()
        else:
            self.dnssec_manager.disable_dnssec()
    
    def _generate_dnssec_key(self):
        """Generate DNSSEC key"""
        zone_name = self.zone_name_edit.text().strip()
        key_type = self.key_type_combo.currentText()
        key_size = self.key_size_spin.value()
        
        if not zone_name:
            QMessageBox.warning(self, "Warning", "Please enter a zone name")
            return
        
        self.dnssec_progress_bar.setVisible(True)
        self.dnssec_progress_bar.setValue(0)
        
        self.worker = SecurityWorker("generate_key", self.dnssec_manager, 
                                    zone_name=zone_name, key_type=key_type, key_size=key_size)
        self.worker.progress_updated.connect(self.dnssec_progress_bar.setValue)
        self.worker.finished.connect(self._on_dnssec_operation_finished)
        self.worker.error.connect(self._on_dnssec_operation_error)
        self.worker.start()
    
    def _sign_zone(self):
        """Sign DNS zone"""
        zone_name = self.zone_name_edit.text().strip()
        
        if not zone_name:
            QMessageBox.warning(self, "Warning", "Please enter a zone name")
            return
        
        # Get records from database (simplified)
        records = []  # Would load from actual database
        
        self.dnssec_progress_bar.setVisible(True)
        self.dnssec_progress_bar.setValue(0)
        
        self.worker = SecurityWorker("sign_zone", self.dnssec_manager, 
                                    zone_name=zone_name, records=records)
        self.worker.progress_updated.connect(self.dnssec_progress_bar.setValue)
        self.worker.finished.connect(self._on_dnssec_operation_finished)
        self.worker.error.connect(self._on_dnssec_operation_error)
        self.worker.start()
    
    def _rotate_dnssec_keys(self):
        """Rotate DNSSEC keys"""
        zone_name = self.zone_name_edit.text().strip()
        
        if not zone_name:
            QMessageBox.warning(self, "Warning", "Please enter a zone name")
            return
        
        self.dnssec_progress_bar.setVisible(True)
        self.dnssec_progress_bar.setValue(0)
        
        self.worker = SecurityWorker("rotate_keys", self.dnssec_manager, 
                                    zone_name=zone_name)
        self.worker.progress_updated.connect(self.dnssec_progress_bar.setValue)
        self.worker.finished.connect(self._on_dnssec_operation_finished)
        self.worker.error.connect(self._on_dnssec_operation_error)
        self.worker.start()
    
    def _on_dnssec_operation_finished(self, result, success):
        """Handle DNSSEC operation completion"""
        self.dnssec_progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", result)
            self._load_security_status()
        else:
            QMessageBox.warning(self, "Warning", result)
    
    def _on_dnssec_operation_error(self, error_message):
        """Handle DNSSEC operation error"""
        self.dnssec_progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", error_message)
    
    # Rate limiting methods
    def _toggle_rate_limiting(self, checked):
        """Toggle rate limiting"""
        # Update configuration
        self.config_manager.set("security.rate_limiting_enabled", checked)
    
    def _apply_rate_limits(self):
        """Apply rate limiting settings"""
        max_rps = self.max_rps_spin.value()
        max_rpm = self.max_rpm_spin.value()
        
        # Update configuration
        self.config_manager.update({
            "security.max_requests_per_second": max_rps,
            "security.max_requests_per_minute": max_rpm
        })
        
        QMessageBox.information(self, "Success", "Rate limiting settings applied")
    
    # IP filtering methods
    def _toggle_ip_filtering(self, checked):
        """Toggle IP filtering"""
        self.config_manager.set("security.ip_filtering_enabled", checked)
    
    def _add_to_whitelist(self):
        """Add IP to whitelist"""
        ip_or_range = self.whitelist_edit.text().strip()
        if not ip_or_range:
            return
        
        if self.security_manager.ip_filter.add_to_whitelist(ip_or_range):
            self.whitelist_edit.clear()
            self._update_ip_tables()
            QMessageBox.information(self, "Success", f"Added to whitelist: {ip_or_range}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to add to whitelist: {ip_or_range}")
    
    def _add_to_blacklist(self):
        """Add IP to blacklist"""
        ip_or_range = self.blacklist_edit.text().strip()
        if not ip_or_range:
            return
        
        if self.security_manager.ip_filter.add_to_blacklist(ip_or_range):
            self.blacklist_edit.clear()
            self._update_ip_tables()
            QMessageBox.information(self, "Success", f"Added to blacklist: {ip_or_range}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to add to blacklist: {ip_or_range}")
    
    def _remove_from_whitelist(self):
        """Remove selected from whitelist"""
        current_row = self.whitelist_table.currentRow()
        if current_row >= 0:
            ip_or_range = self.whitelist_table.item(current_row, 0).text()
            if self.security_manager.ip_filter.remove_from_whitelist(ip_or_range):
                self._update_ip_tables()
                QMessageBox.information(self, "Success", f"Removed from whitelist: {ip_or_range}")
    
    def _remove_from_blacklist(self):
        """Remove selected from blacklist"""
        current_row = self.blacklist_table.currentRow()
        if current_row >= 0:
            ip_or_range = self.blacklist_table.item(current_row, 0).text()
            if self.security_manager.ip_filter.remove_from_blacklist(ip_or_range):
                self._update_ip_tables()
                QMessageBox.information(self, "Success", f"Removed from blacklist: {ip_or_range}")
    
    # Audit logging methods
    def _toggle_audit_logging(self, checked):
        """Toggle audit logging"""
        self.config_manager.set("security.audit_logging_enabled", checked)
    
    def _apply_audit_settings(self):
        """Apply audit logging settings"""
        retention_days = self.retention_days_spin.value()
        
        self.config_manager.set("security.log_retention_days", retention_days)
        QMessageBox.information(self, "Success", "Audit logging settings applied")
    
    def _refresh_audit_events(self):
        """Refresh audit events table"""
        try:
            event_type = self.event_type_combo.currentText()
            severity = self.severity_combo.currentText()
            
            # Build query parameters
            params = {}
            if event_type != "All":
                params["event_type"] = event_type
            if severity != "All":
                params["severity"] = severity
            
            events = self.security_manager.audit_logger.query_events(**params)
            
            self.audit_events_table.setRowCount(len(events))
            
            for i, event in enumerate(events):
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event["timestamp"]))
                self.audit_events_table.setItem(i, 0, QTableWidgetItem(time_str))
                self.audit_events_table.setItem(i, 1, QTableWidgetItem(event["event_type"]))
                self.audit_events_table.setItem(i, 2, QTableWidgetItem(event["source_ip"]))
                self.audit_events_table.setItem(i, 3, QTableWidgetItem(event["query_name"]))
                self.audit_events_table.setItem(i, 4, QTableWidgetItem(event["action"]))
                self.audit_events_table.setItem(i, 5, QTableWidgetItem(event["severity"]))
            
        except Exception as e:
            self.logger.error(f"Error refreshing audit events: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh audit events: {e}")
    
    def _export_audit_events(self):
        """Export audit events to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Audit Events",
                f"audit_events_{int(time.time())}.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                events = self.security_manager.audit_logger.query_events(limit=10000)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Timestamp,Event Type,Source IP,Query Name,Query Type,Action,Severity,Details\n")
                    
                    for event in events:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event["timestamp"]))
                        details = str(event["details"]).replace('"', '""')
                        f.write(f'"{timestamp}","{event["event_type"]}","{event["source_ip"]}",'
                               f'"{event["query_name"]}","{event["query_type"]}","{event["action"]}",'
                               f'"{event["severity"]}","{details}"\n')
                
                QMessageBox.information(self, "Success", f"Audit events exported to: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error exporting audit events: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export audit events: {e}")
    
    # Configuration methods
    def _backup_config(self):
        """Backup configuration"""
        try:
            backup_path = self.config_manager.backup()
            QMessageBox.information(self, "Success", f"Configuration backed up to: {backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to backup configuration: {e}")
    
    def _restore_config(self):
        """Restore configuration"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Configuration Backup",
                "", "Encrypted Files (*.enc);;All Files (*)"
            )
            
            if file_path:
                if self.config_manager.restore(file_path):
                    QMessageBox.information(self, "Success", "Configuration restored successfully")
                    self._load_security_status()
                else:
                    QMessageBox.warning(self, "Error", "Failed to restore configuration")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore configuration: {e}")
    
    def _change_password(self):
        """Change master password"""
        current = self.current_password_edit.text()
        new = self.new_password_edit.text()
        confirm = self.confirm_password_edit.text()
        
        if not current or not new or not confirm:
            QMessageBox.warning(self, "Warning", "All password fields are required")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Warning", "New passwords do not match")
            return
        
        if self.config_manager.change_password(current, new):
            QMessageBox.information(self, "Success", "Master password changed successfully")
            self.current_password_edit.clear()
            self.new_password_edit.clear()
            self.confirm_password_edit.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to change password")
    
    def _verify_integrity(self):
        """Verify configuration integrity"""
        if self.config_manager.verify_integrity():
            QMessageBox.information(self, "Success", "Configuration integrity verified")
            self.integrity_status_label.setText("Valid")
        else:
            QMessageBox.warning(self, "Warning", "Configuration integrity check failed")
            self.integrity_status_label.setText("Invalid")
