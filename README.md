# DNS Server Manager

![Version](https://img.shields.io/badge/Version-1.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)
![GUI](https://img.shields.io/badge/GUI-PySide6.10-blue)
![License](https://img.shields.io/badge/License-GPLv3-blue)
[![Issues](https://img.shields.io/github/issues/Nsfr750/tuxxle-dns)](https://github.com/Nsfr750/tuxxle-dns/issues)
[![Tests](https://img.shields.io/badge/Tests-Pytest-blue)](https://github.com/Nsfr750/tuxxle-dns)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue)](https://github.com/Nsfr750/tuxxle-dns)

![ss](assets/images/logo_text.png)

A comprehensive DNS server management tool with graphical interface, built with PySide6 and Python. Features complete internationalization, comprehensive testing framework, and professional documentation.

## Features

### DNS Server Capabilities

- **Complete UDP DNS Server**: Native DNS protocol implementation
- **Multiple Record Support**: A, AAAA, CNAME, MX, TXT, NS, SOA, PTR records
- **Multiple Connection Handling**: Support for simultaneous queries
- **Flexible Configuration**: Customizable port, bind address, timeout settings
- **Detailed Logging**: Complete query and response tracking

### Graphical Interface

- **Intuitive Management Panel**: Modern interface with PySide6
- **DNS Record Management**: Add, edit, delete DNS records
- **Real-time Monitoring**: Server statistics and metrics
- **Graphical Configuration**: Server settings via interface
- **Log Visualization**: Real-time logs with filters and export

### Internationalization

- **Multi-language Support**: English, Spanish, French, German, Italian
- **Dynamic Language Switching**: Runtime language changes
- **Translation Management**: Built-in translation system
- **Extensible Language Framework**: Easy addition of new languages

### Testing and Quality

- **Comprehensive Test Suite**: Unit, integration, and E2E tests
- **Automated Testing**: pytest-based testing framework
- **Code Coverage**: Detailed test coverage reporting
- **Quality Assurance**: Professional development standards

### Security and Reliability

- **Input Validation**: Rigorous DNS record control
- **Error Handling**: Robust exception management
- **Complete Logging**: Activity tracking
- **Secure Threading**: Concurrent query management

## Installation

### Prerequisites

- Python 3.11 or higher
- Windows 10/11 (recommended)
- Administrator privileges (for port 53)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Manual Installation

```bash
# Install PySide6
pip install PySide6>=6.10.0

# Install the package
python setup.py install
```

## Usage

### Starting the Application

```bash
# Launch the GUI
python main.py

# Or using the installed script
tuxxle-dns-gui
```

### Initial Configuration

1. **Launch**: Start the application with administrator privileges
2. **Configure**: Use the "Configuration" tab to set port and bind address
3. **Start Server**: Click "Start Server" to start the DNS server
4. **Manage Records**: Use the "DNS Records" tab to add custom records

### DNS Record Management

- **A Records**: `example.com -> 192.168.1.1`
- **AAAA Records**: `example.com -> 2001:db8::1`
- **CNAME Records**: `www.example.com -> example.com`
- **MX Records**: `example.com -> 10 mail.example.com`

## Project Structure

```text
tuxxle-dns/
├── main.py                  # Application entry point
├── config/                  # Configuration and data directory
│   ├── config.json          # Default configuration file
│   ├── dns_records.db       # DNS records database
│   └── dns_server.log       # Application log file
├── setup.py                 # Package setup script
├── requirements.txt         # Python dependencies
├── CHANGELOG.md             # Version changelog
├── README.md                # Project documentation
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── version.py           # Version information
│   ├── dns_server.py        # DNS server implementation
│   ├── dns_records.py       # DNS record types
│   ├── config.py            # Configuration management
│   └── database.py          # Database operations
├── ui/                      # User interface
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── records_widget.py    # DNS records management
│   ├── stats_widget.py      # Statistics display
│   ├── config_widget.py     # Configuration interface
│   ├── logs_widget.py       # Log viewer
│   ├── about.py             # About dialog
│   ├── help.py              # Help dialog
│   ├── sponsor.py           # Sponsor dialog
│   ├── menu.py              # Menu management
│   └── themes.py            # Theme management
├── lang/                    # Language management
│   ├── __init__.py
│   ├── language_manager.py  # Language detection and switching
│   └── translations.py      # Translation strings
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_dns_server.py   # DNS server tests
│   ├── test_records.py      # DNS record tests
│   ├── test_config.py       # Configuration tests
│   └── test_ui.py           # UI component tests
├── docs/                    # Documentation
│   ├── STYLE.md             # Code style guidelines
│   ├── TESTING.md           # Testing procedures
│   ├── TRANSLATION.md       # Translation system docs
│   ├── UPDATING.md          # Update procedures
│   └── VERSIONING.md        # Versioning strategy
└── assets/                  # Static assets
    ├── icons/               # Application icons
    └── images/              # Images and logos
```

## Configuration

### Server Settings

- **DNS Port**: Default 53 (requires administrator privileges)
- **Bind Address**: Default 0.0.0.0 (all interfaces)
- **Query Timeout**: Default 5 seconds
- **Max Connections**: Default 1000

### Logging

- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log File**: config/dns_server.log
- **Log Rotation**: Automatic with maximum size
- **Real-time Preview**: Live log viewing in interface

## Advanced Usage

### Supported DNS Records

#### A Records (IPv4)

```text
Name: server.local
Type: A
Value: 192.168.1.100
TTL: 300
```

#### AAAA Records (IPv6)

```text
Name: server.local
Type: AAAA
Value: 2001:db8::100
TTL: 300
```

#### CNAME Records

```text
Name: www.local
Type: CNAME
Value: server.local
TTL: 300
```

#### MX Records

```text
Name: local
Type: MX
Value: 10 mail.local
TTL: 300
```

## Windows Integration

1. **Windows Service**: Configure as service for automatic startup
2. **Firewall**: Add exceptions for DNS port
3. **Network Settings**: Set as primary DNS in network settings

## Troubleshooting

### Port 53 Already in Use

```bash
# Check what's using port 53
netstat -ano | findstr :53

# Stop Windows DNS service if needed
net stop dnscache
```

### Insufficient Privileges

- Run as Administrator
- Check security policies
- Verify Windows firewall

### Network Issues

- Check IP configuration
- Verify firewall rules
- Test with `nslookup` or `dig`

## Development

### Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=core --cov=ui --cov-report=html

# Format code
black .

# Type checking
mypy .
```

### Extensions

- Add new DNS record types
- Implement DNSSEC
- Add web interface
- Support for clustering
- Add new languages to translation system
- Extend testing coverage
- Implement plugin system

### Documentation

Comprehensive documentation is available in the `docs/` directory:

- **STYLE.md**: Code style guidelines and development standards
- **TESTING.md**: Testing philosophy and procedures
- **TRANSLATION.md**: Translation system documentation
- **UPDATING.md**: Update management and procedures
- **VERSIONING.md**: Semantic versioning strategy

## License

This project is distributed under the GPLv3 license. See the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Nsfr750/tuxxle-dns/issues)
- **Website**: <https://www.tuxxle.org>
- **Security**: <mailto:info@tuxxle.org>
- **Documentation**: [Project Documentation](https://github.com/Nsfr750/tuxxle-dns/tree/main/docs)

## Donations

If you find this project useful, please consider a donation:

- **PayPal**: <https://paypal.me/3dmega>
- **Monero**: `47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF`

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
