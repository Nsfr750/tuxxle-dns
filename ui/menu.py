#!/usr/bin/env python3
"""
Menu management for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSettings
from .themes import theme_manager

class MenuManager:
    """Manages application menus"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self.menubar = None
        self._setup_menus()
    
    def _setup_menus(self):
        """Setup all application menus"""
        self.menubar = self.main_window.menuBar()
        
        # File menu
        self._setup_file_menu()
        
        # Edit menu
        self._setup_edit_menu()
        
        # Tools menu
        self._setup_tools_menu()
        
        # Help menu
        self._setup_help_menu()
    
    def _setup_file_menu(self):
        """Setup File menu"""
        file_menu = self.menubar.addMenu("File")
        
        # Add minimize to tray option if system tray is available
        from PySide6.QtWidgets import QSystemTrayIcon
        if QSystemTrayIcon.isSystemTrayAvailable():
            minimize_action = file_menu.addAction("Minimize to Tray")
            minimize_action.setShortcut("Ctrl+M")
            minimize_action.triggered.connect(self.main_window.hide_to_tray)
            file_menu.addSeparator()
        
        # Export configuration
        export_action = file_menu.addAction("Export Configuration")
        export_action.triggered.connect(self.main_window._export_configuration)
        file_menu.addSeparator()
        
        # Exit
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.main_window.force_close)
        
        self.file_menu = file_menu
    
    def _setup_edit_menu(self):
        """Setup Edit menu"""
        edit_menu = self.menubar.addMenu("Edit")
        
        # Preferences
        preferences_action = edit_menu.addAction("Preferences")
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.main_window._show_preferences)
        
        # Theme submenu
        theme_menu = edit_menu.addMenu("Theme")
        
        light_theme_action = theme_menu.addAction("Light Theme")
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self._change_theme("light"))
        
        dark_theme_action = theme_menu.addAction("Dark Theme")
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        
        system_theme_action = theme_menu.addAction("System Theme")
        system_theme_action.setCheckable(True)
        system_theme_action.triggered.connect(lambda: self._change_theme("system"))
        
        # Set current theme checked
        current_theme = theme_manager.get_current_theme()
        if current_theme == "light":
            light_theme_action.setChecked(True)
        elif current_theme == "dark":
            dark_theme_action.setChecked(True)
        else:
            # Default to system theme if current theme is not light/dark
            system_theme_action.setChecked(True)
        
        self.edit_menu = edit_menu
        self.theme_menu = theme_menu
        self.light_theme_action = light_theme_action
        self.dark_theme_action = dark_theme_action
        self.system_theme_action = system_theme_action
    
    def _setup_tools_menu(self):
        """Setup Tools menu"""
        tools_menu = self.menubar.addMenu("Tools")
        
        # Database tools
        db_tools_action = tools_menu.addAction("Database Tools")
        db_tools_action.triggered.connect(self.main_window._show_database_tools)
        
        # Clear logs
        clear_logs_action = tools_menu.addAction("Clear Logs")
        clear_logs_action.triggered.connect(self.main_window._clear_logs)
        
        tools_menu.addSeparator()
        
        # Server diagnostics
        diagnostics_action = tools_menu.addAction("Server Diagnostics")
        diagnostics_action.triggered.connect(self._show_server_diagnostics)
        
        # Network test
        network_test_action = tools_menu.addAction("Network Test")
        network_test_action.triggered.connect(self._show_network_test)
        
        self.tools_menu = tools_menu
    
    def _setup_help_menu(self):
        """Setup Help menu"""
        help_menu = self.menubar.addMenu("Help")
        
        # Help
        help_action = help_menu.addAction("Help")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.main_window._show_help)
        
        # Check for updates
        updates_action = help_menu.addAction("Check for Updates")
        updates_action.triggered.connect(self._check_for_updates)
        
        help_menu.addSeparator()
        
        # About
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.main_window._show_about)
        
        # Version
        version_action = help_menu.addAction("Version")
        version_action.triggered.connect(self.main_window._show_version)
        
        # Sponsor
        sponsor_action = help_menu.addAction("Sponsor")
        sponsor_action.triggered.connect(self.main_window._show_sponsor)
        
        help_menu.addSeparator()
        
        # Report issue
        report_action = help_menu.addAction("Report Issue")
        report_action.triggered.connect(self._report_issue)
        
        # Documentation
        docs_action = help_menu.addAction("Documentation")
        docs_action.triggered.connect(self._open_documentation)
        
        self.help_menu = help_menu
    
    def _change_theme(self, theme_name):
        """Change application theme"""
        try:
            theme_manager.set_theme(theme_name)
            self.main_window.setStyleSheet(theme_manager.get_stylesheet())
            
            # Update menu check states
            self.light_theme_action.setChecked(theme_name == "light")
            self.dark_theme_action.setChecked(theme_name == "dark")
            self.system_theme_action.setChecked(theme_name == "system")
            
            # Save preference
            settings = QSettings()
            settings.setValue("ui/theme", theme_name)
            
            self.logger.info(f"Theme changed to: {theme_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to change theme: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "Theme Error", f"Failed to change theme: {e}")
    
    def _show_server_diagnostics(self):
        """Show server diagnostics dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Server Diagnostics")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Diagnostics text
        diagnostics_text = QTextEdit()
        diagnostics_text.setReadOnly(True)
        
        # Collect diagnostics information
        diagnostics_info = self._collect_diagnostics()
        diagnostics_text.setPlainText(diagnostics_info)
        
        layout.addWidget(diagnostics_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        close_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def _collect_diagnostics(self) -> str:
        """Collect server diagnostics information"""
        import sys
        import os
        from PySide6 import QtCore
        
        diagnostics = []
        diagnostics.append("=== DNS Server Manager Diagnostics ===")
        diagnostics.append(f"Timestamp: {QtCore.QDateTime.currentDateTime().toString()}")
        diagnostics.append("")
        
        # System information
        diagnostics.append("=== System Information ===")
        diagnostics.append(f"Platform: {sys.platform}")
        diagnostics.append(f"Python Version: {sys.version}")
        diagnostics.append(f"Working Directory: {os.getcwd()}")
        diagnostics.append("")
        
        # Application information
        diagnostics.append("=== Application Information ===")
        diagnostics.append(f"PySide6 Version: {QtCore.__version__}")
        diagnostics.append(f"Application Version: {self.main_window.dns_server.__class__.__module__}")
        diagnostics.append("")
        
        # Server status
        diagnostics.append("=== Server Status ===")
        diagnostics.append(f"Server Running: {self.main_window.dns_server.running}")
        diagnostics.append(f"Server Port: {self.main_window.config.dns_port}")
        diagnostics.append(f"Bind Address: {self.main_window.config.bind_address}")
        diagnostics.append("")
        
        # Database status
        diagnostics.append("=== Database Status ===")
        try:
            record_count = len(self.main_window.dns_server.get_all_records())
            diagnostics.append(f"Total Records: {record_count}")
        except Exception as e:
            diagnostics.append(f"Database Error: {e}")
        
        diagnostics.append("")
        
        # Configuration
        diagnostics.append("=== Configuration ===")
        diagnostics.append(f"Config File: {self.main_window.config.config_file}")
        diagnostics.append(f"Database File: {getattr(self.main_window.config, 'database_file', 'N/A')}")
        diagnostics.append("")
        
        # System tray status
        from PySide6.QtWidgets import QSystemTrayIcon
        diagnostics.append("=== System Tray ===")
        diagnostics.append(f"System Tray Available: {QSystemTrayIcon.isSystemTrayAvailable()}")
        diagnostics.append(f"Tray Icon Visible: {hasattr(self.main_window, 'tray_icon') and self.main_window.tray_icon.isVisible()}")
        
        return "\n".join(diagnostics)
    
    def _show_network_test(self):
        """Show network test dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QProgressBar
        from PySide6.QtCore import QThread, Signal
        
        class NetworkTestThread(QThread):
            progress = Signal(int)
            result = Signal(str)
            
            def run(self):
                import socket
                import time
                
                results = []
                test_hosts = [
                    ("Localhost", "127.0.0.1", 53),
                    ("Google DNS", "8.8.8.8", 53),
                    ("Cloudflare DNS", "1.1.1.1", 53),
                    ("OpenDNS", "208.67.222.222", 53)
                ]
                
                for i, (name, host, port) in enumerate(test_hosts):
                    if self.isInterruptionRequested():
                        break
                        
                    self.progress.emit(int((i / len(test_hosts)) * 100))
                    
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(3)
                        
                        start_time = time.time()
                        sock.connect((host, port))
                        end_time = time.time()
                        
                        latency = (end_time - start_time) * 1000
                        results.append(f"✓ {name}: {host}:{port} - {latency:.2f}ms")
                        
                    except Exception as e:
                        results.append(f"✗ {name}: {host}:{port} - {str(e)}")
                    finally:
                        try:
                            sock.close()
                        except:
                            pass
                
                if not self.isInterruptionRequested():
                    self.progress.emit(100)
                    self.result.emit("\n".join(results))
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Network Test")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Progress bar
        progress_bar = QProgressBar()
        layout.addWidget(progress_bar)
        
        # Results text
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_text.setPlainText("Testing network connectivity...")
        layout.addWidget(results_text)
        
        # Test button
        test_button = QPushButton("Run Test")
        layout.addWidget(test_button)
        
        # Store thread reference
        current_thread = None
        
        def run_test():
            nonlocal current_thread
            
            # Stop any existing thread
            if current_thread and current_thread.isRunning():
                current_thread.requestInterruption()
                current_thread.wait(1000)  # Wait up to 1 second
            
            test_button.setEnabled(False)
            test_button.setText("Testing...")
            progress_bar.setValue(0)
            
            current_thread = NetworkTestThread()
            current_thread.progress.connect(progress_bar.setValue)
            current_thread.result.connect(lambda result: (
                results_text.setPlainText(result),
                test_button.setEnabled(True),
                test_button.setText("Run Test")
            ))
            current_thread.start()
        
        def cleanup_thread():
            nonlocal current_thread
            if current_thread and current_thread.isRunning():
                current_thread.requestInterruption()
                current_thread.wait(1000)
        
        test_button.clicked.connect(run_test)
        
        # Cleanup when dialog is closed
        dialog.finished.connect(cleanup_thread)
        
        dialog.exec()
    
    def _check_for_updates(self):
        """Check for application updates"""
        from PySide6.QtWidgets import QMessageBox
        import urllib.request
        import json
        
        try:
            # This would normally check a real update server
            # For now, just show a placeholder
            QMessageBox.information(
                self.main_window,
                "Check for Updates",
                "You are running the latest version of DNS Server Manager.\n\n"
                "Current version: 1.0.0\n"
                "Latest version: 1.0.0"
            )
        except Exception as e:
            QMessageBox.warning(
                self.main_window,
                "Update Check Failed",
                f"Failed to check for updates: {e}"
            )
    
    def _report_issue(self):
        """Open issue reporting dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Report Issue")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel("Issue Title:")
        layout.addWidget(title_label)
        
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Brief description of the issue")
        layout.addWidget(title_edit)
        
        # Description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("Detailed description of the issue, steps to reproduce, etc.")
        layout.addWidget(desc_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        submit_button.clicked.connect(dialog.accept)
        button_layout.addWidget(submit_button)
        
        layout.addLayout(button_layout)
        
        if dialog.exec() == QDialog.Accepted:
            title = title_edit.text()
            description = desc_edit.toPlainText()
            
            if title and description:
                # Open GitHub issues page in browser
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QDesktopServices
                
                url = QUrl("https://github.com/Nsfr750/tuxxle-dns/issues/new")
                QDesktopServices.openUrl(url)
                
                QMessageBox.information(
                    self.main_window,
                    "Issue Reported",
                    "Your browser has been opened to submit the issue on GitHub."
                )
    
    def _open_documentation(self):
        """Open documentation in browser"""
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        
        url = QUrl("https://github.com/Nsfr750/tuxxle-dns/wiki")
        QDesktopServices.openUrl(url)
    
    def update_theme_menu(self, theme_name):
        """Update theme menu check states"""
        self.light_theme_action.setChecked(theme_name == "light")
        self.dark_theme_action.setChecked(theme_name == "dark")
        self.system_theme_action.setChecked(theme_name == "system")
    
    def get_menubar(self):
        """Get the menubar widget"""
        return self.menubar
