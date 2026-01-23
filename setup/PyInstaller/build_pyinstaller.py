#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller Build Script for Tuxxle-DNS

This script compiles the Tuxxle-DNS application into a standalone executable using PyInstaller.
PyInstaller is simpler to configure and more reliable for PySide6 applications.

Usage:
    python build_pyinstaller.py [--clean] [--onefile] [--windowed] [--debug]

Options:
    --clean                Clean build directory before building
    --onefile              Create a single executable file
    --windowed             Create windowed application (no console)
    --debug                Enable debug mode
"""

import os
import sys
import shutil
import subprocess
import argparse
import platform
from pathlib import Path

# Project information
PROJECT_NAME = "Tuxxle-DNS"
MAIN_SCRIPT = "main.py"
VERSION_FILE = "core/version.py"
ASSETS_DIR = "assets"
CONFIG_DIR = "config"
DOCS_DIR = "docs"

# Get version from version.py
try:
    version = {}
    with open(VERSION_FILE, "r") as f:
        exec(f.read(), version)
    __version__ = version.get("__version__", "1.1.0")
except Exception as e:
    print(f"Error reading version from {VERSION_FILE}: {e}")
    __version__ = "1.1.0"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"Build {PROJECT_NAME} with PyInstaller")
    parser.add_argument("--clean", action="store_true", help="Clean build directory before building")
    parser.add_argument("--windowed", action="store_true", help="Create windowed application (no console)")
    parser.add_argument("--onefile", action="store_true", help="Create a single executable file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()

def clean_build():
    """Clean build and dist directories."""
    print("Cleaning build directories...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Removed {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {e}")

def get_pyinstaller_command(args):
    """Build the PyInstaller command based on arguments."""
    # Base command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", f"Tuxxle-DNS-{__version__}",
        "--clean",
        "--noconfirm",
        "--noupx"  # Disable UPX to avoid compression issues
    ]
    
    # Add windowed option if requested
    if args.windowed or not args.debug:
        cmd.append("--windowed")
        cmd.append("--noconsole")
    
    # Add onefile option
    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    # Add icon
    icon_path = os.path.join(ASSETS_DIR, "icons", "icon.ico")
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add version info for Windows
    if platform.system() == "Windows":
        version_info = create_version_file()
        if version_info:
            cmd.extend(["--version-file", version_info])
    
    # Add data files and directories
    data_files = [
        (ASSETS_DIR, "assets"),
        (CONFIG_DIR, "config"),
    ]
    
    for src, dst in data_files:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
    
    # Hidden imports for PySide6
    hidden_imports = [
        "PySide6.QtCore",
        "PySide6.QtGui", 
        "PySide6.QtWidgets",
        "PySide6.QtNetwork",
        "core.config",
        "core.dns_server",
        "core.database",
        "core.dns_records",
        "core.version",
        "ui.main_window",
        "lang.language_manager",
        "lang.translations",
        "wand",
        "qrcode",
        "requests",
        "dns.resolver"
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
    # Exclude modules we don't need
    exclude_modules = [
        "PIL",
        "PIL.*",
        "pillow",
        "matplotlib",
        "numpy",
        "scipy"
    ]
    
    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])
    
    # Add main script
    cmd.append(MAIN_SCRIPT)
    
    return cmd

def create_version_file():
    """Create version file for Windows executable."""
    if platform.system() != "Windows":
        return None
    
    # Import version info from core.version
    try:
        version_info = {}
        with open(VERSION_FILE, "r") as f:
            exec(f.read(), version_info)
        app_name = version_info.get("__app_name__", "Tuxxle-DNS")
        app_version = version_info.get("__version__", "1.1.0")
        app_author = version_info.get("__author__", "Nsfr750")
        app_org = version_info.get("__organization__", "Tuxxle")
        app_copyright = version_info.get("__copyright__", "© Copyright 2024-2026 Nsfr750 - All rights reserved.")
    except Exception as e:
        print(f"Warning: Could not read version info: {e}")
        app_name = "Tuxxle-DNS"
        app_version = "1.1.0"
        app_author = "Nsfr750"
        app_org = "Tuxxle"
        app_copyright = "© Copyright 2024-2026 Nsfr750 - All rights reserved."
    
    version_file_content = f"""
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=({app_version.replace('.', ', ')}, 0),
prodvers=({app_version.replace('.', ', ')}, 0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
  ),
  kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'{app_org}'),
    StringStruct(u'FileDescription', u'{app_name} - DNS Server Manager with PySide6 GUI'),
    StringStruct(u'FileVersion', u'{app_version}'),
    StringStruct(u'InternalName', u'{app_name.replace("-", "").replace(" ", "")}'),
    StringStruct(u'LegalCopyright', u'Copyright (c) 2024-2026 {app_author} - All rights reserved.'),
    StringStruct(u'OriginalFilename', u'{app_name}-{app_version}.exe'),
    StringStruct(u'ProductName', u'{app_name}'),
    StringStruct(u'ProductVersion', u'{app_version}'),
    StringStruct(u'Comments', u'DNS Server Manager with internationalization support and comprehensive testing framework'),
    StringStruct(u'LegalTrademarks', u'Tuxxle is a registered trademark of {app_org}'),
    StringStruct(u'PrivateBuild', u'PyInstaller Build'),
    StringStruct(u'SpecialBuild', u'Production Release')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    version_file_path = "version_info.txt"
    try:
        with open(version_file_path, "w", encoding="utf-8") as f:
            f.write(version_file_content)
        return version_file_path
    except Exception as e:
        print(f"Warning: Could not create version file: {e}")
        return None

def create_runtime_hook():
    """Create runtime hook for PySide6."""
    hook_content = """
import os
import sys

# Set Qt plugin path
if hasattr(sys, 'frozen'):
    # We are running in a PyInstaller bundle
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')

# Disable Qt WebEngine components if not needed
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
"""
    
    hook_path = "rthook_pyqt6.py"
    try:
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_content)
        return hook_path
    except Exception as e:
        print(f"Warning: Could not create runtime hook: {e}")
        return None

def run_build(cmd):
    """Run the build command."""
    print("Running PyInstaller...")
    print("Command:", " ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"Build failed with error: {e}")
        return 1

def build():
    """Build the application with PyInstaller."""
    args = parse_arguments()
    
    # Set defaults
    if not hasattr(args, 'onefile'):
        args.onefile = True  # Default to onefile for easier distribution
    
    if args.clean:
        clean_build()
    
    # Create necessary directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    # Create runtime hook
    create_runtime_hook()
    
    # Build the command
    cmd = get_pyinstaller_command(args)
    
    # Run the command
    try:
        return_code = run_build(cmd)
        if return_code == 0:
            print("\n✅ Build completed successfully!")
            
            if args.onefile:
                exe_name = f"Tuxxle-DNS-{__version__}.exe" if platform.system() == "Windows" else f"Tuxxle-DNS-{__version__}"
                exe_path = os.path.join("dist", exe_name)
                if os.path.exists(exe_path):
                    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                    print(f"\n📦 Standalone executable created: {os.path.abspath(exe_path)}")
                    print(f"📏 Size: {size_mb:.1f} MB")
            else:
                print(f"\n📦 Application created in: {os.path.abspath('dist')}")
                
            print("\n🎉 To create a distributable package, you can create a zip archive of the dist directory.")
        else:
            print(f"\n❌ Build failed with error code {return_code}")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred during build: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary files
        for temp_file in ["version_info.txt", "rthook_pyqt6.py"]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == "__main__":
    build()
