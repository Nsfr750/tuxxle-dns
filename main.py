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
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('config/dns_server.log'),
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
