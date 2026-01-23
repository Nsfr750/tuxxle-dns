# DNS Server Manager - API Documentation v1.2.0

This document describes the API interface for DNS Server Manager v1.2.0.

## Overview

DNS Server Manager provides a comprehensive programmatic interface for managing DNS server configuration, records, security, and sustainability features. The API is designed to be RESTful and follows standard HTTP conventions.

## Base URL

```
http://localhost:8080/api/v1.2
```

## Authentication

Currently, the management interface runs without authentication and requires local access. Remote access should be secured via VPN or SSH tunneling.

## New in v1.2.0

- **Green DNS API**: Energy monitoring and carbon footprint tracking
- **Security API**: Advanced security management endpoints
- **Advanced DNS API**: Wildcard records and conditional forwarding
- **Enhanced Statistics**: Comprehensive metrics collection

## Endpoints

### DNS Server Management

#### Get Server Status
```http
GET /api/v1.2/server/status
```

**Response:**
```json
{
  "status": "running",
  "uptime": 3600,
  "version": "1.2.0",
  "config_file": "/path/to/config.json",
  "green_dns": {
    "energy_mode": "balanced",
    "monitoring_active": true,
    "current_power_watts": 85.5
  },
  "security": {
    "rate_limiting_enabled": true,
    "ip_filtering_enabled": true,
    "dnssec_enabled": false
  }
}
```

#### Start DNS Server
```http
POST /api/v1/server/start
```

**Response:**
```json
{
  "success": true,
  "message": "DNS server started successfully"
}
```

#### Stop DNS Server
```http
POST /api/v1/server/stop
```

**Response:**
```json
{
  "success": true,
  "message": "DNS server stopped successfully"
}
```

#### Restart DNS Server
```http
POST /api/v1/server/restart
```

**Response:**
```json
{
  "success": true,
  "message": "DNS server restarted successfully"
}
```

### Configuration Management

#### Get Configuration
```http
GET /api/v1/config
```

**Response:**
```json
{
  "dns": {
    "bind_address": "0.0.0.0",
    "port": 53,
    "upstream_servers": ["8.8.8.8", "8.8.4.4"]
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/dns-server.log"
  }
}
```

#### Update Configuration
```http
PUT /api/v1/config
Content-Type: application/json

{
  "dns": {
    "bind_address": "127.0.0.1",
    "port": 53,
    "upstream_servers": ["1.1.1.1", "1.0.0.1"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

### DNS Records Management

#### List All Records
```http
GET /api/v1/records
```

**Response:**
```json
{
  "records": [
    {
      "id": 1,
      "name": "example.com",
      "type": "A",
      "value": "192.168.1.1",
      "ttl": 300
    },
    {
      "id": 2,
      "name": "www.example.com",
      "type": "CNAME",
      "value": "example.com",
      "ttl": 300
    }
  ]
}
```

#### Get Specific Record
```http
GET /api/v1/records/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "example.com",
  "type": "A",
  "value": "192.168.1.1",
  "ttl": 300
}
```

#### Create DNS Record
```http
POST /api/v1/records
Content-Type: application/json

{
  "name": "test.example.com",
  "type": "A",
  "value": "192.168.1.100",
  "ttl": 300
}
```

**Response:**
```json
{
  "success": true,
  "record_id": 3,
  "message": "DNS record created successfully"
}
```

#### Update DNS Record
```http
PUT /api/v1/records/{id}
Content-Type: application/json

{
  "name": "test.example.com",
  "type": "A",
  "value": "192.168.1.101",
  "ttl": 600
}
```

**Response:**
```json
{
  "success": true,
  "message": "DNS record updated successfully"
}
```

#### Delete DNS Record
```http
DELETE /api/v1/records/{id}
```

**Response:**
```json
{
  "success": true,
  "message": "DNS record deleted successfully"
}
```

### Statistics and Monitoring

#### Get Statistics
```http
GET /api/v1/stats
```

**Response:**
```json
{
  "queries_total": 1500,
  "queries_per_second": 2.5,
  "cache_hits": 1200,
  "cache_misses": 300,
  "uptime": 3600,
  "memory_usage": "45MB"
}
```

#### Get Query Log
```http
GET /api/v1/logs/queries?limit=100&offset=0
```

**Response:**
```json
{
  "queries": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "client": "192.168.1.100",
      "query": "example.com",
      "type": "A",
      "response": "192.168.1.1",
      "duration": 5
    }
  ],
  "total": 1500,
  "limit": 100,
  "offset": 0
}
```

## Error Responses

All endpoints return appropriate HTTP status codes and error messages in JSON format:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required (future)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in future versions.

## WebSocket API (Future)

Real-time updates for DNS queries and server status will be available via WebSocket:

```
ws://localhost:8080/api/v1/ws
```

## SDK and Libraries

### Python Example

```python
import requests

