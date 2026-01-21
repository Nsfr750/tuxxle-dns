#!/usr/bin/env python3
"""
Version information for DNS Server Manager
"""

__version__ = "1.1.0"
__app_name__ = "DNS Server Manager"
__author__ = "Nsfr750"
__organization__ = "Tuxxle"
__copyright__ = "© Copyright 2024-2026 Nsfr750 - All rights reserved."
__website__ = "https://www.tuxxle.org"
__email__ = "info@tuxxle.org"
__license__ = "GPLv3"

def get_version_info():
    """Get complete version information"""
    return {
        "version": __version__,
        "app_name": __app_name__,
        "author": __author__,
        "organization": __organization__,
        "copyright": __copyright__,
        "website": __website__,
        "email": __email__,
        "license": __license__
    }

def get_version_string():
    """Get formatted version string"""
    return f"{__app_name__} v{__version__}"
