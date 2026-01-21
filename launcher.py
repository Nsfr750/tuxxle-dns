#!/usr/bin/env python3
"""
DNS Server Manager Launcher
A simple launcher script for the DNS Server Manager application
"""

import sys
import os
import traceback
from pathlib import Path

def main():
    """Main launcher function"""
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Check if main.py exists
        main_file = current_dir / "main.py"
        if not main_file.exists():
            print("Error: main.py not found in the current directory")
            print("Please make sure you're running this from the project root directory")
            return 1
        
        # Import and run the main application
        print("Starting DNS Server Manager...")
        
        # Import the main module
        import main
        
        # The main module should handle the rest
        return 0
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nMissing dependencies. Please install the required packages:")
        print("pip install PySide6 dnspython")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
