# Building DNS Server Manager

This guide explains how to build the DNS Server Manager application into standalone executables.

## Prerequisites

### Required Software

- **Python 3.10+**: Required for the application
- **PyInstaller**: For creating standalone executables
- **Windows 10/11**: Target platform (though builds can work on other OS)

### Development Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `PySide6==6.10.1` - GUI framework
- `PySide6-Addons==6.10.1` - Additional components
- `PySide6-Essentials==6.10.1` - Core components
- `wand==0.6.13` - Image processing
- `qrcode==8.2` - QR code generation
- `pyinstaller==6.12.2` - Build tool
- `nuitka==0.7.1` - Alternative compiler

## Quick Build

### Method 1: Using the Build Script (Recommended)

```bash
# Run the automated build script
python py-build.py

# Or use the batch file (Windows)
build.bat
```

This will:
1. Clean previous builds
2. Check dependencies
3. Build the executable
4. Create an installer package
5. Verify the build

### Method 2: Direct PyInstaller

```bash
# Simple one-file build
pyinstaller --onefile --windowed --icon=assets/icons/icon.ico main.py

# Using the spec file for more control
pyinstaller build.spec
```

## Build Options

### One-File vs One-Directory

**One-File (Default)**:
- Single executable file
- Slower startup
- Easier distribution

**One-Directory**:
- Faster startup
- Multiple files
- Better for debugging

```bash
# One-file build
pyinstaller --onefile --windowed main.py

# One-directory build
pyinstaller --onedir --windowed main.py
```

### Platform-Specific Builds

#### Windows

```bash
# Windows with icon and version info
pyinstaller --onefile --windowed --icon=assets/icons/icon.ico --version-file=version_info.txt main.py
```

#### Linux

```bash
# Linux build
pyinstaller --onefile --windowed main.py
```

#### macOS

```bash
# macOS build with app bundle
pyinstaller --windowed --onefile --osx-bundle-identifier=com.tuxxle.dnsservermanager main.py
```

## Advanced Configuration

### Custom Spec File

The `build.spec` file provides detailed control over the build process:

- **Data Files**: Includes assets, config, and language files
- **Hidden Imports**: Ensures all modules are included
- **Excludes**: Removes unnecessary modules to reduce size
- **Icon**: Sets the application icon
- **Console**: Controls console window visibility

### Optimization Options

```bash
# With UPX compression (smaller executable)
pyinstaller --onefile --upx-dir=/path/to/upx main.py

# Without debug information (smaller size)
pyinstaller --onefile --debug=noimports main.py

# Strip binaries (Linux/macOS)
pyinstaller --onefile --strip main.py
```

## Build Artifacts

### Generated Files

After building, you'll find:

```
dist/
├── DNS_Server_Manager.exe          # Main executable (one-file)
└── DNS_Server_Manager_Dir/         # Directory version (if created)
    ├── DNS_Server_Manager.exe
    ├── _internal/
    └── ...

installer/
├── DNS_Server_Manager.exe          # Copy of executable
├── start.bat                      # Launch script
├── README.md                      # Documentation
├── LICENSE                        # License file
└── CHANGELOG.md                   # Version history
```

### File Sizes

Typical file sizes:
- **One-file executable**: ~50-80 MB
- **Directory build**: ~40-60 MB total
- **With UPX compression**: ~30-50 MB

## Troubleshooting

### Common Issues

#### Module Not Found Errors

```bash
# Add hidden imports to build command
pyinstaller --hidden-import=module_name main.py
```

#### Missing Assets

```bash
# Add data files explicitly
pyinstaller --add-data="assets;assets" main.py
```

#### DLL Errors on Windows

```bash
# Include specific DLLs
pyinstaller --add-binary="path/to/dll.dll;." main.py
```

#### Large File Size

```bash
# Exclude unnecessary modules
pyinstaller --exclude-module=tkinter --exclude-module=matplotlib main.py
```

### Debug Mode

```bash
# Build with console for debugging
pyinstaller --onefile --console main.py

# Or temporarily modify the build script to remove --windowed
```

### Clean Build

```bash
# Remove all build artifacts
python -c "
import os, shutil
for item in ['build', 'dist', '__pycache__']:
    if os.path.exists(item):
        shutil.rmtree(item)
"
```

## Distribution

### Windows

1. **Executable**: Distribute `dist/DNS_Server_Manager.exe`
2. **Installer Package**: Use the `installer/` directory
3. **Dependencies**: None required (standalone)

### Version Information

The executable includes:
- Product name: DNS Server Manager
- Version: 1.1.0.0
- Company: Tuxxle
- Copyright: © 2024-2026 Nsfr750

### Code Signing (Optional)

For distribution, consider code signing:

```bash
# Sign the executable (requires certificate)
signtool sign /f certificate.p12 /p password DNS_Server_Manager.exe
```

## Automated Builds

### GitHub Actions

Create `.github/workflows/build.yml`:

```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Build
      run: python py-build.py
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: dns-server-manager
        path: dist/
```

## Alternative Build Tools

### Nuitka

For potentially better performance:

```bash
python -m nuitka --standalone --onefile --windowed --include-module=PySide6 main.py
```

### cx_Freeze

Alternative to PyInstaller:

```bash
pip install cx_Freeze
python setup.py build
```

## Support

For build-related issues:

- **Documentation**: [Building Guide](https://github.com/Nsfr750/tuxxle-dns/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/Nsfr750/tuxxle-dns/issues)
- **Email**: <mailto:nsfr750@yandex.com>

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
