#!/usr/bin/env python3
"""
Setup script for DNS Server Manager
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "DNS Server Manager with PySide6 GUI"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['PySide6>=6.6.0']

setup(
    name="dns-server-manager",
    version="1.0.0",
    author="Nsfr750",
    author_email="nsfr750@yandex.com",
    description="DNS Server with PySide6 Management Panel for Windows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Nsfr750",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'dns-server-manager=main:main',
        ],
        'gui_scripts': [
            'dns-server-gui=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.png', '*.jpg', '*.ico', '*.json'],
    },
    keywords="dns server management gui pyside6 windows",
    project_urls={
        'Bug Reports': 'https://github.com/Nsfr750/issues',
        'Source': 'https://github.com/Nsfr750',
        'Website': 'https://www.tuxxle.org',
    },
)
