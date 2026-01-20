#!/usr/bin/env python3
"""
About dialog for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

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