class DNSServerManager:
    def __init__(self, base_url="http://localhost:8080/api/v1"):
        self.base_url = base_url
    
    def get_server_status(self):
        response = requests.get(f"{self.base_url}/server/status")
        return response.json()
    
    def create_record(self, name, record_type, value, ttl=300):
        data = {
            "name": name,
            "type": record_type,
            "value": value,
            "ttl": ttl
        }
        response = requests.post(f"{self.base_url}/records", json=data)
        return response.json()
```

### JavaScript Example

```javascript
class DNSServerManager {
    constructor(baseUrl = 'http://localhost:8080/api/v1') {
        this.baseUrl = baseUrl;
    }
    
    async getServerStatus() {
        const response = await fetch(`${this.baseUrl}/server/status`);
        return await response.json();
    }
    
    async createRecord(name, type, value, ttl = 300) {
        const response = await fetch(`${this.baseUrl}/records`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, type, value, ttl })
        });
        return await response.json();
    }
}
```

### Green DNS Management (NEW in v1.2.0)

#### Get Energy Metrics
```http
GET /api/v1.2/green/energy/metrics
```

**Response:**
```json
{
  "timestamp": 1642972800,
  "cpu_usage": 25.5,
  "memory_usage": 45.2,
  "power_consumption": 85.5,
  "carbon_footprint": 0.000023,
  "energy_per_query": 0.15,
  "queries_processed": 1500
}
```

#### Get Environmental Report
```http
GET /api/v1.2/green/report?days=30
```

**Response:**
```json
{
  "period_days": 30,
  "energy_consumption": {
    "total_energy_kwh": 125.5,
    "daily_energy_kwh": 4.18
  },
  "carbon_footprint": {
    "total_carbon_kg": 29.2,
    "daily_carbon_kg": 0.97
  },
  "environmental_equivalents": {
    "trees_needed": 1.33,
    "car_km_offset": 243.3
  }
}
```

#### Set Energy Mode
```http
POST /api/v1.2/green/energy/mode
```

**Request:**
```json
{
  "mode": "eco"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Energy mode set to eco"
}
```

### Security Management (NEW in v1.2.0)

#### Get Security Status
```http
GET /api/v1.2/security/status
```

**Response:**
```json
{
  "rate_limiting": {
    "enabled": true,
    "max_rps": 100,
    "max_rpm": 1000,
    "blocked_queries": 25
  },
  "ip_filtering": {
    "enabled": true,
    "whitelist_count": 10,
    "blacklist_count": 5
  },
  "dnssec": {
    "enabled": false,
    "signed_zones": 0
  },
  "audit_logging": {
    "enabled": true,
    "events_today": 150
  }
}
```

#### Get Audit Events
```http
GET /api/v1.2/security/audit?limit=100&severity=WARNING
```

**Response:**
```json
{
  "events": [
    {
      "timestamp": 1642972800,
      "type": "ip_blocked",
      "source_ip": "192.168.1.100",
      "query_name": "example.com",
      "action": "blocked",
      "severity": "WARNING"
    }
  ],
  "total": 150,
  "limit": 100
}
```

#### Add IP to Blacklist
```http
POST /api/v1.2/security/ip/blacklist
```

**Request:**
```json
{
  "ip": "192.168.1.100",
  "reason": "Malicious activity detected"
}
```

### Advanced DNS Features (NEW in v1.2.0)

#### Add Wildcard Record
```http
POST /api/v1.2/dns/records/wildcard
```

**Request:**
```json
{
  "name": "*.example.com",
  "type": "A",
  "value": "192.168.1.100",
  "ttl": 300
}
```

#### Add Forwarding Rule
```http
POST /api/v1.2/dns/forwarding/rules
```

**Request:**
```json
{
  "name": "external.com",
  "type": "conditional",
  "servers": ["8.8.8.8", "1.1.1.1"],
  "conditions": {
    "record_exists": {
      "negate": true,
      "record_types": ["A", "AAAA"]
    }
  },
  "priority": 100
}
```

## Version History

- **v1.0.0**: Initial API release
- **v1.1.0**: Added WebSocket support and basic authentication
- **v1.2.0**: Added Green DNS, Security, and Advanced DNS APIs

## Support

For API-related issues and questions, please contact:
- **Email**: info@tuxxle.org
- **GitHub**: https://github.com/Nsfr750/tuxxle-dns

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
