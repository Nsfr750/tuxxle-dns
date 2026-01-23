#!/usr/bin/env python3
"""
Test script to verify the PyInstaller executable works correctly
"""

import subprocess
import time
import sys
from pathlib import Path

def test_executable():
    """Test the PyInstaller executable"""
    exe_path = Path("dist/Tuxxle-DNS-1.1.0/Tuxxle-DNS-1.1.0.exe")
    
    if not exe_path.exists():
        print("❌ Executable not found!")
        return False
    
    print(f"🧪 Testing executable: {exe_path}")
    print(f"📏 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        # Start the executable
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running (successful startup)
        if process.poll() is None:
            print("✅ Application started successfully!")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Application terminated gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Application had to be force-killed")
            
            return True
        else:
            # Process exited, check output
            stdout, _ = process.communicate()
            print(f"❌ Application exited with code {process.returncode}")
            if stdout:
                print(f"Output: {stdout[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False

def check_files():
    """Check that all necessary files are present"""
    dist_dir = Path("dist/Tuxxle-DNS-1.1.0")
    
    required_files = [
        "Tuxxle-DNS-1.1.0.exe",
        "_internal/config/config.json",
        "_internal/config/dns_records.db",
        "_internal/assets/icons/icon.ico"
    ]
    
    print("\n📁 Checking required files:")
    all_present = True
    
    for file_path in required_files:
        full_path = dist_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size if full_path.is_file() else ""
            print(f"✅ {file_path} ({size} bytes)" if size else f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False
    
    return all_present

if __name__ == "__main__":
    print("🔍 Testing PyInstaller executable...")
    print("=" * 50)
    
    # Check files
    files_ok = check_files()
    
    # Test executable
    if files_ok:
        print("\n" + "=" * 50)
        exe_ok = test_executable()
        
        if exe_ok:
            print("\n🎉 All tests passed! The executable is ready for distribution.")
        else:
            print("\n❌ Executable test failed!")
            sys.exit(1)
    else:
        print("\n❌ Some required files are missing!")
        sys.exit(1)
