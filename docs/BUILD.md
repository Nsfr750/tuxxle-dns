# Build Instructions for Tuxxle-DNS

This document explains how to build Tuxxle-DNS into a standalone executable.

## Prerequisites

- Python 3.10+ installed
- Virtual environment created and dependencies installed

## Quick Start

### Option 1: Run from Source (Recommended for Development)

```bash
# Install dependencies
python install_deps.py

# Run the application
python main.py
# or use the launcher
run_app.bat
```

### Option 2: Build with PyInstaller (Recommended for Distribution)

```bash
# Build as directory (more reliable)
python setup\PyInstaller\build_pyinstaller.py --windowed

# Build as single file (may have issues)
python setup\PyInstaller\build_pyinstaller.py --onefile --windowed
```

### Option 3: Build with Nuitka (Advanced)

**Note**: Nuitka requires Visual Studio Build Tools with Windows SDK to be installed.

```bash
# Install Visual Studio Build Tools with Windows SDK
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

# Build with Nuitka
python setup\Nuitka\build_nuitka.py --onefile
```

## Build Options

### PyInstaller Commands

```bash
# Build as directory (recommended)
python setup\PyInstaller\build_pyinstaller.py --windowed

# Build as single file
python setup\PyInstaller\build_pyinstaller.py --onefile --windowed

# Debug mode (shows console)
python setup\PyInstaller\build_pyinstaller.py --debug

# Clean build
python setup\PyInstaller\build_pyinstaller.py --clean --windowed
```

### Nuitka Commands

```bash
# Single file build
python setup\Nuitka\build_nuitka.py --onefile

# Directory build
python setup\Nuitka\build_nuitka.py

# Clean build
python setup\Nuitka\build_nuitka.py --clean --onefile
```

## Output Locations

### PyInstaller
- **Directory build**: `dist/Tuxxle-DNS-1.1.0/`
- **Single file**: `dist/Tuxxle-DNS-1.1.0.exe`

### Nuitka
- **Single file**: `dist/Tuxxle-DNS-1.1.0.exe`
- **Directory build**: `dist/Tuxxle-DNS-1.1.0/`

## Troubleshooting

### PyInstaller Issues

1. **Missing modules**: Add them to `hidden_imports` list in the build script
2. **Data files not found**: Check that paths in `--add-data` are correct
3. **Application won't start**: Try debug mode to see console output

### Nuitka Issues

1. **Windows SDK headers missing**: Install Visual Studio Build Tools with Windows SDK
2. **Compiler errors**: Ensure MSVC compiler is properly configured
3. **Missing dependencies**: Add them to `--include-package` options

## Recommended Approach

For most users, **PyInstaller directory build** is recommended:

```bash
python setup\PyInstaller\build_pyinstaller.py --windowed
```

This creates a self-contained directory with all dependencies that is:
- More reliable than single-file builds
- Easier to debug if issues occur
- Still portable (can be zipped for distribution)

## File Sizes

Typical output sizes:
- **PyInstaller directory**: ~45MB
- **PyInstaller single file**: ~42MB
- **Nuitka single file**: ~35-40MB (if build succeeds)

## Distribution

To distribute the application:

1. Use PyInstaller directory build
2. Zip the `dist/Tuxxle-DNS-1.1.0/` directory
3. Users can unzip and run `Tuxxle-DNS-1.1.0.exe`

## Version Information

Version is automatically read from `core/version.py`. Update this file to change the application version.

## Dependencies

Main dependencies:
- PySide6 (GUI framework)
- wand (Image processing)
- qrcode (QR code generation)
- requests (HTTP client)
- dnspython (DNS library)

See `requirements.txt` for complete list.
