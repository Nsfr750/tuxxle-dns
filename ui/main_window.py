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
    QMenuBar, QMenu, QSystemTrayIcon, QStyle, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QAction

from .records_widget import RecordsWidget
from .stats_widget import StatsWidget
from .config_widget import ConfigWidget
from .logs_widget import LogsWidget
from .database_widget import DatabaseWidget
from .preferences_dialog import PreferencesDialog
from .menu import MenuManager
from .about import AboutDialog
from .help import HelpDialog
from .sponsor import SponsorDialog
from core.dns_server import DNSServer
from core.config import Config
from core.dns_records import DNSRecord, DNSRecordType
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
        self.setWindowIcon(QIcon("assets/icons/icon.ico"))
        
        # Setup system tray
        self._setup_system_tray()
        
        # Setup UI
        self._setup_theme()
        self.menu_manager = MenuManager(self)
        self._setup_ui()
        self._setup_status_bar()
        self._setup_timer()
        
        # Load initial state and preferences
        self._load_preferences()
        self._update_server_status()
    
    def _setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray is not available on this system")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icons/icon.ico"))
        self.tray_icon.setToolTip("DNS Server Manager")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self.show)
        tray_menu.addAction(self.show_action)
        
        # Hide action
        self.hide_action = QAction("Hide to Tray", self)
        self.hide_action.triggered.connect(self.hide_to_tray)
        tray_menu.addAction(self.hide_action)
        
        tray_menu.addSeparator()
        
        # Server status action
        self.status_action = QAction("Server: Stopped", self)
        self.status_action.setEnabled(False)
        tray_menu.addAction(self.status_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.force_close)
        tray_menu.addAction(exit_action)
        
        # Set menu and show
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        self.tray_icon.show()
        
        self.logger.info("System tray initialized")
    
    def _tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide_to_tray()
            else:
                self.show()
        elif reason == QSystemTrayIcon.Trigger:
            if not self.isVisible():
                self.show()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        self.logger.info("Window hidden to system tray")
    
    def show_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.logger.info("Window shown from system tray")
    
    def update_tray_status(self, is_running):
        """Update tray icon status"""
        if hasattr(self, 'status_action'):
            if is_running:
                self.status_action.setText("Server: Running")
                # QAction doesn't support setStyleSheet, use font instead
                font = self.status_action.font()
                font.setBold(True)
                self.status_action.setFont(font)
            else:
                self.status_action.setText("Server: Stopped")
                font = self.status_action.font()
                font.setBold(True)
                self.status_action.setFont(font)
    
    def closeEvent(self, event):
        """Handle close event - minimize to tray or exit based on context"""
        # Check if this is a force close (from tray menu) vs window close
        from PySide6.QtWidgets import QSystemTrayIcon
        
        # If system tray is available and visible, minimize to tray
        if QSystemTrayIcon.isSystemTrayAvailable() and hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # Check if this is called from tray menu (force close)
            # We need to determine if this is a regular window close or tray menu close
            if not hasattr(self, '_force_close'):
                event.ignore()
                self.hide_to_tray()
                
                # Show notification
                self.tray_icon.showMessage(
                    "DNS Server Manager",
                    "Application minimized to system tray. Double-click to restore.",
                    QSystemTrayIcon.Information,
                    3000
                )
                return
        
        # If we get here, it's a force close from tray menu or no tray available
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
    
    def force_close(self):
        """Force close the application (called from tray menu)"""
        self._force_close = True
        self.close()
    
    def _setup_theme(self):
        """Setup application theme"""
        # Get theme from config
        theme_name = self.config.get("ui.theme", "light")
        theme_manager.set_theme(theme_name)
        
        # Apply stylesheet
        self.setStyleSheet(theme_manager.get_stylesheet())
    
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
        
        # Add minimize to tray button if system tray is available
        if QSystemTrayIcon.isSystemTrayAvailable():
            tray_button = QPushButton("📋")
            tray_button.setToolTip("Minimize to System Tray")
            tray_button.clicked.connect(self.hide_to_tray)
            tray_button.setMaximumWidth(40)
            header_layout.addWidget(tray_button)
        
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
            self.update_tray_status(True)
        else:
            self.status_label.setText("Server Status: Stopped")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            self.update_tray_status(False)
    
    def _update_status(self):
        """Update all status displays"""
        self._update_server_status()
        self.stats_widget.update_stats()
    
    def _show_preferences(self):
        """Show preferences dialog"""
        dialog = PreferencesDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Apply preferences that affect the main window
            settings = dialog.get_settings()
            
            # Apply theme
            if 'ui' in settings and 'theme' in settings['ui']:
                self.menu_manager._change_theme(settings['ui']['theme'])
            
            # Apply window settings
            if 'ui' in settings:
                ui_settings = settings['ui']
                if 'always_on_top' in ui_settings:
                    self.setWindowFlags(
                        self.windowFlags() | Qt.WindowStaysOnTopHint if ui_settings['always_on_top']
                        else self.windowFlags() & ~Qt.WindowStaysOnTopHint
                    )
                    self.show()
            
            self.logger.info("Preferences applied successfully")
    
    def _load_preferences(self):
        """Load and apply preferences at startup"""
        from PySide6.QtCore import QSettings
        settings = QSettings()
        
        # Apply UI preferences
        settings.beginGroup("ui")
        
        # Theme
        theme = settings.value("theme", "light", str)
        self.menu_manager._change_theme(theme)
        
        # Window behavior
        always_on_top = settings.value("always_on_top", False, bool)
        if always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Font size
        font_size = settings.value("font_size", 10, int)
        if font_size != 10:
            font = self.font()
            font.setPointSize(font_size)
            self.setFont(font)
        
        settings.endGroup()
        
        # Apply general preferences
        settings.beginGroup("general")
        
        # Start minimized
        start_minimized = settings.value("start_minimized", False, bool)
        if start_minimized and QSystemTrayIcon.isSystemTrayAvailable():
            # Hide to tray after showing initially
            QTimer.singleShot(100, self.hide_to_tray)
        
        settings.endGroup()
        
        self.logger.info("Startup preferences loaded")
    
    def _show_database_tools(self):
        """Show database tools dialog"""
        QMessageBox.information(self, "Database Tools", "Database tools dialog will be implemented in future versions.")
    
    def _export_configuration(self):
        """Export current configuration"""
        from PySide6.QtWidgets import QFileDialog
        import json
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", "dns_config.json", "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                config_data = {
                    'dns_port': self.config.dns_port,
                    'bind_address': self.config.bind_address,
                    'timeout': self.config.timeout,
                    'max_connections': self.config.max_connections,
                    'log_level': self.config.log_level,
                    'database_file': getattr(self.config, 'database_file', 'dns_records.db')
                }
                
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                QMessageBox.information(self, "Export Successful", f"Configuration exported to {file_path}")
                self.logger.info(f"Configuration exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export configuration: {e}")
                self.logger.error(f"Failed to export configuration: {e}")
    
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
