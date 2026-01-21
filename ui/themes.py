"""
Theme management for DNS Server Manager
"""

from PySide6.QtCore import QObject
from typing import Dict, Any

class ThemeManager(QObject):
    """Theme management system"""
    
    # Light theme colors
    LIGHT_THEME = {
        "background": "#ffffff",
        "secondary_background": "#f8f9fa",
        "tertiary_background": "#e9ecef",
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8",
        "text": "#212529",
        "text_secondary": "#6c757d",
        "text_muted": "#adb5bd",
        "border": "#dee2e6",
        "border_light": "#f8f9fa",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "hover": "#f1f3f4",
        "active": "#e9ecef",
        "disabled": "#e9ecef",
        "log_bg": "#1e1e1e",
        "log_text": "#ffffff",
        "log_debug": "#888888",
        "log_info": "#00ff00",
        "log_warning": "#ffff00",
        "log_error": "#ff6600",
        "log_critical": "#ff0000"
    }
    
    # Dark theme colors
    DARK_THEME = {
        "background": "#1e1e1e",
        "secondary_background": "#2d2d30",
        "tertiary_background": "#3e3e42",
        "primary": "#0078d4",
        "secondary": "#9e9e9e",
        "success": "#107c10",
        "warning": "#ff8c00",
        "danger": "#d13438",
        "info": "#0078d4",
        "text": "#ffffff",
        "text_secondary": "#cccccc",
        "text_muted": "#888888",
        "border": "#3e3e42",
        "border_light": "#2d2d30",
        "shadow": "rgba(0, 0, 0, 0.3)",
        "hover": "#3e3e42",
        "active": "#48484a",
        "disabled": "#3e3e42",
        "log_bg": "#0d1117",
        "log_text": "#c9d1d9",
        "log_debug": "#8b949e",
        "log_info": "#58a6ff",
        "log_warning": "#d29922",
        "log_error": "#f85149",
        "log_critical": "#ff7b72"
    }
    
    def __init__(self):
        super().__init__()
        self._current_theme = "light"
    
    def get_theme(self, theme_name: str = None) -> Dict[str, str]:
        """Get theme colors"""
        if theme_name is None:
            theme_name = self._current_theme
        
        if theme_name == "dark":
            return self.DARK_THEME.copy()
        else:
            return self.LIGHT_THEME.copy()
    
    def set_theme(self, theme_name: str):
        """Set current theme"""
        if theme_name in ["light", "dark"]:
            self._current_theme = theme_name
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self._current_theme
    
    def get_stylesheet(self, theme_name: str = None) -> str:
        """Generate complete stylesheet for theme"""
        theme = self.get_theme(theme_name)
        
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Central Widget */
        QWidget {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        /* Frame */
        QFrame {{
            background-color: {theme['secondary_background']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
        }}
        
        QFrame[frameShape="5"] {{
            background-color: {theme['secondary_background']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {theme['border']};
            background-color: {theme['background']};
        }}
        
        QTabBar::tab {{
            background-color: {theme['tertiary_background']};
            color: {theme['text']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme['background']};
            border-bottom: 2px solid {theme['primary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {theme['hover']};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {theme['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {theme['hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['active']};
        }}
        
        QPushButton:disabled {{
            background-color: {theme['disabled']};
            color: {theme['text_muted']};
        }}
        
        /* Danger Button */
        QPushButton[class="danger"] {{
            background-color: {theme['danger']};
        }}
        
        QPushButton[class="danger"]:hover {{
            background-color: #c82333;
        }}
        
        /* Success Button */
        QPushButton[class="success"] {{
            background-color: {theme['success']};
        }}
        
        QPushButton[class="success"]:hover {{
            background-color: #218838;
        }}
        
        /* Labels */
        QLabel {{
            color: {theme['text']};
            background-color: transparent;
        }}
        
        QLabel[class="status"] {{
            color: {theme['text_secondary']};
            font-weight: bold;
        }}
        
        QLabel[class="title"] {{
            color: {theme['primary']};
            font-weight: bold;
            font-size: 14px;
        }}
        
        /* Line Edit */
        QLineEdit {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {theme['primary']};
        }}
        
        /* Spin Box */
        QSpinBox {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QSpinBox:focus {{
            border: 2px solid {theme['primary']};
        }}
        
        /* Combo Box */
        QComboBox {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {theme['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {theme['text_secondary']};
        }}
        
        /* Table Widget */
        QTableWidget {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            gridline-color: {theme['border']};
            selection-background-color: {theme['primary']};
        }}
        
        QTableWidget::item {{
            padding: 6px;
            border-bottom: 1px solid {theme['border']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {theme['primary']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {theme['tertiary_background']};
            color: {theme['text']};
            padding: 8px;
            border: 1px solid {theme['border']};
            font-weight: bold;
        }}
        
        /* Text Edit */
        QTextEdit {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 8px;
            border-radius: 4px;
        }}
        
        QTextEdit:focus {{
            border: 2px solid {theme['primary']};
        }}
        
        /* Group Box */
        QGroupBox {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {theme['primary']};
            font-weight: bold;
        }}
        
        /* Check Box */
        QCheckBox {{
            color: {theme['text']};
            background-color: transparent;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {theme['border']};
            background-color: {theme['secondary_background']};
            border-radius: 2px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme['primary']};
            border: 1px solid {theme['primary']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {theme['tertiary_background']};
            color: {theme['text']};
            border-top: 1px solid {theme['border']};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border-bottom: 1px solid {theme['border']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {theme['hover']};
        }}
        
        /* Menu */
        QMenu {{
            background-color: {theme['secondary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 20px;
        }}
        
        QMenu::item:selected {{
            background-color: {theme['hover']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {theme['border']};
            margin: 4px 10px;
        }}
        
        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: {theme['tertiary_background']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['text_muted']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme['tertiary_background']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme['text_muted']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['text_secondary']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* Tool Tip */
        QToolTip {{
            background-color: {theme['tertiary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {theme['tertiary_background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme['primary']};
            border-radius: 3px;
        }}
        """

# Global theme manager instance
theme_manager = ThemeManager()
