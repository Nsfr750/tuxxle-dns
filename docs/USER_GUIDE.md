# DNS Server Manager - User Guide v1.2.0

This guide provides comprehensive instructions for using DNS Server Manager v1.2.0 to manage your DNS server, records, security, and sustainability features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Web Interface Overview](#web-interface-overview)
3. [DNS Server Management](#dns-server-management)
4. [DNS Records Management](#dns-records-management)
5. [Advanced DNS Features](#advanced-dns-features) (NEW)
6. [Security Management](#security-management) (NEW)
7. [Green DNS & Sustainability](#green-dns-sustainability) (NEW)
8. [Configuration](#configuration)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Application

1. Start the DNS Server Manager:

```bash
python main.py
```

2. The application will open with the main window featuring:
   - Server status indicator
   - Quick statistics
   - Recent DNS queries
   - Configuration summary

### Initial Setup

When you first start the application, you'll see the main dashboard with:

- **Server Control**: Start/stop DNS server
- **Records Management**: Add, edit, delete DNS records
- **Security Dashboard**: Advanced security controls (NEW)
- **Green DNS Monitor**: Energy and sustainability tracking (NEW)
- **Configuration**: System and DNS settings
- **Logs & Stats**: Real-time monitoring

## Web Interface Overview

### Navigation Menu

The application interface consists of several main sections accessible via the menu bar:

- **File**: Application management and exit
- **Edit**: Preferences and settings
- **Tools**: Advanced tools and utilities
  - Database Tools: Database management
  - IP Converter: IPv4/IPv6 conversion (NEW)
  - Security: Advanced security management (NEW)
  - Green DNS: Energy optimization (NEW)
  - Clear Logs: Log management
  - Server Diagnostics: System diagnostics
  - Export Configuration: Settings export
- **Help**: Documentation and support

### Main Tabs

- **Dashboard**: Overview and quick access to common tasks
- **DNS Records**: DNS record management
- **Configuration**: Server and application settings
- **Statistics**: Real-time statistics and monitoring
- **Logs**: Query logs and system logs
- **Help**: Documentation and support

### Dashboard

The dashboard provides:

- **Server Status**: Running/Stopped indicator with uptime
- **Query Statistics**: Total queries, queries per second
- **Recent Activity**: Last 10 DNS queries
- **Quick Actions**: Start/Stop server, Add record buttons
- **System Information**: Version, memory usage, disk space

## DNS Server Management

### Starting and Stopping the Server

#### Via Web Interface

1. Navigate to the **Server** section
2. Use the **Start** button to start the DNS server
3. Use the **Stop** button to stop the DNS server
4. Use **Restart** to restart the server

#### Via Command Line

```bash
# Start server
python main.py --start

# Stop server
python main.py --stop

# Restart server
python main.py --restart

# Check status
python main.py --status
```

### Server Configuration

#### Basic Settings

- **Bind Address**: IP address to listen on (default: 0.0.0.0)
- **Port**: DNS port (default: 53)
- **Upstream Servers**: External DNS servers to forward queries

#### Advanced Settings

- **Cache Size**: Maximum number of cached responses
- **Cache TTL**: Time to live for cached entries
- **Query Timeout**: Maximum time to wait for upstream responses
- **Max Connections**: Maximum concurrent connections

### Server Status Monitoring

The server status page shows:

- **Current Status**: Running/Stopped
- **Uptime**: How long the server has been running
- **Memory Usage**: Current memory consumption
- **Active Connections**: Number of active DNS connections
- **Queries Processed**: Total queries since start

## DNS Records Management

### Supported Record Types

- **A**: IPv4 address records
- **AAAA**: IPv6 address records
- **CNAME**: Canonical name records
- **MX**: Mail exchange records
- **TXT**: Text records
- **NS**: Name server records
- **SOA**: Start of authority records
- **PTR**: Pointer records (reverse DNS)

### Adding DNS Records

#### Via Web Interface (Records)

1. Navigate to the **Records** section
2. Click the **Add Record** button
3. Fill in the record details:
   - **Name**: Domain or subdomain name
   - **Type**: Record type (A, AAAA, CNAME, etc.)
   - **Value**: Record value (IP address, domain name, etc.)
   - **TTL**: Time to live in seconds (default: 300)
4. Click **Save** to create the record

#### Example Records

```text
# A Record
Name: www.example.com
Type: A
Value: 192.168.1.100
TTL: 300

# CNAME Record
Name: blog.example.com
Type: CNAME
Value: www.example.com
TTL: 300

# MX Record
Name: example.com
Type: MX
Value: 10 mail.example.com
TTL: 3600
```

### Editing DNS Records

1. In the **Records** section, find the record you want to edit
2. Click the **Edit** button next to the record
3. Modify the desired fields
4. Click **Save** to update the record

### Deleting DNS Records

1. In the **Records** section, find the record you want to delete
2. Click the **Delete** button next to the record
3. Confirm the deletion in the dialog box

### Bulk Operations

#### Import Records

1. Click the **Import** button in the Records section
2. Choose a file format (CSV, JSON, or BIND zone file)
3. Upload the file or paste the content
4. Review the import preview
5. Click **Import** to add the records

#### Export Records

1. Click the **Export** button in the Records section
2. Choose the export format (CSV, JSON, or BIND)
3. Select which records to export (all or filtered)
4. Download the exported file

### Record Search and Filtering

- **Search**: Use the search box to find records by name or value
- **Filter**: Filter by record type, domain, or TTL
- **Sort**: Sort records by name, type, TTL, or last modified

## Configuration

### General Configuration

Access configuration settings via the **Config** section:

#### DNS Settings

```json
{
  "dns": {
    "bind_address": "0.0.0.0",
    "port": 53,
    "upstream_servers": ["8.8.8.8", "8.8.4.4"],
    "cache_size": 1000,
    "cache_ttl": 300,
    "query_timeout": 5
  }
}
```

#### Web Interface Settings

```json
{
  "web": {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": false,
    "session_timeout": 3600
  }
}
```

#### Logging Settings

```json
{
  "logging": {
    "level": "INFO",
    "file": "dns-server.log",
    "max_size": "10MB",
    "backup_count": 5,
    "query_logging": true
  }
}
```

### Security Configuration

#### Network Security

- **Bind to Specific Interface**: Limit access to specific network interfaces
- **Firewall Rules**: Configure firewall to restrict access
- **Rate Limiting**: Limit queries per IP to prevent abuse

#### Access Control (Future)

- **Authentication**: Username/password protection
- **Role-Based Access**: Different permission levels
- **API Keys**: For programmatic access

### Backup and Restore

#### Configuration Backup

1. Navigate to **Config > Backup**
2. Click **Create Backup**
3. Save the backup file to a secure location

#### Configuration Restore

1. Navigate to **Config > Restore**
2. Upload the backup file
3. Confirm the restore operation

## Monitoring and Logging

### Query Logging

View real-time and historical DNS queries:

#### Live Query Log

1. Navigate to **Logs > Queries**
2. Click **Live View** to see real-time queries
3. Use filters to focus on specific domains or clients

#### Query Log Analysis

The query log shows:

- **Timestamp**: When the query was received
- **Client IP**: Source IP address of the query
- **Query**: Domain name being queried
- **Type**: Query type (A, AAAA, MX, etc.)
- **Response**: Query result or error
- **Duration**: Time taken to process the query

### System Logging

System logs include:

- Server start/stop events
- Configuration changes
- Error messages
- Performance warnings

### Statistics and Metrics

#### Real-time Statistics

- **Queries per Second**: Current query rate
- **Cache Hit Rate**: Percentage of queries served from cache
- **Response Times**: Average and maximum response times
- **Error Rate**: Percentage of failed queries

#### Historical Statistics

View historical data with customizable time ranges:

- **Hourly**: Last 24 hours
- **Daily**: Last 30 days
- **Monthly**: Last 12 months

#### Performance Metrics

- **Memory Usage**: Current and historical memory consumption
- **CPU Usage**: Processor utilization
- **Network I/O**: Network traffic statistics
- **Disk Usage**: Log file and database size

## Advanced Features

### DNSSEC Support (Future)

DNSSEC (DNS Security Extensions) provides:

- **Data Integrity**: Verify DNS responses haven't been tampered with
- **Authentication**: Confirm DNS responses come from authorized sources
- **Trust Chain**: Validate the complete chain of trust

### Conditional Forwarding

Configure rules to forward specific domains to different servers:

```json
{
  "conditional_forwarding": {
    "internal.example.com": "192.168.1.10",
    "external.example.com": "8.8.8.8"
  }
}
```

### Split-Horizon DNS

Provide different responses based on client IP:

```json
{
  "split_horizon": {
    "192.168.1.0/24": {
      "example.com": "192.168.1.100"
    },
    "10.0.0.0/8": {
      "example.com": "10.0.0.100"
    }
  }
}
```

### API Integration

Use the REST API for programmatic access:

```python
import requests

# Get server status
response = requests.get('http://localhost:8080/api/v1/server/status')
status = response.json()

# Add a DNS record
record_data = {
    "name": "test.example.com",
    "type": "A",
    "value": "192.168.1.200",
    "ttl": 300
}
response = requests.post('http://localhost:8080/api/v1/records', json=record_data)
```

## Troubleshooting

### Common Issues

#### DNS Server Not Starting

**Symptoms**: Server status shows "Stopped" or fails to start

**Solutions**:

1. Check if port 53 is already in use:

   ```bash
   netstat -tulpn | grep :53
   ```

2. Run with elevated privileges:

   ```bash
   sudo python main.py
   ```

3. Check configuration file for syntax errors

#### DNS Queries Not Working

**Symptoms**: DNS queries timeout or return errors

**Solutions**:

1. Verify upstream DNS servers are reachable
2. Check firewall rules allow DNS traffic
3. Review query logs for error messages
4. Test with external DNS tools:

   ```bash
   nslookup example.com 127.0.0.1
   dig @127.0.0.1 example.com
   ```

#### Web Interface Not Accessible

**Symptoms**: Cannot access the web interface

**Solutions**:

1. Check if the web server is running
2. Verify port 8080 is not blocked by firewall
3. Check if binding to correct IP address
4. Review web server logs for errors

#### Performance Issues

**Symptoms**: Slow DNS responses or high resource usage

**Solutions**:

1. Increase cache size
2. Optimize upstream DNS servers
3. Monitor system resources
4. Check for DNS amplification attacks

### Debug Mode

Enable debug mode for detailed logging:

```bash
python main.py --debug
```

Or via configuration:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Log Analysis

#### Query Log Analysis

```bash
# Find most queried domains
grep "QUERY" dns-server.log | awk '{print $4}' | sort | uniq -c | sort -nr

# Find error responses
grep "ERROR" dns-server.log

# Monitor query rate
tail -f dns-server.log | grep "QUERY" | wc -l
```

#### System Log Analysis

```bash
# Find recent errors
grep "ERROR" dns-server.log | tail -10

# Monitor server events
tail -f dns-server.log | grep "SERVER"
```

### Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: Review both query and system logs
2. **Verify configuration**: Ensure all settings are correct
3. **Test connectivity**: Use network tools to verify connectivity
4. **Consult documentation**: Review the [API documentation](API.md) and [Installation guide](INSTALLATION.md)
5. **Contact support**:
   - **Email**: <info@tuxxle.org>
   - **Security issues**: <security@tuxxle.org>
   - **GitHub Issues**: <https://github.com/Nsfr750/tuxxle-dns/issues>

### Best Practices

#### Security

- Restrict access to the web interface
- Use firewall rules to limit DNS access
- Regularly update the software
- Monitor query logs for suspicious activity
- Implement rate limiting to prevent abuse

#### Performance

- Use appropriate cache sizes
- Choose fast upstream DNS servers
- Monitor system resources
- Regularly clean old log files
- Optimize record TTL values

#### Maintenance

- Regular backups of configuration
- Monitor disk space usage
- Review and update DNS records
- Test disaster recovery procedures
- Keep documentation up to date

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
