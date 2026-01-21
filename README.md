# DNS Server Manager

![Logo](assets/images/logo-text.png)

A comprehensive DNS server management tool with graphical interface, built with PySide6 and Python.

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
├── main.py                 # Application entry point
├── config.json             # Default configuration file
├── version.py              # Version information
├── about.py               # About dialog
├── help.py                # Help dialog
├── sponsor.py             # Sponsor dialog
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── dns_server.py       # DNS server implementation
│   ├── dns_records.py      # DNS record types
│   ├── config.py           # Configuration management
│   └── database.py         # Database operations
├── ui/                    # User interface
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── records_widget.py   # DNS records management
│   ├── stats_widget.py     # Statistics display
│   ├── config_widget.py    # Configuration interface
│   └── logs_widget.py      # Log viewer
├── tests/                 # Test suite
├── docs/                  # Documentation
├── assets/                 # Static assets
│   ├── icons/            # Application icons
│   └── images/           # Images and logos
└── requirements.txt        # Python dependencies
```

## Configuration

### Server Settings

- **DNS Port**: Default 53 (requires administrator privileges)
- **Bind Address**: Default 0.0.0.0 (all interfaces)
- **Query Timeout**: Default 5 seconds
- **Max Connections**: Default 1000

### Logging

- **Log Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log File**: dns_server.log
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

# Format code
black .
```

### Extensions

- Add new DNS record types
- Implement DNSSEC
- Add web interface
- Support for clustering

## License

This project is distributed under the GPLv3 license. See the LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/Nsfr750/tuxxle-dns/issues)
- **Email**: <mailto:nsfr750@yandex.com>
- **Website**: <https://www.tuxxle.org>
- **Security**: <mailto:security@tuxxle.org>

## Donations

If you find this project useful, please consider a donation:

- **PayPal**: <https://paypal.me/3dmega>
- **Monero**: `47Jc6MC47WJVFhiQFYwHyBNQP5BEsjUPG6tc8R37FwcTY8K5Y3LvFzveSXoGiaDQSxDrnCUBJ5WBj6Fgmsfix8VPD4w3gXF`

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
