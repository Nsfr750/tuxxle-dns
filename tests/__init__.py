#!/usr/bin/env python3
"""
Test package for DNS Server Manager
Contains unit tests for all components of the DNS server application
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

__all__ = [
    'test_dns_server',
    'test_records', 
    'test_config',
    'test_ui'
]
