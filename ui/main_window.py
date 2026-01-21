"""
Main window for DNS Server Manager
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QMessageBox, QStatusBar, QSplitter, QFrame,
    QMenuBar, QMenu
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QAction

from .records_widget import RecordsWidget
from .stats_widget import StatsWidget
from .config_widget import ConfigWidget
from .logs_widget import LogsWidget
from .database_widget import DatabaseWidget
from core.dns_server import DNSServer
from core.config import Config
from core.dns_records import DNSRecord, DNSRecordType
from about import AboutDialog
from help import HelpDialog
from sponsor import SponsorDialog
import version
from .themes import theme_manager

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, dns_server: DNSServer, config: Config):
        super().__init__()
        self.dns_server = dns_server
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle("DNS Server Manager")
        self.setMinimumSize(1200, 800)
        
        # Setup UI
        self._setup_theme()
        self._setup_menu()
        self._setup_ui()
        self._setup_status_bar()
        self._setup_timer()
        
        # Load initial state
        self._update_server_status()
    
    def _setup_theme(self):
        """Setup application theme"""
        # Get theme from config
        theme_name = self.config.get("ui.theme", "light")
        theme_manager.set_theme(theme_name)
        
        # Apply stylesheet
        self.setStyleSheet(theme_manager.get_stylesheet())
    
    def _setup_menu(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        preferences_action = edit_menu.addAction("Preferences")
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self._show_preferences)
        
        # Theme submenu
        theme_menu = edit_menu.addMenu("Theme")
        light_theme_action = theme_menu.addAction("Light Theme")
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self._change_theme("light"))
        
        dark_theme_action = theme_menu.addAction("Dark Theme")
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        
        # Set current theme checked
        current_theme = theme_manager.get_current_theme()
        if current_theme == "light":
            light_theme_action.setChecked(True)
        else:
            dark_theme_action.setChecked(True)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        clear_logs_action = tools_menu.addAction("Clear Logs")
        clear_logs_action.triggered.connect(self._clear_logs)
        
        export_config_action = tools_menu.addAction("Export Configuration")
        export_config_action.triggered.connect(self._export_configuration)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = help_menu.addAction("Help")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self._show_help)
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)
        
        version_action = help_menu.addAction("Version")
        version_action.triggered.connect(self._show_version)
        
        sponsor_action = help_menu.addAction("Sponsor")
        sponsor_action.triggered.connect(self._show_sponsor)
    
    def _setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header with server controls
        header_widget = self._create_header_widget()
        main_layout.addWidget(header_widget)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Records management tab
        self.records_widget = RecordsWidget(self.dns_server)
        self.tab_widget.addTab(self.records_widget, "DNS Records")
        
        # Statistics tab
        self.stats_widget = StatsWidget(self.dns_server)
        self.tab_widget.addTab(self.stats_widget, "Statistics")
        
        # Configuration tab
        self.config_widget = ConfigWidget(self.config)
        self.tab_widget.addTab(self.config_widget, "Configuration")
        
        # Logs tab
        self.logs_widget = LogsWidget()
        self.tab_widget.addTab(self.logs_widget, "Logs")
        
        # Database tab
        self.database_widget = DatabaseWidget(self.dns_server)
        self.tab_widget.addTab(self.database_widget, "Database")
        
        main_layout.addWidget(self.tab_widget)
    
    def _create_header_widget(self) -> QWidget:
        """Create header widget with server controls"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Server status
        self.status_label = QLabel("Server Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        # Server control buttons
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self._start_server)
        header_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self._stop_server)
        self.stop_button.setEnabled(False)
        header_layout.addWidget(self.stop_button)
        
        # Server info
        info_label = QLabel(f"Port: {self.config.dns_port} | Bind: {self.config.bind_address}")
        info_label.setStyleSheet("color: gray;")
        header_layout.addWidget(info_label)
        
        return header_frame
    
    def _setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_status)
        self.update_timer.start(1000)  # Update every second
    
    def _start_server(self):
        """Start the DNS server"""
        try:
            if self.dns_server.start():
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_bar.showMessage("DNS Server started successfully")
                self.logs_widget.add_log("INFO", "DNS Server started")
            else:
                QMessageBox.warning(self, "Error", "Failed to start DNS server")
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start DNS server: {e}")
    
    def _stop_server(self):
        """Stop the DNS server"""
        try:
            if self.dns_server.stop():
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.status_bar.showMessage("DNS Server stopped")
                self.logs_widget.add_log("INFO", "DNS Server stopped")
            else:
                QMessageBox.warning(self, "Error", "Failed to stop DNS server")
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
            QMessageBox.critical(self, "Error", f"Failed to stop DNS server: {e}")
    
    def _update_server_status(self):
        """Update server status display"""
        if self.dns_server.running:
            self.status_label.setText("Server Status: Running")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setText("Server Status: Stopped")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
    
    def _update_status(self):
        """Update all status displays"""
        self._update_server_status()
        self.stats_widget.update_stats()
    
    def _show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog will be implemented in future versions.")
    
    def _clear_logs(self):
        """Clear application logs"""
        reply = QMessageBox.question(
            self, 'Clear Logs',
            'Are you sure you want to clear all logs?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logs_widget.clear_logs()
            self.status_bar.showMessage("Logs cleared")
    
    def _export_configuration(self):
        """Export current configuration"""
        QMessageBox.information(self, "Export Configuration", "Configuration export will be implemented in future versions.")
    
    def _show_help(self):
        """Show help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()
    
    def _show_about(self):
        """Show about dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def _show_version(self):
        """Show version information"""
        version_info = version.get_version_info()
        version_text = f"""
{version_info['app_name']} v{version_info['version']}

Author: {version_info['author']}
Organization: {version_info['organization']}
License: {version_info['license']}
Website: {version_info['website']}
Email: {version_info['email']}

{version_info['copyright']}
        """.strip()
        
        QMessageBox.information(self, "Version Information", version_text)
    
    def _show_sponsor(self):
        """Show sponsor dialog"""
        sponsor_dialog = SponsorDialog(self)
        sponsor_dialog.exec()
    
    def _change_theme(self, theme_name: str):
        """Change application theme"""
        try:
            # Update theme manager
            theme_manager.set_theme(theme_name)
            
            # Apply new stylesheet
            self.setStyleSheet(theme_manager.get_stylesheet())
            
            # Update all widget themes
            self.logs_widget.update_theme()
            
            # Update configuration
            self.config.set("ui.theme", theme_name)
            
            # Update menu check states
            for action in self.findChildren(QAction):
                if action.text() in ["Light Theme", "Dark Theme"]:
                    action.setChecked(False)
                    if (theme_name == "light" and action.text() == "Light Theme") or \
                       (theme_name == "dark" and action.text() == "Dark Theme"):
                        action.setChecked(True)
            
            self.status_bar.showMessage(f"Theme changed to {theme_name}")
            
        except Exception as e:
            self.logger.error(f"Error changing theme: {e}")
            QMessageBox.critical(self, "Error", f"Failed to change theme: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.dns_server.running:
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'DNS Server is still running. Stop it and exit?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.dns_server.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
