#!/usr/bin/env python3
"""
Security module for DNS Server Manager - Rate limiting, IP filtering, and audit logging
"""

import time
import json
import hashlib
import threading
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging
import ipaddress
from dataclasses import dataclass, asdict
import sqlite3

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: float
    event_type: str
    source_ip: str
    query_name: str
    query_type: str
    action: str
    details: Dict[str, Any]
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL

class RateLimiter:
    """Query rate limiting implementation"""
    
    def __init__(self, max_requests_per_second: int = 100, max_requests_per_minute: int = 1000):
        self.max_rps = max_requests_per_second
        self.max_rpm = max_requests_per_minute
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting storage
        self.request_counts = defaultdict(lambda: defaultdict(int))
        self.request_timestamps = defaultdict(lambda: defaultdict(deque))
        self.lock = threading.Lock()
        
        # Cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_data, daemon=True)
        self.cleanup_thread.start()
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request from client IP is allowed"""
        with self.lock:
            current_time = time.time()
            current_minute = int(current_time // 60)
            current_second = int(current_time)
            
            # Check per-second rate limit
            self._cleanup_timestamps(client_ip, current_second, "second")
            second_count = len(self.request_timestamps[client_ip]["second"])
            
            if second_count >= self.max_rps:
                return False, {
                    "blocked": True,
                    "reason": "rate_limit_exceeded",
                    "limit_type": "per_second",
                    "current": second_count,
                    "max": self.max_rps,
                    "retry_after": 1
                }
            
            # Check per-minute rate limit
            self._cleanup_timestamps(client_ip, current_minute, "minute")
            minute_count = len(self.request_timestamps[client_ip]["minute"])
            
            if minute_count >= self.max_rpm:
                return False, {
                    "blocked": True,
                    "reason": "rate_limit_exceeded",
                    "limit_type": "per_minute",
                    "current": minute_count,
                    "max": self.max_rpm,
                    "retry_after": 60
                }
            
            # Record this request
            self.request_timestamps[client_ip]["second"].append(current_time)
            self.request_timestamps[client_ip]["minute"].append(current_time)
            
            return True, {
                "blocked": False,
                "second_count": second_count + 1,
                "minute_count": minute_count + 1
            }
    
    def _cleanup_timestamps(self, client_ip: str, current_period: int, period_type: str):
        """Clean up old timestamps"""
        timestamps = self.request_timestamps[client_ip][period_type]
        
        if period_type == "second":
            cutoff = current_time = time.time()
            while timestamps and timestamps[0] < cutoff - 1:
                timestamps.popleft()
        else:  # minute
            cutoff_minute = current_period - 1
            cutoff_time = cutoff_minute * 60
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
    
    def _cleanup_old_data(self):
        """Background cleanup of old data"""
        while True:
            try:
                with self.lock:
                    current_time = time.time()
                    current_minute = int(current_time // 60)
                    current_second = int(current_time)
                    
                    # Clean up old data for all IPs
                    ips_to_remove = []
                    for client_ip in list(self.request_timestamps.keys()):
                        # Clean second timestamps
                        second_timestamps = self.request_timestamps[client_ip]["second"]
                        while second_timestamps and second_timestamps[0] < current_time - 1:
                            second_timestamps.popleft()
                        
                        # Clean minute timestamps
                        minute_timestamps = self.request_timestamps[client_ip]["minute"]
                        while minute_timestamps and minute_timestamps[0] < current_time - 60:
                            minute_timestamps.popleft()
                        
                        # Remove IP if no recent activity
                        if not second_timestamps and not minute_timestamps:
                            ips_to_remove.append(client_ip)
                    
                    for ip in ips_to_remove:
                        del self.request_timestamps[ip]
                
                time.sleep(30)  # Cleanup every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in rate limiter cleanup: {e}")
                time.sleep(30)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        with self.lock:
            total_ips = len(self.request_timestamps)
            total_requests_second = sum(len(ts["second"]) for ts in self.request_timestamps.values())
            total_requests_minute = sum(len(ts["minute"]) for ts in self.request_timestamps.values())
            
            return {
                "active_ips": total_ips,
                "requests_last_second": total_requests_second,
                "requests_last_minute": total_requests_minute,
                "max_rps": self.max_rps,
                "max_rpm": self.max_rpm
            }

class IPFilter:
    """IP whitelisting and blacklisting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.whitelist_ranges: List[ipaddress.IPv4Network] = []
        self.blacklist_ranges: List[ipaddress.IPv4Network] = []
        self.lock = threading.RLock()
        
        # Load initial configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load IP filter configuration from file"""
        try:
            config_file = Path("config/ip_filter.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.whitelist = set(config.get("whitelist", []))
                self.blacklist = set(config.get("blacklist", []))
                
                # Load network ranges
                for range_str in config.get("whitelist_ranges", []):
                    self.whitelist_ranges.append(ipaddress.IPv4Network(range_str))
                
                for range_str in config.get("blacklist_ranges", []):
                    self.blacklist_ranges.append(ipaddress.IPv4Network(range_str))
                
                self.logger.info(f"Loaded IP filter config: {len(self.whitelist)} whitelist, {len(self.blacklist)} blacklist")
            
        except Exception as e:
            self.logger.error(f"Error loading IP filter configuration: {e}")
    
    def save_configuration(self):
        """Save IP filter configuration to file"""
        try:
            config_file = Path("config/ip_filter.json")
            config_file.parent.mkdir(exist_ok=True)
            
            config = {
                "whitelist": list(self.whitelist),
                "blacklist": list(self.blacklist),
                "whitelist_ranges": [str(r) for r in self.whitelist_ranges],
                "blacklist_ranges": [str(r) for r in self.blacklist_ranges]
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info("IP filter configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving IP filter configuration: {e}")
    
    def add_to_whitelist(self, ip_or_range: str) -> bool:
        """Add IP or range to whitelist"""
        try:
            with self.lock:
                if '/' in ip_or_range:
                    # Network range
                    network = ipaddress.IPv4Network(ip_or_range)
                    self.whitelist_ranges.append(network)
                else:
                    # Single IP
                    ip = ipaddress.IPv4Address(ip_or_range)
                    self.whitelist.add(str(ip))
                
                self.save_configuration()
                self.logger.info(f"Added to whitelist: {ip_or_range}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding to whitelist: {e}")
            return False
    
    def add_to_blacklist(self, ip_or_range: str) -> bool:
        """Add IP or range to blacklist"""
        try:
            with self.lock:
                if '/' in ip_or_range:
                    # Network range
                    network = ipaddress.IPv4Network(ip_or_range)
                    self.blacklist_ranges.append(network)
                else:
                    # Single IP
                    ip = ipaddress.IPv4Address(ip_or_range)
                    self.blacklist.add(str(ip))
                
                self.save_configuration()
                self.logger.info(f"Added to blacklist: {ip_or_range}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding to blacklist: {e}")
            return False
    
    def remove_from_whitelist(self, ip_or_range: str) -> bool:
        """Remove IP or range from whitelist"""
        try:
            with self.lock:
                if '/' in ip_or_range:
                    # Network range
                    network = ipaddress.IPv4Network(ip_or_range)
                    self.whitelist_ranges = [r for r in self.whitelist_ranges if r != network]
                else:
                    # Single IP
                    self.whitelist.discard(ip_or_range)
                
                self.save_configuration()
                self.logger.info(f"Removed from whitelist: {ip_or_range}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing from whitelist: {e}")
            return False
    
    def remove_from_blacklist(self, ip_or_range: str) -> bool:
        """Remove IP or range from blacklist"""
        try:
            with self.lock:
                if '/' in ip_or_range:
                    # Network range
                    network = ipaddress.IPv4Network(ip_or_range)
                    self.blacklist_ranges = [r for r in self.blacklist_ranges if r != network]
                else:
                    # Single IP
                    self.blacklist.discard(ip_or_range)
                
                self.save_configuration()
                self.logger.info(f"Removed from blacklist: {ip_or_range}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing from blacklist: {e}")
            return False
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if IP is allowed based on whitelist/blacklist"""
        try:
            ip_obj = ipaddress.IPv4Address(client_ip)
            
            with self.lock:
                # Check blacklist first (deny takes precedence)
                if client_ip in self.blacklist:
                    return False, {"blocked": True, "reason": "blacklisted", "type": "exact"}
                
                for range_network in self.blacklist_ranges:
                    if ip_obj in range_network:
                        return False, {"blocked": True, "reason": "blacklisted", "type": "range", "range": str(range_network)}
                
                # If whitelist is empty, allow all (except blacklisted)
                if not self.whitelist and not self.whitelist_ranges:
                    return True, {"blocked": False, "reason": "no_whitelist"}
                
                # Check whitelist
                if client_ip in self.whitelist:
                    return True, {"blocked": False, "reason": "whitelisted", "type": "exact"}
                
                for range_network in self.whitelist_ranges:
                    if ip_obj in range_network:
                        return True, {"blocked": False, "reason": "whitelisted", "type": "range", "range": str(range_network)}
                
                # Not in whitelist and whitelist is active
                return False, {"blocked": True, "reason": "not_whitelisted"}
                
        except Exception as e:
            self.logger.error(f"Error checking IP filter: {e}")
            # Fail open - allow if there's an error
            return True, {"blocked": False, "reason": "error", "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get IP filter statistics"""
        with self.lock:
            return {
                "whitelist_count": len(self.whitelist),
                "blacklist_count": len(self.blacklist),
                "whitelist_range_count": len(self.whitelist_ranges),
                "blacklist_range_count": len(self.blacklist_ranges),
                "whitelist": list(self.whitelist),
                "blacklist": list(self.blacklist),
                "whitelist_ranges": [str(r) for r in self.whitelist_ranges],
                "blacklist_ranges": [str(r) for r in self.blacklist_ranges]
            }

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self, log_file: str = "config/security_audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger(f"{__name__}.audit")
        self.lock = threading.Lock()
        
        # Setup audit logger
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup audit logger with secure configuration"""
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't propagate to root logger
    
    def log_event(self, event: SecurityEvent):
        """Log a security event"""
        try:
            with self.lock:
                # Create log entry
                log_data = {
                    "timestamp": event.timestamp,
                    "datetime": datetime.fromtimestamp(event.timestamp).isoformat(),
                    "event_type": event.event_type,
                    "source_ip": event.source_ip,
                    "query_name": event.query_name,
                    "query_type": event.query_type,
                    "action": event.action,
                    "severity": event.severity,
                    "details": event.details
                }
                
                # Log to file
                log_message = f"{event.event_type.upper()} - {event.source_ip} - {event.query_name} {event.query_type} - {event.action}"
                if event.details:
                    log_message += f" - {json.dumps(event.details)}"
                
                self.logger.log(
                    logging.getLevelName(event.severity),
                    log_message
                )
                
                # Also store in database for querying
                self._store_in_database(log_data)
                
        except Exception as e:
            print(f"Error logging security event: {e}")
    
    def _store_in_database(self, log_data: Dict[str, Any]):
        """Store audit log in database for querying"""
        try:
            db_path = "config/security_audit.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    datetime TEXT,
                    event_type TEXT,
                    source_ip TEXT,
                    query_name TEXT,
                    query_type TEXT,
                    action TEXT,
                    severity TEXT,
                    details TEXT
                )
            ''')
            
            # Insert event
            cursor.execute('''
                INSERT INTO security_events 
                (timestamp, datetime, event_type, source_ip, query_name, query_type, action, severity, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_data["timestamp"],
                log_data["datetime"],
                log_data["event_type"],
                log_data["source_ip"],
                log_data["query_name"],
                log_data["query_type"],
                log_data["action"],
                log_data["severity"],
                json.dumps(log_data["details"])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing audit log in database: {e}")
    
    def query_events(self, 
                     start_time: Optional[float] = None,
                     end_time: Optional[float] = None,
                     source_ip: Optional[str] = None,
                     event_type: Optional[str] = None,
                     severity: Optional[str] = None,
                     limit: int = 1000) -> List[Dict[str, Any]]:
        """Query security events from database"""
        try:
            db_path = "config/security_audit.db"
            if not Path(db_path).exists():
                return []
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM security_events WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            if source_ip:
                query += " AND source_ip = ?"
                params.append(source_ip)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            events = []
            
            for row in rows:
                event = dict(zip(columns, row))
                try:
                    event["details"] = json.loads(event["details"]) if event["details"] else {}
                except:
                    event["details"] = {}
                events.append(event)
            
            conn.close()
            return events
            
        except Exception as e:
            self.logger.error(f"Error querying security events: {e}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get security event statistics"""
        try:
            start_time = time.time() - (days * 24 * 3600)
            events = self.query_events(start_time=start_time)
            
            stats = {
                "total_events": len(events),
                "time_period_days": days,
                "event_types": defaultdict(int),
                "severity_counts": defaultdict(int),
                "top_source_ips": defaultdict(int),
                "top_query_names": defaultdict(int),
                "actions": defaultdict(int)
            }
            
            for event in events:
                stats["event_types"][event["event_type"]] += 1
                stats["severity_counts"][event["severity"]] += 1
                stats["top_source_ips"][event["source_ip"]] += 1
                stats["top_query_names"][event["query_name"]] += 1
                stats["actions"][event["action"]] += 1
            
            # Convert to regular dicts and sort
            stats["event_types"] = dict(sorted(stats["event_types"].items(), key=lambda x: x[1], reverse=True))
            stats["severity_counts"] = dict(stats["severity_counts"])
            stats["top_source_ips"] = dict(sorted(stats["top_source_ips"].items(), key=lambda x: x[1], reverse=True)[:10])
            stats["top_query_names"] = dict(sorted(stats["top_query_names"].items(), key=lambda x: x[1], reverse=True)[:10])
            stats["actions"] = dict(sorted(stats["actions"].items(), key=lambda x: x[1], reverse=True))
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting security statistics: {e}")
            return {}

class SecurityManager:
    """Main security manager combining all security features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = RateLimiter()
        self.ip_filter = IPFilter()
        self.audit_logger = AuditLogger()
        self.enabled = True
        
        self.logger.info("Security manager initialized")
    
    def check_request(self, client_ip: str, query_name: str, query_type: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed by all security measures"""
        if not self.enabled:
            return True, {"allowed": True, "reason": "security_disabled"}
        
        result = {"allowed": True, "checks": {}}
        
        # IP filtering check
        ip_allowed, ip_result = self.ip_filter.is_allowed(client_ip)
        result["checks"]["ip_filter"] = ip_result
        
        if not ip_allowed:
            result["allowed"] = False
            result["reason"] = "ip_blocked"
            
            # Log security event
            event = SecurityEvent(
                timestamp=time.time(),
                event_type="ip_blocked",
                source_ip=client_ip,
                query_name=query_name,
                query_type=query_type,
                action="blocked",
                details=ip_result,
                severity="WARNING"
            )
            self.audit_logger.log_event(event)
            
            return False, result
        
        # Rate limiting check
        rate_allowed, rate_result = self.rate_limiter.is_allowed(client_ip)
        result["checks"]["rate_limit"] = rate_result
        
        if not rate_allowed:
            result["allowed"] = False
            result["reason"] = "rate_limited"
            
            # Log security event
            event = SecurityEvent(
                timestamp=time.time(),
                event_type="rate_limit_exceeded",
                source_ip=client_ip,
                query_name=query_name,
                query_type=query_type,
                action="blocked",
                details=rate_result,
                severity="WARNING"
            )
            self.audit_logger.log_event(event)
            
            return False, result
        
        # Log allowed request
        event = SecurityEvent(
            timestamp=time.time(),
            event_type="query_allowed",
            source_ip=client_ip,
            query_name=query_name,
            query_type=query_type,
            action="allowed",
            details=result,
            severity="INFO"
        )
        self.audit_logger.log_event(event)
        
        return True, result
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            "enabled": self.enabled,
            "rate_limiter": self.rate_limiter.get_stats(),
            "ip_filter": self.ip_filter.get_stats(),
            "audit_statistics": self.audit_logger.get_statistics()
        }
    
    def enable(self):
        """Enable security features"""
        self.enabled = True
        self.logger.info("Security features enabled")
    
    def disable(self):
        """Disable security features"""
        self.enabled = False
        self.logger.warning("Security features disabled")
