# DNS Server Manager - Installation Guide

This guide provides step-by-step instructions for installing DNS Server Manager on various platforms.

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM
- **Storage**: 100MB free disk space
- **Network**: Administrative access to bind to ports 53 (DNS) and 8080 (Web UI)

### Recommended Requirements

- **Operating System**: Ubuntu 20.04+ LTS or Windows 11
- **Python**: 3.10 or higher
- **Memory**: 2GB RAM
- **Storage**: 1GB free disk space
- **Network**: Dedicated network interface

## Installation Methods

### Method 1: Using Git Clone (Recommended)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
```

#### Step 2: Install Dependencies

```bash
python setup/install_deps.py
```

Or manually install dependencies:

```bash
pip install -r requirements.txt
```

#### Step 3: Verify Installation

```bash
python main.py --version
```

### Method 2: Download Release Package

#### Step 1: Download Latest Release

Visit the [GitHub Releases](https://github.com/Nsfr750/tuxxle-dns/releases) page and download the latest release package for your platform.

#### Step 2: Extract the Package

```bash
# For Linux/macOS
tar -xzf tuxxle-dns-v1.0.0.tar.gz
cd tuxxle-dns-v1.0.0

# For Windows
# Use Explorer or 7-Zip to extract the ZIP file
```

#### Step 3: Install Dependencies

```bash
python setup/install_deps.py
```

### Method 3: Using pip (Future)

```bash
pip install tuxxle-dns
```

## Platform-Specific Instructions

### Windows Installation

#### Prerequisites

1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Ensure Python is added to PATH during installation
3. Install Microsoft Visual C++ Build Tools if required

#### Installation Steps

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the installation directory
3. Run the installation commands:

```cmd
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
python setup/install_deps.py
```

#### Windows Service Installation (Optional)

```cmd
python main.py --install-service
```

### macOS Installation

#### Prerequisites

1. Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Python:
```bash
brew install python@3.10
```

#### Installation Steps

```bash
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
python3 setup/install_deps.py
```

#### macOS Service Installation (Optional)

```bash
python3 main.py --install-launchd
```

### Linux Installation

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git

# Clone and install
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
python3 setup/install_deps.py
```

#### CentOS/RHEL/Fedora

```bash
# Install Python and dependencies
sudo yum install python3 python3-pip git

# For Fedora
sudo dnf install python3 python3-pip git

# Clone and install
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
python3 setup/install_deps.py
```

#### systemd Service Installation (Optional)

```bash
sudo python3 main.py --install-systemd
```

## Configuration

### Initial Configuration

1. Copy the example configuration:

```bash
cp config.example.json config.json
```

2. Edit the configuration file:

```json
{
  "dns": {
    "bind_address": "0.0.0.0",
    "port": 53,
    "upstream_servers": ["8.8.8.8", "8.8.4.4"]
  },
  "web": {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": false
  },
  "logging": {
    "level": "INFO",
    "file": "dns-server.log"
  }
}
```

### Environment Variables

You can also configure using environment variables:

```bash
export DNS_BIND_ADDRESS=0.0.0.0
export DNS_PORT=53
export WEB_HOST=127.0.0.1
export WEB_PORT=8080
export LOG_LEVEL=INFO
```

## Running the Application

### Development Mode

```bash
python main.py
```

### Production Mode

```bash
python main.py --production
```

### With Custom Configuration

```bash
python main.py --config /path/to/config.json
```

### Daemon Mode (Linux/macOS)

```bash
nohup python main.py --production > dns-server.log 2>&1 &
```

## Verification

### Check DNS Server

```bash
# Test DNS resolution
nslookup example.com localhost

# Or using dig
dig @localhost example.com
```

### Check Web Interface

Open your web browser and navigate to:
- Local: <http://localhost:8080>
- Remote: <http://your-server-ip:8080>

### Check Logs

```bash
tail -f dns-server.log
```

## Firewall Configuration

### Windows Firewall

```cmd
# Allow DNS (port 53)
netsh advfirewall firewall add rule name="DNS Server" dir=in action=allow protocol=UDP localport=53

# Allow Web UI (port 8080)
netsh advfirewall firewall add rule name="DNS Web UI" dir=in action=allow protocol=TCP localport=8080
```

### Linux (ufw)

```bash
sudo ufw allow 53/udp
sudo ufw allow 8080/tcp
sudo ufw reload
```

### Linux (iptables)

```bash
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save
```

## Troubleshooting

### Common Issues

#### Port 53 Already in Use

```bash
# Check what's using port 53
sudo netstat -tulpn | grep :53

# On Linux, you may need to stop systemd-resolved
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
```

#### Permission Denied

```bash
# Run with appropriate permissions
sudo python main.py

# Or use non-privileged ports (above 1024)
# Edit config.json to use ports 5353 and 8081
```

#### Python Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### DNS Resolution Not Working

1. Check if the DNS server is running:
```bash
ps aux | grep python
```

2. Verify configuration:
```bash
python main.py --check-config
```

3. Test with specific DNS server:
```bash
nslookup example.com 127.0.0.1
```

### Log Analysis

Check the log file for error messages:

```bash
tail -f dns-server.log
grep ERROR dns-server.log
```

### Getting Help

If you encounter issues during installation:

1. Check the [GitHub Issues](https://github.com/Nsfr750/tuxxle-dns/issues)
2. Review the [Security Policy](SECURITY.md)
3. Contact support:
   - **Email**: info@tuxxle.org
   - **Security**: security@tuxxle.org

## Upgrading

### Upgrade from Git

```bash
cd tuxxle-dns
git pull origin main
python setup/install_deps.py
```

### Upgrade from Release

1. Backup your configuration:
```bash
cp config.json config.json.backup
```

2. Download and extract the new version
3. Restore your configuration:
```bash
cp config.json.backup config.json
```

## Uninstallation

### Manual Removal

```bash
# Stop the service
sudo systemctl stop tuxxle-dns  # Linux
# or stop the Windows service

# Remove files
rm -rf /path/to/tuxxle-dns

# Remove systemd service (Linux)
sudo systemctl disable tuxxle-dns
sudo rm /etc/systemd/system/tuxxle-dns.service
```

### Clean Uninstallation

```bash
python setup/clean_pycache.py
```

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
