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
DNS SERVER MANAGER - USER GUIDE v1.2.0

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
  - Wildcard records support (*.example.com)
  - Bulk import/export functionality
  - Search and filter capabilities

• ADVANCED DNS FEATURES
  - Wildcard Records: Support for DNS wildcards (* and ? patterns)
  - Conditional Forwarding: Smart query forwarding based on conditions
  - DNSSEC Support: Digital signatures for DNS records
  - Query Rate Limiting: Protection against DoS attacks
  - IP Filtering: Whitelist/blacklist access control

• SECURITY MANAGEMENT
  - Comprehensive security dashboard
  - Real-time threat monitoring
  - Audit logging with database storage
  - Secure configuration encryption
  - Rate limiting and IP filtering controls

• GREEN DNS (NEW)
  - Energy usage optimization and monitoring
  - Carbon footprint tracking and reporting
  - Environmental impact analysis
  - Green hosting recommendations
  - Energy efficiency modes (Performance, Balanced, Eco, Ultra Eco)

• STATISTICS
  - Real-time query statistics
  - Request/response monitoring
  - Performance metrics
  - Connection tracking
  - Energy consumption metrics
  - Security event statistics

• CONFIGURATION
  - Server settings (port, bind address, timeout)
  - Logging configuration
  - UI preferences
  - Database settings
  - Security policy configuration
  - Green DNS optimization settings

• LOGS
  - Real-time log viewing
  - Log level filtering
  - Export logs functionality
  - Search capabilities
  - Security audit logs

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
  - IP Converter: IPv4 to IPv6 conversion tools
  - Security: Advanced security management
  - Green DNS: Energy optimization and sustainability
  - Clear Logs: Clear application logs
  - Server Diagnostics: System diagnostics
  - Export Configuration: Export current settings

• HELP MENU
  - Help: Show this help dialog
  - About: Application information
  - Version: Show version details
  - Sponsor: Support information

NEW FEATURES IN v1.2.0:

🌱 GREEN DNS
- Real-time energy consumption monitoring
- Carbon footprint calculation and tracking
- Environmental impact reporting
- Green hosting recommendations
- Energy optimization modes

🔒 ADVANCED SECURITY
- DNSSEC support with key management
- Query rate limiting per second/minute
- IP whitelisting/blacklisting with CIDR support
- Comprehensive audit logging
- Secure encrypted configuration storage

🚀 DNS ENHANCEMENTS
- Wildcard record support (*.example.com)
- Conditional forwarding with multiple conditions
- Time-based, client IP, and query type forwarding
- Enhanced caching and performance optimization

TROUBLESHOOTING:

• Server won't start:
  - Check if port 53 is available
  - Verify bind address configuration
  - Check firewall settings

• Records not resolving:
  - Verify record configuration
  - Check DNS server status
  - Review logs for errors
  - Check wildcard patterns if used

• Performance issues:
  - Monitor statistics tab
  - Check database size
  - Review system resources
  - Consider energy optimization mode

• Security concerns:
  - Review security dashboard
  - Check audit logs
  - Verify rate limiting settings
  - Update DNSSEC keys if needed

• Energy optimization:
  - Use Green DNS dialog for monitoring
  - Select appropriate energy mode
  - Review green recommendations
  - Monitor carbon footprint trends

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
