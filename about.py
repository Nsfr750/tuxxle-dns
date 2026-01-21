#!/usr/bin/env python3
"""
About dialog for DNS Server Manager
"""

import logging
import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("About DNS Server Manager")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the about dialog UI"""
        layout = QVBoxLayout(self)
        
        # Logo
        logo_label = QLabel()
        try:
            # Try multiple path approaches
            import sys
            if hasattr(sys, 'frozen'):
                # PyInstaller executable
                base_path = sys._MEIPASS
                logo_path = os.path.join(base_path, 'assets', 'images', 'logo-text.png')
            else:
                # Regular Python execution
                script_dir = os.path.dirname(os.path.abspath(__file__))
                base_path = os.path.dirname(script_dir)  # Go up one level from ui/
                logo_path = os.path.join(base_path, 'assets', 'images', 'logo-text.png')
            
            self.logger.info(f"Trying to load logo from: {logo_path}")
            
            if os.path.exists(logo_path):
                logo_pixmap = QPixmap(logo_path)
                if not logo_pixmap.isNull():
                    # Scale logo to reasonable size
                    scaled_pixmap = logo_pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                    self.logger.info("Logo loaded successfully")
                else:
                    self.logger.warning("Could not load pixmap from existing file")
                    logo_label.setText("🌐 DNS Server Manager")
                    logo_label.setStyleSheet("font-size: 48px; color: #007bff;")
            else:
                self.logger.warning(f"Logo file not found at: {logo_path}")
                logo_label.setText("🌐 DNS Server Manager")
                logo_label.setStyleSheet("font-size: 48px; color: #007bff;")
                
        except Exception as e:
            self.logger.error(f"Error loading logo: {e}")
            logo_label.setText("🌐 DNS Server Manager")
            logo_label.setStyleSheet("font-size: 48px; color: #007bff;")
        
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Application title
        title_label = QLabel("DNS Server Manager")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description_label = QLabel(
            "A comprehensive DNS server management tool with graphical interface.\n\n"
            "Features:\n"
            "• DNS server management\n"
            "• Record management (A, AAAA, CNAME, MX, TXT, NS)\n"
            "• Real-time statistics\n"
            "• Configuration management\n"
            "• Log monitoring\n"
            "• Database management"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Copyright
        copyright_label = QLabel("© Copyright 2024-2026 Nsfr750 - All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: gray;")
        layout.addWidget(copyright_label)
        
        # Website
        website_label = QLabel("Website: https://www.tuxxle.org")
        website_label.setAlignment(Qt.AlignCenter)
        website_label.setStyleSheet("color: blue;")
        website_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        layout.addWidget(website_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        layout.addWidget(close_button)
        
        layout.addStretch()
