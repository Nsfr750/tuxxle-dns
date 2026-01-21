#!/usr/bin/env python3
"""
Update management for DNS Server Manager
Handles checking for updates and installing them
"""

import sys
import logging
import json
from typing import Optional, Dict, Any
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QMessageBox, QFrame
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from PySide6.QtGui import QFont

from core import get_version_info

# Try to import requests, fallback to basic functionality if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

class UpdateChecker(QThread):
    """Thread for checking updates in background"""
    update_available = Signal(dict)
    update_not_available = Signal()
    update_error = Signal(str)
    
    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        """Check for updates in background"""
        if not REQUESTS_AVAILABLE:
            self.update_error.emit("requests library not available. Please install: pip install requests")
            return
            
        try:
            # GitHub API URL for releases
            api_url = "https://api.github.com/repos/Nsfr750/tuxxle-dns/releases/latest"
            
            self.logger.info("Checking for updates...")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if self._is_newer_version(latest_version, self.current_version):
                update_info = {
                    'version': latest_version,
                    'name': release_data.get('name', ''),
                    'body': release_data.get('body', ''),
                    'download_url': self._get_download_url(release_data),
                    'release_date': release_data.get('published_at', ''),
                    'assets': release_data.get('assets', [])
                }
                self.update_available.emit(update_info)
            else:
                self.update_not_available.emit()
                
        except requests.RequestException as e:
            self.logger.error(f"Network error checking updates: {e}")
            self.update_error.emit(f"Network error: {e}")
        except Exception as e:
            self.logger.error(f"Error checking updates: {e}")
            self.update_error.emit(f"Error: {e}")
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad with zeros if needed
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> str:
        """Get download URL for current platform"""
        import platform
        
        system = platform.system().lower()
        architecture = platform.architecture()[0].lower()
        
        for asset in release_data.get('assets', []):
            name = asset.get('name', '').lower()
            
            # Look for executable based on platform
            if system == 'windows' and name.endswith('.exe'):
                return asset.get('browser_download_url', '')
            elif system == 'linux' and 'linux' in name:
                return asset.get('browser_download_url', '')
            elif system == 'darwin' and 'macos' in name or 'darwin' in name:
                return asset.get('browser_download_url', '')
        
        # Fallback to source code
        return release_data.get('zipball_url', '')

class UpdateDialog(QDialog):
    """Dialog for showing update information and managing updates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.update_checker = None
        self.update_info = None
        
        self.setWindowTitle("Update Manager")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Update Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Current version info
        current_version = get_version_info()['version']
        current_label = QLabel(f"Current Version: {current_version}")
        current_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(current_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Check for updates button
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self._check_for_updates)
        layout.addWidget(self.check_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Update info area
        self.update_text = QTextEdit()
        self.update_text.setVisible(False)
        self.update_text.setReadOnly(True)
        layout.addWidget(self.update_text)
        
        # Buttons area
        button_layout = QHBoxLayout()
        
        self.download_button = QPushButton("Download Update")
        self.download_button.setVisible(False)
        self.download_button.clicked.connect(self._download_update)
        button_layout.addWidget(self.download_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def _check_for_updates(self):
        """Start checking for updates"""
        current_version = get_version_info()['version']
        
        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Checking for updates...")
        self.update_text.setVisible(False)
        self.download_button.setVisible(False)
        
        # Start update checker thread
        self.update_checker = UpdateChecker(current_version)
        self.update_checker.update_available.connect(self._on_update_available)
        self.update_checker.update_not_available.connect(self._on_no_update)
        self.update_checker.update_error.connect(self._on_update_error)
        self.update_checker.finished.connect(self._on_check_finished)
        self.update_checker.start()
        
    def _on_update_available(self, update_info: Dict[str, Any]):
        """Handle update available"""
        self.update_info = update_info
        
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Update Available: {update_info['version']}")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        
        # Show update information
        update_text = f"""
<b>New Version Available: {update_info['version']}</b>
<b>Release Name:</b> {update_info['name']}
<b>Release Date:</b> {update_info['release_date']}

<b>Release Notes:</b>
{update_info['body']}

<b>Download URL:</b> {update_info['download_url']}
        """.strip()
        
        self.update_text.setHtml(update_text)
        self.update_text.setVisible(True)
        self.download_button.setVisible(True)
        
    def _on_no_update(self):
        """Handle no update available"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("You are using the latest version!")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
    def _on_update_error(self, error_message: str):
        """Handle update check error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error checking for updates: {error_message}")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
    def _on_check_finished(self):
        """Handle update check finished"""
        self.check_button.setEnabled(True)
        if self.update_checker:
            self.update_checker.deleteLater()
            self.update_checker = None
            
    def _download_update(self):
        """Download and install update"""
        if not self.update_info:
            return
            
        try:
            # Try to import webbrowser
            try:
                import webbrowser
                webbrowser.open(self.update_info['download_url'])
                
                QMessageBox.information(
                    self,
                    "Download Started",
                    f"Download started for version {self.update_info['version']}.\n\n"
                    "Please install the new version after download completes."
                )
            except ImportError:
                # Fallback: copy URL to clipboard
                from PySide6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(self.update_info['download_url'])
                
                QMessageBox.information(
                    self,
                    "Download URL",
                    f"Download URL copied to clipboard:\n\n{self.update_info['download_url']}\n\n"
                    "Please paste this URL in your browser to download the update."
                )
                
        except Exception as e:
            self.logger.error(f"Error opening download URL: {e}")
            QMessageBox.critical(
                self,
                "Download Error",
                f"Failed to start download: {e}\n\n"
                f"Please visit:\n{self.update_info['download_url']}"
            )

class UpdateManager:
    """Main update management class"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
    def check_for_updates(self, show_no_update_message: bool = True):
        """Check for updates and show dialog if available"""
        dialog = UpdateDialog(self.parent)
        
        # Auto-check for updates
        QTimer.singleShot(100, dialog._check_for_updates)
        
        result = dialog.exec()
        return result
    
    def show_update_dialog(self):
        """Show update dialog without auto-checking"""
        dialog = UpdateDialog(self.parent)
        dialog.exec()
