#!/usr/bin/env python3
"""
Setup script for DNS Server Manager v1.2.0
"""

from setuptools import setup, find_packages
import os
import sys

# Add parent directory to Python path to import core.version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import version information
from core.version import __version__, __app_name__, __author__, __organization__

# Read the README file
def read_readme():
    """Read README file for long description"""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return f"{__app_name__} v1.2.0 - Enterprise DNS Server Manager with Green DNS, Security, and Advanced Features"

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['PySide6>=6.10.0', 'wand>=0.6.13', 'qrcode>=8.2', 'psutil>=5.9.0', 'cryptography>=41.0.7', 'dnspython>=2.6.1']

# Change to parent directory for package discovery
parent_dir = os.path.dirname(os.path.dirname(__file__))
os.chdir(parent_dir)

setup(
    name="tuxxle-dns",
    version=__version__,
    author=__author__,
    author_email="nsfr750@yandex.com",
    description=f"{__app_name__} v1.2.0 - Enterprise DNS Server Manager with Green DNS, Security, and Advanced Features",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750/tuxxle-dns",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Networking",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: English",
        "Natural Language :: Spanish",
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Italian",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            f'{__name__}=main:main',
        ],
        'gui_scripts': [
            f'{__name__}-gui=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.png', '*.jpg', '*.ico', '*.json', '*.md', '*.txt', '*.rst'],
        'assets': ['icons/*', 'images/*'],
        'lang': ['*.py'],
        'docs': ['*.md'],
        'config': ['*.json', '*.db'],
    },
    keywords="dns server management gui pyside6 windows internationalization testing green-dns sustainability energy-monitoring carbon-footprint dnssec security wildcard-records conditional-forwarding enterprise",
    project_urls={
        'Bug Reports': 'https://github.com/Nsfr750/tuxxle-dns/issues',
        'Source': 'https://github.com/Nsfr750/tuxxle-dns',
        'Documentation': 'https://github.com/Nsfr750/tuxxle-dns/tree/main/docs',
        'Website': 'https://www.tuxxle.org',
        'Changelog': 'https://github.com/Nsfr750/tuxxle-dns/blob/main/CHANGELOG.md',
        'License': 'https://github.com/Nsfr750/tuxxle-dns/blob/main/LICENSE',
    },
)
