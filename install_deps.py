#!/usr/bin/env python3
"""
Automatic dependency installation script for DNS Server Manager
Detects Python version and installs appropriate dependencies
"""

import sys
import subprocess
import platform

def get_python_version():
    """Get Python version as tuple"""
    return sys.version_info[:2]

def install_requirements():
    """Install requirements based on Python version"""
    py_version = get_python_version()
    print(f"Detected Python version: {'.'.join(map(str, py_version))}")
    
    # Choose requirements file based on Python version
    if py_version >= (3, 12):
        requirements_file = "requirements-312.txt"
    else:
        requirements_file = "requirements.txt"
    
    print(f"Using requirements file: {requirements_file}")
    
    try:
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("\n✅ All dependencies installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ pip not found. Please install pip first.")
        return False
    
    return True

def check_python_version():
    """Check if Python version is supported"""
    py_version = get_python_version()
    
    if py_version < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {'.'.join(map(str, py_version))}")
        return False
    
    print(f"✅ Python version {'.'.join(map(str, py_version))} is supported")
    return True

def main():
    """Main installation function"""
    print("=== DNS Server Manager - Dependency Installer ===")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if install_requirements():
        print("\n🎉 Installation completed successfully!")
        print("\nYou can now run the application with:")
        print("   python main.py")
        print("   python launcher.py")
        print("   run.bat (Windows)")
    else:
        print("\n❌ Installation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
