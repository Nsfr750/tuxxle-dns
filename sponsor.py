#!/usr/bin/env python3
"""
Sponsor dialog for DNS Server Manager
"""

import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor

class SponsorDialog(QDialog):
    """Sponsor dialog showing support information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("Support DNS Server Manager")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the sponsor dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Support DNS Server Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Support information
        support_text = QTextEdit()
        support_text.setReadOnly(True)
        support_content = """
SUPPORT OPEN SOURCE DEVELOPMENT

DNS Server Manager is free and open-source software developed by Nsfr750.
If you find this software useful, please consider supporting its continued development.

WAYS TO SUPPORT:

• PAYPAL DONATION
  Send your donation to: https://paypal.me/3dmega
  Every contribution helps maintain and improve this software.

• CRYPTOCURRENCY
  Monero (XMR): 47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF
  
• GITHUB
  Star the repository: https://github.com/Nsfr750
  Report issues and request features
  Submit pull requests to contribute code

• SPREAD THE WORD
  Tell your friends and colleagues about DNS Server Manager
  Write reviews and testimonials
  Share on social media

• TECHNICAL SUPPORT
  Report bugs and security issues to: info@tuxxle.org
  Contribute to documentation
  Help other users in the community

BENEFITS OF SUPPORT:

• Continued development and updates
• Bug fixes and security patches
• New features and improvements
• Community support and documentation
• Free software for everyone

ORGANIZATION:
Tuxxle - Open Source Software Development
Website: https://www.tuxxle.org
Email: info@tuxxle.org

Thank you for your support! 🙏
"""
        support_text.setPlainText(support_content)
        layout.addWidget(support_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold;")
        layout.addWidget(close_button)
