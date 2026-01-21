# DNS Server Manager - API Documentation

This document describes the API interface for DNS Server Manager.

## Overview

DNS Server Manager provides a programmatic interface for managing DNS server configuration, records, and operations. The API is designed to be RESTful and follows standard HTTP conventions.

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

Currently, the management interface runs without authentication and requires local access. Remote access should be secured via VPN or SSH tunneling.

## Endpoints

### DNS Server Management

#### Get Server Status
```http
GET /api/v1/server/status
```

**Response:**
```json
{
  "status": "running",
  "uptime": 3600,
  "version": "1.0.0",
  "config_file": "/path/to/config.json"
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

## Version History

- **v1.0.0**: Initial API release
- **v1.1.0**: Added WebSocket support (planned)
- **v1.2.0**: Added authentication (planned)

## Support

For API-related issues and questions, please contact:
- **Email**: info@tuxxle.org
- **GitHub**: https://github.com/Nsfr750/tuxxle-dns

---

© Copyright 2024-2026 Nsfr750 - All rights reserved.
