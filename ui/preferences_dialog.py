#!/usr/bin/env python3
"""
Preferences dialog for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QGroupBox, QFormLayout, QSlider,
    QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont

class PreferencesDialog(QDialog):
    """Preferences dialog for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("Preferences - DNS Server Manager")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the preferences dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # General tab
        self.general_tab = self._create_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Server tab
        self.server_tab = self._create_server_tab()
        self.tab_widget.addTab(self.server_tab, "Server")
        
        # UI tab
        self.ui_tab = self._create_ui_tab()
        self.tab_widget.addTab(self.ui_tab, "Interface")
        
        # Logging tab
        self.logging_tab = self._create_logging_tab()
        self.tab_widget.addTab(self.logging_tab, "Logging")
        
        # Network tab
        self.network_tab = self._create_network_tab()
        self.tab_widget.addTab(self.network_tab, "Network")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._ok_clicked)
        self.ok_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Application settings
        app_group = QGroupBox("Application")
        app_layout = QFormLayout(app_group)
        
        self.start_minimized_checkbox = QCheckBox("Start minimized to system tray")
        app_layout.addRow("Startup:", self.start_minimized_checkbox)
        
        self.minimize_on_close_checkbox = QCheckBox("Minimize to tray on close")
        self.minimize_on_close_checkbox.setChecked(True)
        app_layout.addRow("Window Behavior:", self.minimize_on_close_checkbox)
        
        self.show_notifications_checkbox = QCheckBox("Show system notifications")
        self.show_notifications_checkbox.setChecked(True)
        app_layout.addRow("Notifications:", self.show_notifications_checkbox)
        
        self.auto_start_server_checkbox = QCheckBox("Auto-start DNS server")
        app_layout.addRow("Server:", self.auto_start_server_checkbox)
        
        layout.addWidget(app_group)
        
        # Backup settings
        backup_group = QGroupBox("Backup")
        backup_layout = QFormLayout(backup_group)
        
        self.auto_backup_checkbox = QCheckBox("Enable automatic backup")
        backup_layout.addRow("Auto Backup:", self.auto_backup_checkbox)
        
        self.backup_interval_spinbox = QSpinBox()
        self.backup_interval_spinbox.setRange(1, 24)
        self.backup_interval_spinbox.setValue(6)
        self.backup_interval_spinbox.setSuffix(" hours")
        backup_layout.addRow("Backup Interval:", self.backup_interval_spinbox)
        
        self.backup_path_edit = QLineEdit()
        self.backup_browse_button = QPushButton("Browse...")
        self.backup_browse_button.clicked.connect(self._browse_backup_path)
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(self.backup_browse_button)
        backup_layout.addRow("Backup Path:", backup_path_layout)
        
        layout.addWidget(backup_group)
        
        layout.addStretch()
        return widget
    
    def _create_server_tab(self) -> QWidget:
        """Create server settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # DNS server settings
        dns_group = QGroupBox("DNS Server")
        dns_layout = QFormLayout(dns_group)
        
        self.default_port_spinbox = QSpinBox()
        self.default_port_spinbox.setRange(1, 65535)
        self.default_port_spinbox.setValue(53)
        dns_layout.addRow("Default Port:", self.default_port_spinbox)
        
        self.default_bind_edit = QLineEdit("0.0.0.0")
        dns_layout.addRow("Default Bind Address:", self.default_bind_edit)
        
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(5)
        self.timeout_spinbox.setSuffix(" seconds")
        dns_layout.addRow("Query Timeout:", self.timeout_spinbox)
        
        self.max_connections_spinbox = QSpinBox()
        self.max_connections_spinbox.setRange(10, 10000)
        self.max_connections_spinbox.setValue(1000)
        dns_layout.addRow("Max Connections:", self.max_connections_spinbox)
        
        layout.addWidget(dns_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout(perf_group)
        
        self.cache_size_spinbox = QSpinBox()
        self.cache_size_spinbox.setRange(100, 100000)
        self.cache_size_spinbox.setValue(10000)
        perf_layout.addRow("Cache Size:", self.cache_size_spinbox)
        
        self.thread_pool_spinbox = QSpinBox()
        self.thread_pool_spinbox.setRange(1, 100)
        self.thread_pool_spinbox.setValue(10)
        perf_layout.addRow("Thread Pool Size:", self.thread_pool_spinbox)
        
        layout.addWidget(perf_group)
        
        layout.addStretch()
        return widget
    
    def _create_ui_tab(self) -> QWidget:
        """Create UI settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "system"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(10)
        appearance_layout.addRow("Font Size:", self.font_size_spinbox)
        
        self.compact_mode_checkbox = QCheckBox("Compact mode")
        appearance_layout.addRow("Display:", self.compact_mode_checkbox)
        
        layout.addWidget(appearance_group)
        
        # Window behavior
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.remember_size_checkbox = QCheckBox("Remember window size and position")
        self.remember_size_checkbox.setChecked(True)
        window_layout.addRow("Memory:", self.remember_size_checkbox)
        
        self.always_on_top_checkbox = QCheckBox("Always on top")
        window_layout.addRow("Behavior:", self.always_on_top_checkbox)
        
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray")
        self.minimize_to_tray_checkbox.setChecked(True)
        window_layout.addRow("", self.minimize_to_tray_checkbox)
        
        layout.addWidget(window_group)
        
        layout.addStretch()
        return widget
    
    def _create_logging_tab(self) -> QWidget:
        """Create logging settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log settings
        log_group = QGroupBox("Logging")
        log_layout = QFormLayout(log_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow("Log Level:", self.log_level_combo)
        
        self.log_file_edit = QLineEdit("config/dns_server.log")
        self.log_browse_button = QPushButton("Browse...")
        self.log_browse_button.clicked.connect(self._browse_log_file)
        
        log_file_layout = QHBoxLayout()
        log_file_layout.addWidget(self.log_file_edit)
        log_file_layout.addWidget(self.log_browse_button)
        log_layout.addRow("Log File:", log_file_layout)
        
        self.max_log_size_spinbox = QSpinBox()
        self.max_log_size_spinbox.setRange(1, 100)
        self.max_log_size_spinbox.setValue(10)
        self.max_log_size_spinbox.setSuffix(" MB")
        log_layout.addRow("Max File Size:", self.max_log_size_spinbox)
        
        self.log_backup_count_spinbox = QSpinBox()
        self.log_backup_count_spinbox.setRange(1, 10)
        self.log_backup_count_spinbox.setValue(5)
        log_layout.addRow("Backup Count:", self.log_backup_count_spinbox)
        
        layout.addWidget(log_group)
        
        # Log options
        options_group = QGroupBox("Log Options")
        options_layout = QFormLayout(options_group)
        
        self.log_to_console_checkbox = QCheckBox("Log to console")
        self.log_to_console_checkbox.setChecked(True)
        options_layout.addRow("Console:", self.log_to_console_checkbox)
        
        self.log_queries_checkbox = QCheckBox("Log DNS queries")
        options_layout.addRow("DNS Queries:", self.log_queries_checkbox)
        
        self.log_performance_checkbox = QCheckBox("Log performance metrics")
        options_layout.addRow("Performance:", self.log_performance_checkbox)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        return widget
    
    def _create_network_tab(self) -> QWidget:
        """Create network settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Network settings
        network_group = QGroupBox("Network")
        network_layout = QFormLayout(network_group)
        
        self.upstream_dns_edit = QLineEdit("8.8.8.8,8.8.4.4")
        network_layout.addRow("Upstream DNS:", self.upstream_dns_edit)
        
        self.dns_timeout_spinbox = QSpinBox()
        self.dns_timeout_spinbox.setRange(1, 30)
        self.dns_timeout_spinbox.setValue(5)
        self.dns_timeout_spinbox.setSuffix(" seconds")
        network_layout.addRow("DNS Timeout:", self.dns_timeout_spinbox)
        
        self.max_retries_spinbox = QSpinBox()
        self.max_retries_spinbox.setRange(1, 5)
        self.max_retries_spinbox.setValue(3)
        network_layout.addRow("Max Retries:", self.max_retries_spinbox)
        
        layout.addWidget(network_group)
        
        # Security
        security_group = QGroupBox("Security")
        security_layout = QFormLayout(security_group)
        
        self.rate_limit_checkbox = QCheckBox("Enable rate limiting")
        security_layout.addRow("Rate Limiting:", self.rate_limit_checkbox)
        
        self.rate_limit_spinbox = QSpinBox()
        self.rate_limit_spinbox.setRange(10, 1000)
        self.rate_limit_spinbox.setValue(100)
        self.rate_limit_spinbox.setSuffix(" req/sec")
        security_layout.addRow("Rate Limit:", self.rate_limit_spinbox)
        
        self.allow_recursive_checkbox = QCheckBox("Allow recursive queries")
        self.allow_recursive_checkbox.setChecked(True)
        security_layout.addRow("Recursive:", self.allow_recursive_checkbox)
        
        layout.addWidget(security_group)
        
        layout.addStretch()
        return widget
    
    def _browse_backup_path(self):
        """Browse for backup directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            self.backup_path_edit.setText(directory)
    
    def _browse_log_file(self):
        """Browse for log file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Log File", self.log_file_edit.text(), "Log Files (*.log);;All Files (*)"
        )
        if file_path:
            self.log_file_edit.setText(file_path)
    
    def _load_settings(self):
        """Load settings from QSettings"""
        settings = QSettings()
        
        # General settings
        settings.beginGroup("general")
        self.start_minimized_checkbox.setChecked(settings.value("start_minimized", False, bool))
        self.minimize_on_close_checkbox.setChecked(settings.value("minimize_on_close", True, bool))
        self.show_notifications_checkbox.setChecked(settings.value("show_notifications", True, bool))
        self.auto_start_server_checkbox.setChecked(settings.value("auto_start_server", False, bool))
        self.auto_backup_checkbox.setChecked(settings.value("auto_backup", False, bool))
        self.backup_interval_spinbox.setValue(settings.value("backup_interval", 6, int))
        self.backup_path_edit.setText(settings.value("backup_path", "", str))
        settings.endGroup()
        
        # Server settings
        settings.beginGroup("server")
        self.default_port_spinbox.setValue(settings.value("default_port", 53, int))
        self.default_bind_edit.setText(settings.value("default_bind", "0.0.0.0", str))
        self.timeout_spinbox.setValue(settings.value("timeout", 5, int))
        self.max_connections_spinbox.setValue(settings.value("max_connections", 1000, int))
        self.cache_size_spinbox.setValue(settings.value("cache_size", 10000, int))
        self.thread_pool_spinbox.setValue(settings.value("thread_pool", 10, int))
        settings.endGroup()
        
        # UI settings
        settings.beginGroup("ui")
        self.theme_combo.setCurrentText(settings.value("theme", "light", str))
        self.font_size_spinbox.setValue(settings.value("font_size", 10, int))
        self.compact_mode_checkbox.setChecked(settings.value("compact_mode", False, bool))
        self.remember_size_checkbox.setChecked(settings.value("remember_size", True, bool))
        self.always_on_top_checkbox.setChecked(settings.value("always_on_top", False, bool))
        self.minimize_to_tray_checkbox.setChecked(settings.value("minimize_to_tray", True, bool))
        settings.endGroup()
        
        # Logging settings
        settings.beginGroup("logging")
        self.log_level_combo.setCurrentText(settings.value("log_level", "INFO", str))
        self.log_file_edit.setText(settings.value("log_file", "config/dns_server.log", str))
        self.max_log_size_spinbox.setValue(settings.value("max_log_size", 10, int))
        self.log_backup_count_spinbox.setValue(settings.value("log_backup_count", 5, int))
        self.log_to_console_checkbox.setChecked(settings.value("log_to_console", True, bool))
        self.log_queries_checkbox.setChecked(settings.value("log_queries", False, bool))
        self.log_performance_checkbox.setChecked(settings.value("log_performance", False, bool))
        settings.endGroup()
        
        # Network settings
        settings.beginGroup("network")
        self.upstream_dns_edit.setText(settings.value("upstream_dns", "8.8.8.8,8.8.4.4", str))
        self.dns_timeout_spinbox.setValue(settings.value("dns_timeout", 5, int))
        self.max_retries_spinbox.setValue(settings.value("max_retries", 3, int))
        self.rate_limit_checkbox.setChecked(settings.value("rate_limit", False, bool))
        self.rate_limit_spinbox.setValue(settings.value("rate_limit_value", 100, int))
        self.allow_recursive_checkbox.setChecked(settings.value("allow_recursive", True, bool))
        settings.endGroup()
    
    def _save_settings(self):
        """Save settings to QSettings"""
        settings = QSettings()
        
        # General settings
        settings.beginGroup("general")
        settings.setValue("start_minimized", self.start_minimized_checkbox.isChecked())
        settings.setValue("minimize_on_close", self.minimize_on_close_checkbox.isChecked())
        settings.setValue("show_notifications", self.show_notifications_checkbox.isChecked())
        settings.setValue("auto_start_server", self.auto_start_server_checkbox.isChecked())
        settings.setValue("auto_backup", self.auto_backup_checkbox.isChecked())
        settings.setValue("backup_interval", self.backup_interval_spinbox.value())
        settings.setValue("backup_path", self.backup_path_edit.text())
        settings.endGroup()
        
        # Server settings
        settings.beginGroup("server")
        settings.setValue("default_port", self.default_port_spinbox.value())
        settings.setValue("default_bind", self.default_bind_edit.text())
        settings.setValue("timeout", self.timeout_spinbox.value())
        settings.setValue("max_connections", self.max_connections_spinbox.value())
        settings.setValue("cache_size", self.cache_size_spinbox.value())
        settings.setValue("thread_pool", self.thread_pool_spinbox.value())
        settings.endGroup()
        
        # UI settings
        settings.beginGroup("ui")
        settings.setValue("theme", self.theme_combo.currentText())
        settings.setValue("font_size", self.font_size_spinbox.value())
        settings.setValue("compact_mode", self.compact_mode_checkbox.isChecked())
        settings.setValue("remember_size", self.remember_size_checkbox.isChecked())
        settings.setValue("always_on_top", self.always_on_top_checkbox.isChecked())
        settings.setValue("minimize_to_tray", self.minimize_to_tray_checkbox.isChecked())
        settings.endGroup()
        
        # Logging settings
        settings.beginGroup("logging")
        settings.setValue("log_level", self.log_level_combo.currentText())
        settings.setValue("log_file", self.log_file_edit.text())
        settings.setValue("max_log_size", self.max_log_size_spinbox.value())
        settings.setValue("log_backup_count", self.log_backup_count_spinbox.value())
        settings.setValue("log_to_console", self.log_to_console_checkbox.isChecked())
        settings.setValue("log_queries", self.log_queries_checkbox.isChecked())
        settings.setValue("log_performance", self.log_performance_checkbox.isChecked())
        settings.endGroup()
        
        # Network settings
        settings.beginGroup("network")
        settings.setValue("upstream_dns", self.upstream_dns_edit.text())
        settings.setValue("dns_timeout", self.dns_timeout_spinbox.value())
        settings.setValue("max_retries", self.max_retries_spinbox.value())
        settings.setValue("rate_limit", self.rate_limit_checkbox.isChecked())
        settings.setValue("rate_limit_value", self.rate_limit_spinbox.value())
        settings.setValue("allow_recursive", self.allow_recursive_checkbox.isChecked())
        settings.endGroup()
    
    def _apply_settings(self):
        """Apply settings without closing dialog"""
        self._save_settings()
        self.logger.info("Preferences applied")
        QMessageBox.information(self, "Preferences", "Settings have been applied successfully.")
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Preferences",
            "Are you sure you want to reset all preferences to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear settings
            settings = QSettings()
            settings.clear()
            
            # Reload defaults
            self._load_settings()
            self.logger.info("Preferences reset to defaults")
            QMessageBox.information(self, "Preferences", "All preferences have been reset to defaults.")
    
    def _ok_clicked(self):
        """Save settings and close dialog"""
        self._save_settings()
        self.accept()
    
    def get_settings(self):
        """Get current settings as dictionary"""
        return {
            'general': {
                'start_minimized': self.start_minimized_checkbox.isChecked(),
                'minimize_on_close': self.minimize_on_close_checkbox.isChecked(),
                'show_notifications': self.show_notifications_checkbox.isChecked(),
                'auto_start_server': self.auto_start_server_checkbox.isChecked(),
            },
            'ui': {
                'theme': self.theme_combo.currentText(),
                'font_size': self.font_size_spinbox.value(),
                'remember_size': self.remember_size_checkbox.isChecked(),
                'always_on_top': self.always_on_top_checkbox.isChecked(),
                'minimize_to_tray': self.minimize_to_tray_checkbox.isChecked(),
            },
            'server': {
                'default_port': self.default_port_spinbox.value(),
                'default_bind': self.default_bind_edit.text(),
                'timeout': self.timeout_spinbox.value(),
                'max_connections': self.max_connections_spinbox.value(),
            },
            'logging': {
                'log_level': self.log_level_combo.currentText(),
                'log_file': self.log_file_edit.text(),
                'log_to_console': self.log_to_console_checkbox.isChecked(),
            }
        }
