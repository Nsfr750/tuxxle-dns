#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuitka Build Script for Tuxxle-DNS

This script compiles the Tuxxle-DNS application into a standalone executable using Nuitka.
It handles all necessary dependencies, data files, and platform-specific configurations.

Usage:
    python build_nuitka.py [--clean] [--onefile] [--windows-disable-console] [--include-qt-plugins]

Options:
    --clean                Clean build directory before building
    --onefile              Create a single executable file
    --windows-disable-console  Disable console window (Windows only)
    --include-qt-plugins   Include additional Qt plugins (may increase size)
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path

# Project information
PROJECT_NAME = "Tuxxle-DNS"
MAIN_SCRIPT = "main.py"
VERSION_FILE = "core/version.py"
ASSETS_DIR = "assets"
CONFIG_DIR = "config"
DOCS_DIR = "docs"
COPYRIGHT = "© Copyright 2024-2026 Tuxxle"

# Get version from version.py and ensure it's in Windows version format (X.Y.Z.W)
try:
    version = {}
    with open(VERSION_FILE, "r") as f:
        exec(f.read(), version)
    
    # Extract only numeric version parts for Windows file version
    # VERSION_QUALIFIER is ignored for Windows file version as it must be integers only
    version_parts = [
        str(version.get("VERSION_MAJOR", 1)),
        str(version.get("VERSION_MINOR", 1)),
        str(version.get("VERSION_PATCH", 0)),
        "0"  # Build number, always 0 for now
    ]
    VERSION = '.'.join(version_parts[:4])  # Take first 4 parts
    
    # Get the full version string with qualifier for output filename
    __version__ = version.get("__version__", "1.1.0")
    if not __version__:
        __version__ = get_version()
    
except Exception as e:
    print(f"Error reading version from {VERSION_FILE}: {e}")
    VERSION = "1.1.0"
    __version__ = "1.1.0"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"Build {PROJECT_NAME} with Nuitka")
    parser.add_argument("--clean", action="store_true", help="Clean build directory before building")
    parser.add_argument("--windows-disable-console", action="store_true", 
                        help="Disable console window (Windows only)")
    parser.add_argument("--onefile", action="store_true", 
                        help="Create a single executable file")
    parser.add_argument("--debug", action="store_true", 
                        help="Enable debug mode")
    return parser.parse_args()

def clean_build():
    """Clean build and dist directories."""
    print("Cleaning build directories...")
    for dir_name in ['build', 'dist', f'{PROJECT_NAME}.spec']:
        if os.path.exists(dir_name):
            try:
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                else:
                    os.remove(dir_name)
                print(f"Removed {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {e}")

def get_nuitka_command(args):
    """Build the Nuitka command based on arguments."""
    # Base command with minimal required options - using working configuration from build_debug.py
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--assume-yes-for-downloads",
        "--output-dir=dist",
        "--jobs=8",
        f"--output-filename=Tuxxle-DNS-{__version__}",  # Remove .exe here, Nuitka will add it
        "--windows-icon-from-ico=assets/icons/icon.ico",
        "--company-name=Tuxxle",
        "--product-name=Tuxxle-DNS",
        f"--copyright={COPYRIGHT}", # Copyright information
        f"--product-version={VERSION}",
        f"--file-version={VERSION}",
        "--file-description=Tuxxle-DNS",
        "--windows-company-name=Tuxxle",
        f"--windows-file-version={VERSION}",
        f"--windows-product-version={VERSION}",
        "--windows-product-name=Tuxxle-DNS",
        # Use force for console mode in debug, disable for production
        "--windows-console-mode=force" if hasattr(args, 'debug') and args.debug else "--windows-console-mode=disable",
        "--windows-file-description=Tuxxle-DNS",
        "--enable-plugin=pyside6",
        "--remove-output",
        "--no-prefer-source-code",
        "--disable-ccache",
        "--show-progress",
        "--show-modules",
        "--follow-imports",
        # Use MSVC compiler on Windows for better Windows SDK compatibility
        "--msvc=latest" if platform.system() == "Windows" else "--mingw64",
        "--onefile" if args.onefile else "",
        "--include-package=config",
        "--include-package=core",
        "--include-package-data=core",
        # Exclude PIL/Pillow modules to prevent compilation conflicts
        # We use Wand instead of Pillow as specified in requirements
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=PIL.*",
        "--nofollow-import-to=pillow",
        # Include Wand explicitly (our image processing library)
        "--include-package=wand",
        "--include-package=requests",
        "--include-package=qrcode",
        # Include data files with proper relative paths
        f"--include-data-dir=assets=assets",
        f"--include-data-dir=config=config",
        # Explicitly include all necessary files
        f"--include-data-files=assets/icons/icon.ico=assets/icons/icon.ico",
        f"--include-data-files=assets/icons/icon.png=assets/icons/icon.png",
        f"--include-data-files=assets/images/logo_text.png=assets/images/logo_text.png",
        f"--include-data-files=assets/version_info.txt=assets/version_info.txt",
        f"--include-data-files=config/config.json=config/config.json",
        # Add the main script as the last argument
        MAIN_SCRIPT
    ]
    
    # Filter out any empty strings from the command
    return [x for x in cmd if x]

def run_build(cmd):
    """Run the build command."""
    import subprocess
    import os
    
    if platform.system() == "Windows" and "--msvc=latest" in cmd:
        print("Setting up MSVC environment...")
        print("This requires Visual Studio Build Tools with Windows SDK to be installed.")
        
        # Try to find and setup MSVC environment
        vcvars_paths = [
            r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvarsall.bat",
            r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat",
        ]
        
        vcvars_path = None
        for path in vcvars_paths:
            if os.path.exists(path):
                vcvars_path = path
                break
        
        if vcvars_path:
            print(f"Found MSVC at: {vcvars_path}")
            # Create a batch script to setup environment and run Nuitka
            batch_script = f'@echo off\ncall "{vcvars_path}" x64\n' + ' '.join(cmd)
            print("Running with MSVC environment...")
            return subprocess.run(batch_script, shell=True).returncode
        else:
            print("ERROR: Visual Studio Build Tools not found!")
            print("Please install Visual Studio Build Tools with Windows SDK:")
            print("https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
            print("\nFalling back to MinGW64 (may have compatibility issues)...")
            # Replace --msvc=latest with --mingw64
            cmd = ["--mingw64" if x == "--msvc=latest" else x for x in cmd]
    
    print("Running Nuitka...")
    return subprocess.run(cmd).returncode

def build():
    """Build the application with Nuitka."""
    args = parse_arguments()
    
    # Set default for onefile if not provided
    if not hasattr(args, 'onefile'):
        args.onefile = True  # Default to onefile for easier distribution
    
    if args.clean:
        clean_build()
    
    # Create necessary directories
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    # Build the command
    cmd = get_nuitka_command(args)
    
    print("Running command:", " ".join(cmd))
    
    # Run the command
    try:
        return_code = run_build(cmd)
        if return_code == 0:
            print("\nBuild completed successfully!")
            
            if args.onefile:
                # For onefile builds, the executable is already standalone
                exe_name = f"MSR605-{__version__}.exe" if os.name == 'nt' else f"MSR605-{__version__}"
                exe_path = os.path.join("dist", exe_name)
                if os.path.exists(exe_path):
                    print(f"\nStandalone executable created: {os.path.abspath(exe_path)}")
                
                print("\nTo create a distributable package, you can create a zip archive of the build directory.")
            else:
                print(f"\nStandalone executable created in: {os.path.abspath('build')}")
        else:
            print(f"\nBuild failed with error code {return_code}")
            sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during build: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
