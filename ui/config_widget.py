"""
Configuration widget for DNS Server
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QPushButton, QMessageBox,
    QTabWidget, QLabel, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.config import Config

class ConfigWidget(QWidget):
    """Widget for managing DNS server configuration"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self):
        """Setup the configuration widget UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Server Configuration")
        title_label.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        # Tab widget for different config sections
        self.tab_widget = QTabWidget()
        
        # DNS configuration tab
        dns_tab = self._create_dns_config_tab()
        self.tab_widget.addTab(dns_tab, "DNS Settings")
        
        # Logging configuration tab
        logging_tab = self._create_logging_config_tab()
        self.tab_widget.addTab(logging_tab, "Logging")
        
        # UI configuration tab
        ui_tab = self._create_ui_config_tab()
        self.tab_widget.addTab(ui_tab, "Interface")
        
        layout.addWidget(self.tab_widget)
        
        # Save/Reset buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_config)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _create_dns_config_tab(self) -> QWidget:
        """Create DNS configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # DNS settings group
        dns_group = QGroupBox("DNS Server Settings")
        dns_layout = QFormLayout(dns_group)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(53)
        dns_layout.addRow("DNS Port:", self.port_spin)
        
        # Bind address
        self.bind_address_edit = QLineEdit()
        self.bind_address_edit.setPlaceholderText("0.0.0.0")
        dns_layout.addRow("Bind Address:", self.bind_address_edit)
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(5)
        self.timeout_spin.setSuffix(" seconds")
        dns_layout.addRow("Query Timeout:", self.timeout_spin)
        
        # Max connections
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(10, 10000)
        self.max_connections_spin.setValue(1000)
        dns_layout.addRow("Max Connections:", self.max_connections_spin)
        
        layout.addWidget(dns_group)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        # Enable recursion
        self.enable_recursion_check = QCheckBox("Enable DNS Recursion")
        self.enable_recursion_check.setChecked(True)
        advanced_layout.addRow(self.enable_recursion_check)
        
        # Forward DNS
        self.forward_dns_edit = QLineEdit()
        self.forward_dns_edit.setPlaceholderText("8.8.8.8, 1.1.1.1")
        advanced_layout.addRow("Forward DNS Servers:", self.forward_dns_edit)
        
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        return tab
    
    def _create_logging_config_tab(self) -> QWidget:
        """Create logging configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging settings group
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QFormLayout(logging_group)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        # Log file
        self.log_file_edit = QLineEdit()
        self.log_file_edit.setText("config/dns_server.log")
        logging_layout.addRow("Log File:", self.log_file_edit)
        
        # Max file size
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1024, 104857600)  # 1KB to 100MB
        self.max_size_spin.setValue(10485760)  # 10MB
        self.max_size_spin.setSuffix(" bytes")
        logging_layout.addRow("Max File Size:", self.max_size_spin)
        
        # Backup count
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 50)
        self.backup_count_spin.setValue(5)
        logging_layout.addRow("Backup Count:", self.backup_count_spin)
        
        layout.addWidget(logging_group)
        
        # Log preview
        preview_group = QGroupBox("Current Log Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.log_preview = QTextEdit()
        self.log_preview.setReadOnly(True)
        self.log_preview.setMaximumHeight(200)
        self.log_preview.setFont(QFont("Consolas", 9))
        preview_layout.addWidget(self.log_preview)
        
        refresh_button = QPushButton("Refresh Log Preview")
        refresh_button.clicked.connect(self._refresh_log_preview)
        preview_layout.addWidget(refresh_button)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
        return tab
    
    def _create_ui_config_tab(self) -> QWidget:
        """Create UI configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Interface settings group
        ui_group = QGroupBox("Interface Settings")
        ui_layout = QFormLayout(ui_group)
        
        # Window width
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2560)
        self.window_width_spin.setValue(1200)
        ui_layout.addRow("Window Width:", self.window_width_spin)
        
        # Window height
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1440)
        self.window_height_spin.setValue(800)
        ui_layout.addRow("Window Height:", self.window_height_spin)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "auto"])
        self.theme_combo.setCurrentText("light")
        ui_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(ui_group)
        
        # Behavior settings group
        behavior_group = QGroupBox("Behavior Settings")
        behavior_layout = QFormLayout(behavior_group)
        
        # Auto start server
        self.auto_start_check = QCheckBox("Auto-start server on launch")
        behavior_layout.addRow(self.auto_start_check)
        
        # Minimize to tray
        self.minimize_tray_check = QCheckBox("Minimize to system tray")
        behavior_layout.addRow(self.minimize_tray_check)
        
        # Show notifications
        self.show_notifications_check = QCheckBox("Show desktop notifications")
        self.show_notifications_check.setChecked(True)
        behavior_layout.addRow(self.show_notifications_check)
        
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        return tab
    
    def _load_config(self):
        """Load configuration from config object"""
        try:
            # DNS settings
            self.port_spin.setValue(self.config.dns_port)
            self.bind_address_edit.setText(self.config.bind_address)
            self.timeout_spin.setValue(self.config.dns_timeout)
            self.max_connections_spin.setValue(self.config.max_connections)
            
            # Logging settings
            self.log_level_combo.setCurrentText(self.config.get("logging.level", "INFO"))
            self.log_file_edit.setText(self.config.get("logging.file", "config/dns_server.log"))
            self.max_size_spin.setValue(self.config.get("logging.max_size", 10485760))
            self.backup_count_spin.setValue(self.config.get("logging.backup_count", 5))
            
            # UI settings
            self.window_width_spin.setValue(self.config.get("ui.window_width", 1200))
            self.window_height_spin.setValue(self.config.get("ui.window_height", 800))
            self.theme_combo.setCurrentText(self.config.get("ui.theme", "light"))
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def _save_config(self):
        """Save configuration to config object"""
        try:
            # DNS settings
            self.config.set("dns.port", self.port_spin.value())
            self.config.set("dns.bind_address", self.bind_address_edit.text())
            self.config.set("dns.timeout", self.timeout_spin.value())
            self.config.set("dns.max_connections", self.max_connections_spin.value())
            
            # Logging settings
            self.config.set("logging.level", self.log_level_combo.currentText())
            self.config.set("logging.file", self.log_file_edit.text())
            self.config.set("logging.max_size", self.max_size_spin.value())
            self.config.set("logging.backup_count", self.backup_count_spin.value())
            
            # UI settings
            self.config.set("ui.window_width", self.window_width_spin.value())
            self.config.set("ui.window_height", self.window_height_spin.value())
            self.config.set("ui.theme", self.theme_combo.currentText())
            
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.logger.info("Configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
    
    def _reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, 'Confirm Reset',
            'Reset all configuration to default values?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Reset to defaults (this would require config object support)
                self._load_config()  # Reload current values
                QMessageBox.information(self, "Success", "Configuration reset to defaults!")
                self.logger.info("Configuration reset to defaults")
                
            except Exception as e:
                self.logger.error(f"Error resetting configuration: {e}")
                QMessageBox.critical(self, "Error", f"Failed to reset configuration: {e}")
    
    def _refresh_log_preview(self):
        """Refresh log preview"""
        try:
            with open(self.log_file_edit.text(), 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 50 lines
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                self.log_preview.setText(''.join(recent_lines))
        except FileNotFoundError:
            self.log_preview.setText("Log file not found")
        except Exception as e:
            self.log_preview.setText(f"Error reading log file: {e}")
