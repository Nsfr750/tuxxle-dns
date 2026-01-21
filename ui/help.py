#!/usr/bin/env python3
"""
Help dialog for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class HelpDialog(QDialog):
    """Help dialog showing application usage information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("Help - DNS Server Manager")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the help dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("DNS Server Manager - Help")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Help content
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_content = """
DNS SERVER MANAGER - USER GUIDE

GETTING STARTED:
1. Start DNS server using "Start Server" button
2. Configure server settings in Configuration tab
3. Add DNS records in DNS Records tab
4. Monitor server activity in Statistics and Logs tabs

MAIN FEATURES:

• SERVER CONTROL
  - Start/Stop DNS server
  - Real-time status monitoring
  - Port and bind address configuration

• DNS RECORDS MANAGEMENT
  - Add, edit, delete DNS records
  - Support for A, AAAA, CNAME, MX, TXT, NS records
  - Bulk import/export functionality
  - Search and filter capabilities

• STATISTICS
  - Real-time query statistics
  - Request/response monitoring
  - Performance metrics
  - Connection tracking

• CONFIGURATION
  - Server settings (port, bind address, timeout)
  - Logging configuration
  - UI preferences
  - Database settings

• LOGS
  - Real-time log viewing
  - Log level filtering
  - Export logs functionality
  - Search capabilities

• DATABASE
  - Database management interface
  - Backup/restore functionality
  - Performance optimization

MENU OPTIONS:

• FILE MENU
  - Exit: Close application

• EDIT MENU
  - Preferences: Configure application settings

• TOOLS MENU
  - Database Tools: Database management utilities
  - Clear Logs: Clear application logs
  - Export Configuration: Export current settings

• HELP MENU
  - Help: Show this help dialog
  - About: Application information
  - Version: Show version details
  - Sponsor: Support information

TROUBLESHOOTING:

• Server won't start:
  - Check if port 53 is available
  - Verify bind address configuration
  - Check firewall settings

• Records not resolving:
  - Verify record configuration
  - Check DNS server status
  - Review logs for errors

• Performance issues:
  - Monitor statistics tab
  - Check database size
  - Review system resources

For additional support, visit: https://www.tuxxle.org
Security reports: security@tuxxle.org
General inquiries: info@tuxxle.org
"""
        help_text.setPlainText(help_content)
        layout.addWidget(help_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        layout.addWidget(close_button)
