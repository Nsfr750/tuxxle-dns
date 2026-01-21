#!/usr/bin/env python3
"""
Menu management for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import QMenuBar, QMenu, QAction
from PySide6.QtCore import Qt, QSettings
from .themes import theme_manager
from ..lang.language_manager import LanguageManager

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
        
        # Import configuration
        import_action = file_menu.addAction("Import Configuration")
        import_action.triggered.connect(self.main_window._import_configuration)
        file_menu.addSeparator()
        
        # Language submenu
        language_menu = file_menu.addMenu("Language")
        
        # Import language manager
        from ..lang.language_manager import LanguageManager
        self.language_manager = LanguageManager()
        
        # Add language options
        available_languages = self.language_manager.get_available_languages()
        current_language = self.language_manager.current_language
        
        # Add language options
        for lang_code, lang_name in available_languages.items():
            if lang_code in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'zh', 'ar', 'hi', 'ko', 'nl', 'pl', 'tr']:
                lang_action = language_menu.addAction(lang_name)
                lang_action.setCheckable(True)
                lang_action.triggered.connect(lambda checked, code=lang_code: self._change_language(code))
                
                # Set current language as checked
                if lang_code == current_language:
                    lang_action.setChecked(True)
        
        file_menu.addSeparator()
    
    def _setup_edit_menu(self):
        """Setup Edit menu"""
        edit_menu = self.menubar.addMenu("Edit")
        
        # Preferences
        preferences_action = edit_menu.addAction("Preferences")
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.main_window._show_preferences)
        
        self.edit_menu = edit_menu
    
    def _setup_tools_menu(self):
        """Setup Tools menu"""
        tools_menu = self.menubar.addMenu("Tools")
        
        # Database tools
        db_tools_action = tools_menu.addAction("Database Tools")
        db_tools_action.triggered.connect(self.main_window._show_database_tools)
        
        # Clear logs
        clear_logs_action = tools_menu.addAction("Clear Logs")
        clear_logs_action.triggered.connect(self.main_window._clear_logs)
        
        # Server diagnostics
        diagnostics_action = tools_menu.addAction("Server Diagnostics")
        diagnostics_action.triggered.connect(self.main_window._show_server_diagnostics)
        
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
        updates_action.triggered.connect(self.main_window._check_for_updates)
        
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
        
        # Report issue
        report_action = help_menu.addAction("Report Issue")
        report_action.triggered.connect(self.main_window._report_issue)
        
        # Documentation
        docs_action = help_menu.addAction("Documentation")
        docs_action.triggered.connect(self.main_window._open_documentation)
        
        self.help_menu = help_menu
    
    def _change_theme(self, theme_name):
        """Change application theme"""
        try:
            theme_manager.set_theme(theme_name)
            self.main_window.setStyleSheet(theme_manager.get_stylesheet())
            
            # Save preference
            settings = QSettings()
            settings.setValue("ui/theme", theme_name)
            
            self.logger.info(f"Theme changed to: {theme_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to change theme: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "Theme Error", f"Failed to change theme: {e}")
    
    def get_menubar(self):
        """Get menubar widget"""
        return self.menubar
    
    def _change_language(self, language_code: str):
        """Change application language"""
        try:
            self.language_manager.set_language(language_code)
            self.logger.info(f"Language changed to: {language_code}")
            # Update menu check states
            self._update_theme_menu()
            return True
        except Exception as e:
            self.logger.error(f"Failed to change language: {e}")
            return False
