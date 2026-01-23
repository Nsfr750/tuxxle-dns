#!/usr/bin/env python3
"""
DNS Server with PySide6 Management Panel
Main entry point for the DNS server application
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from ui.main_window import MainWindow
from core.dns_server import DNSServer
from core.config import Config

def setup_logging():
    """Setup logging configuration"""
    # Determine the correct path for config directory
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent
    
    config_dir = base_path / 'config'
    
    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = config_dir / 'dns_server.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DNS Server Manager")
    app.setOrganizationName("Tuxxle")
    
    # Allow application to run without a window
    app.setQuitOnLastWindowClosed(False)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        config = Config()
        dns_server = DNSServer(config)
        
        main_window = MainWindow(dns_server, config)
        main_window.show()
        
        logger.info("DNS Server Manager started successfully")
        
        return app.exec()
    
    except Exception as e:
        logger.error(f"Failed to start DNS Server Manager: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
