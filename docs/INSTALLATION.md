# DNS Server Manager - Installation Guide

Complete installation guide for DNS Server Manager on all platforms.

## System Requirements

### Minimum Requirements

- **Python 3.8+** (3.12+ recommended)
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space
- **Network**: TCP port 53 access

### Platform Support

- **Windows 10/11** (x64)
- **macOS 10.15+** (Intel/Apple Silicon)
- **Linux** (Ubuntu 18.04+, CentOS 7+, Debian 10+)

## Installation Methods

### Method 1: Automatic Installation (Recommended)

#### Windows

1. Download and run the installer:

   ```cmd
   install_deps.bat
   ```

2. Follow the on-screen instructions

3. Launch the application:

   ```cmd
   run.bat
   ```

#### Linux/macOS

1. Run the Python installer:

   ```bash
   python install_deps.py
   ```

2. Follow the prompts

3. Launch the application:

   ```bash
   python launcher.py
   ```

### Method 2: Manual Installation

#### Step 1: Clone Repository

```bash
git clone https://github.com/Nsfr750/tuxxle-dns.git
cd tuxxle-dns
```

#### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### Step 3: Install Dependencies

**For Python 3.12+:**

```bash
pip install -r requirements-312.txt
```

**For Python 3.8-3.11:**

```bash
pip install -r requirements.txt
```

#### Step 4: Verify Installation

```bash
python main.py --version
```

## Configuration

### Initial Setup

1. **Launch Application**: Start with administrator privileges
2. **Configure Server**: Set DNS port and bind address
3. **Add Records**: Create initial DNS records
4. **Start Server**: Begin serving DNS queries

### Configuration Files

The application creates a `config/` directory with:

- `config.json` - Main configuration
- `dns_records.db` - SQLite database
- `dns_server.log` - Application logs

## Platform-Specific Instructions

### Windows

#### Administrator Privileges

Required for port 53 (privileged port):

```cmd
# Run as administrator
run.bat
```

#### Firewall Configuration

Add Windows Firewall exception:

```cmd
netsh advfirewall firewall add rule name="DNS Server" dir=in action=allow protocol=TCP localport=53
```

#### Service Installation (Optional)

Install as Windows service:

```cmd
python main.py --install-service
```

### macOS

#### Port Configuration

```bash
# Use alternative port if not running as root
sudo python main.py --port 5353
```

#### Firewall Settings

```bash
# Allow DNS through firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3 --allow
```

### Linux

#### Systemd Service (Optional)

Create systemd service:

```bash
sudo cp scripts/tuxxle-dns.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tuxxle-dns
sudo systemctl start tuxxle-dns
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
   - **Email**: <mailto:info@tuxxle.org>
   - **Security**: <mailto:info@tuxxle.org>

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
