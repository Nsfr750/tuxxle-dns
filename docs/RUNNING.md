# DNS Server Manager - Running Instructions

## Quick Start

### Method 1: Direct Python Execution

```bash
python main.py
```

### Method 2: Using the Launcher

```bash
python launcher.py
```

### Method 3: Using the Batch File (Windows)

```bash
run.bat
```

## Compilation Options

### Nuitka Compilation

```bash
python setup/Nuitka/comp.py
```

- **Status**: ✅ Works (creates `TuxxleDNS-1.1.0.exe`)
- **Requirements**: Windows SDK, proper compiler setup
- **Output**: `dist/TuxxleDNS-1.1.0.exe`

### PyInstaller Compilation

```bash
python setup/PyInstaller/comp.py
```

- **Status**: ❌ Currently has issues with PE file creation
- **Requirements**: PyInstaller (`pip install pyinstaller`)
- **Output**: `dist/TuxxleDNS.exe` (currently 0 bytes)

## Dependencies

Make sure you have the required packages installed:

```bash
pip install PySide6 dnspython
```

For compilation:

```bash
pip install nuitka pyinstaller
```

## Troubleshooting

### Import Errors

If you encounter import errors, make sure:

1. You're running from the project root directory
2. All dependencies are installed
3. Python version is compatible (3.11+ recommended)

### Compilation Issues

- **Nuitka**: Requires Windows SDK and proper compiler setup
- **PyInstaller**: May have issues with UPX compression and PE file handling

### Application Crashes

Check the logs in the console output for detailed error information.

## Project Structure

```text
tuxxle-dns/
├── main.py              # Main application entry point
├── launcher.py           # Safe launcher with error handling
├── run.bat              # Windows batch file launcher
├── setup/
│   ├── Nuitka/
│   │   └── comp.py     # Nuitka compilation script
│   └── PyInstaller/
│       └── comp.py     # PyInstaller compilation script
├── dist/                # Compiled executables output
├── core/                # Core DNS server functionality
├── ui/                  # User interface components
├── lang/                # Language translations
└── assets/              # Icons, images, etc.
```

## Recommended Usage

For development and testing:

```bash
python launcher.py
```

For distribution:

1. Use Nuitka compilation (if you have proper compiler setup)
2. Or distribute the source code with `launcher.py`
3. Or create an installer using the batch file approach

## Notes

- The application requires Python 3.11 or higher
- PySide6 is used for the GUI framework
- The DNS server functionality uses dnspython
- All import issues have been resolved in the current version
- The application includes system tray support
- Multi-language support is built-in
