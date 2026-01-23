#!/usr/bin/env python3
"""
Conditional DNS forwarding support for DNS Server Manager
"""

import socket
import struct
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from .dns_records import DNSRecord, DNSRecordType, DNSResponse
from .config import Config

class ForwardingPolicy(Enum):
    """Forwarding policy types"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"

@dataclass
class ForwardingRule:
    """DNS forwarding rule"""
    name: str
    rule_type: ForwardingPolicy
    target_servers: List[str]
    conditions: Dict[str, Any]  # Conditions for conditional forwarding
    priority: int = 100
    ttl: int = 300
    enabled: bool = True
    created_at: float = 0
    last_used: float = 0
    usage_count: int = 0

class ConditionalForwarding:
    """Conditional DNS forwarding based on various criteria"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules: List[ForwardingRule] = []
        self.cache: Dict[str, Tuple[List[str], float]] = {}  # name -> (servers, timestamp)
        self.cache_ttl = 300  # 5 minutes
        self.forwarders: Dict[str, List[str]] = {}  # name -> [servers]
        self.conditions: Dict[str, Callable] = {
            'time_based': self._time_based_condition,
            'client_ip': self._client_ip_condition,
            'query_type': self._query_type_condition,
            'record_exists': self._record_exists_condition,
            'custom': self._custom_condition
        }
        self._load_forwarding_rules()
    
    def _load_forwarding_rules(self):
        """Load forwarding rules from configuration"""
        try:
            # Load from config file
            config = Config()
            forwarding_config = config.get('forwarding', {})
            
            for rule_config in forwarding_config.get('rules', []):
                rule = ForwardingRule(
                    name=rule_config.get('name', ''),
                    rule_type=ForwardingPolicy(rule_config.get('type', 'allow')),
                    target_servers=rule_config.get('servers', []),
                    conditions=rule_config.get('conditions', {}),
                    priority=rule_config.get('priority', 100),
                    ttl=rule_config.get('ttl', 300),
                    enabled=rule_config.get('enabled', True),
                    created_at=rule_config.get('created_at', time.time()),
                    last_used=rule_config.get('last_used', 0),
                    usage_count=rule_config.get('usage_count', 0)
                )
                self.rules.append(rule)
            
            # Load default forwarders
            self.forwarders = forwarding_config.get('forwarders', {})
            
            # Sort rules by priority (lower number = higher priority)
            self.rules.sort(key=lambda r: r.priority)
            
            self.logger.info(f"Loaded {len(self.rules)} forwarding rules")
            
        except Exception as e:
            self.logger.error(f"Error loading forwarding rules: {e}")
            # Load default rules
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default forwarding rules"""
        self.rules = []
        self.forwarders = {}
        
        # Add some common default forwarders if not configured
        default_forwarders = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "208.67.222.222",  # OpenDNS
        ]
        
        # Default rule for external domains
        external_rule = ForwardingRule(
            name="*",
            rule_type=ForwardingPolicy.CONDITIONAL,
            target_servers=default_forwarders,
            conditions={
                'type': 'record_exists',
                'negate': True,
                'record_types': ['A', 'AAAA', 'MX', 'TXT']
            },
            priority=1000,
            enabled=True
        )
        self.rules.append(external_rule)
        
        self.logger.info("Loaded default forwarding rules")
    
    def should_forward(self, query_name: str, query_type: str, client_ip: str, 
                      local_records: List[DNSRecord]) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """Determine if query should be forwarded and to which servers"""
        
        try:
            # Check if we have local records
            has_local_records = len(local_records) > 0
            
            # Find matching rules
            matching_rules = []
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                if self._rule_matches(rule, query_name, query_type, client_ip, has_local_records):
                    matching_rules.append(rule)
            
            if not matching_rules:
                return False, None, None
            
            # Get the highest priority rule (lowest priority number)
            rule = matching_rules[0]
            
            # Update rule statistics
            rule.last_used = time.time()
            rule.usage_count += 1
            
            # Check cache first
            cache_key = f"{query_name}:{query_type}"
            if cache_key in self.cache:
                cached_servers, cache_time = self.cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    return True, cached_servers, rule.name
            
            # Use rule's target servers
            servers = rule.target_servers if rule.target_servers else self.forwarders.get(rule.name, [])
            
            # Cache the result
            self.cache[cache_key] = (servers, time.time())
            
            self.logger.debug(f"Forwarding {query_name} {query_type} to {servers} (rule: {rule.name})")
            return True, servers, rule.name
            
        except Exception as e:
            self.logger.error(f"Error checking forwarding for {query_name}: {e}")
            return False, None, None
    
    def _rule_matches(self, rule: ForwardingRule, query_name: str, query_type: str, client_ip: str, 
                    has_local_records: bool) -> bool:
        """Check if a rule matches the query conditions"""
        try:
            # Check name pattern matching
            if not self._match_name_pattern(rule.name, query_name):
                return False
            
            # Check rule type
            if rule.rule_type == ForwardingPolicy.DENY:
                return False
            
            elif rule.rule_type == ForwardingPolicy.ALLOW:
                return True
            
            elif rule.rule_type == ForwardingPolicy.CONDITIONAL:
                return self._evaluate_conditions(rule.conditions, query_name, query_type, client_ip, has_local_records)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.name}: {e}")
            return False
    
    def _match_name_pattern(self, pattern: str, name: str) -> bool:
        """Check if name matches the rule pattern"""
        if pattern == "*":
            return True
        elif pattern.startswith("*."):
            # Subdomain pattern
            domain = pattern[2:]
            return name == domain or name.endswith("." + domain)
        elif pattern.endswith("*."):
            # Parent domain pattern
            domain = pattern[:-2]
            return name == domain or name.startswith(domain + ".")
        else:
            # Exact match
            return name == pattern
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], query_name: str, query_type: str,
                           client_ip: str, has_local_records: bool) -> bool:
        """Evaluate forwarding conditions"""
        try:
            for condition_type, condition_value in conditions.items():
                if condition_type in self.conditions:
                    condition_func = self.conditions[condition_type]
                    
                    if condition_type == 'custom':
                        # Custom condition with lambda function
                        if callable(condition_value):
                            return condition_value(query_name, query_type, client_ip, has_local_records)
                    else:
                        return condition_func(query_name, query_type, client_ip, has_local_records, condition_value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {e}")
            return True
    
    def _time_based_condition(self, query_name: str, query_type: str, client_ip: str, 
                           has_local_records: bool, condition_value: Any) -> bool:
        """Time-based forwarding condition"""
        try:
            current_time = time.localtime()
            current_hour = current_time.tm_hour
            
            # Parse time ranges like "9-17" or "22-6"
            if isinstance(condition_value, str):
                if '-' in condition_value:
                    start, end = map(int, condition_value.split('-'))
                    return start <= current_hour <= end
                else:
                    return current_hour == int(condition_value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in time-based condition: {e}")
            return True
    
    def _client_ip_condition(self, query_name: str, query_type: str, client_ip: str, 
                           has_local_records: bool, condition_value: Any) -> bool:
        """Client IP-based forwarding condition"""
        try:
            if isinstance(condition_value, list):
                return client_ip in condition_value
            elif isinstance(condition_value, str):
                if '/' in condition_value:
                    # CIDR range check
                    import ipaddress
                    try:
                        network = ipaddress.IPv4Network(condition_value)
                        client_addr = ipaddress.IPv4Address(client_ip)
                        return client_addr in network
                    except:
                        return False
                else:
                    return client_ip == condition_value
            elif isinstance(condition_value, dict):
                # Complex IP conditions
                if 'range' in condition_value:
                    ip_range = condition_value['range']
                    if '/' in ip_range:
                        import ipaddress
                        network = ipaddress.IPv4Network(ip_range)
                        client_addr = ipaddress.IPv4Address(client_ip)
                        return client_addr in network
                
                if 'not' in condition_value:
                    excluded_ips = condition_value['not']
                    return client_ip not in excluded_ips
                
                if 'allowed' in condition_value:
                    allowed_ips = condition_value['allowed']
                    return client_ip in allowed_ips
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in client IP condition: {e}")
            return True
    
    def _query_type_condition(self, query_name: str, query_type: str, client_ip: str, 
                           has_local_records: bool, condition_value: Any) -> bool:
        """Query type-based forwarding condition"""
        try:
            if isinstance(condition_value, list):
                return query_type in condition_value
            elif isinstance(condition_value, str):
                return query_type == condition_value
            elif isinstance(condition_value, dict):
                if 'types' in condition_value:
                    types = condition_value['types']
                    return query_type in types
                
                if 'exclude' in condition_value:
                    excluded_types = condition_value['exclude']
                    return query_type not in excluded_types
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in query type condition: {e}")
            return True
    
    def _record_exists_condition(self, query_name: str, query_type: str, client_ip: str, 
                             has_local_records: bool, condition_value: Any) -> bool:
        """Record existence condition"""
        try:
            negate = condition_value.get('negate', False) if isinstance(condition_value, dict) else False
            
            has_record = has_local_records
            
            if 'record_types' in condition_value:
                # Check for specific record types
                record_types = condition_value['record_types']
                has_record = any(r.record_type in record_types for r in local_records)
            
            result = has_record
            
            if negate:
                return not result
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"Error in record exists condition: {e}")
            return True
    
    def _custom_condition(self, query_name: str, query_type: str, client_ip: str, 
                        has_local_records: bool, condition_value: Any) -> bool:
        """Custom forwarding condition"""
        # This would be loaded from configuration
        return True
    
    def forward_query(self, query_data: bytes, servers: List[str], timeout: int = 5) -> Optional[bytes]:
        """Forward query to specified servers"""
        try:
            for server in servers:
                try:
                    # Create socket for forwarding
                    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    forward_socket.settimeout(timeout)
                    
                    # Send query to forwarder
                    forward_socket.sendto(query_data, (server, 53))
                    
                    # Wait for response
                    response_data, _ = forward_socket.recvfrom(512)
                    
                    forward_socket.close()
                    
                    self.logger.debug(f"Forwarded query to {server}, got response of {len(response_data)} bytes")
                    return response_data
                    
                except socket.timeout:
                    self.logger.warning(f"Timeout forwarding to {server}")
                    continue
                except Exception as e:
                    self.logger.error(f"Error forwarding to {server}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in forward_query: {e}")
            return None
    
    def add_forwarding_rule(self, name: str, rule_type: str, target_servers: List[str],
                           conditions: Dict[str, Any] = None, priority: int = 100,
                           ttl: int = 300) -> bool:
        """Add a forwarding rule"""
        try:
            rule = ForwardingRule(
                name=name,
                rule_type=ForwardingPolicy(rule_type),
                target_servers=target_servers,
                conditions=conditions or {},
                priority=priority,
                ttl=ttl,
                enabled=True,
                created_at=time.time()
            )
            
            self.rules.append(rule)
            
            # Re-sort rules by priority
            self.rules.sort(key=lambda r: r.priority)
            
            # Clear cache to force re-evaluation
            self.clear_cache()
            
            # Save to configuration
            self._save_rules()
            
            self.logger.info(f"Added forwarding rule: {name} -> {target_servers}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding forwarding rule: {e}")
            return False
    
    def remove_forwarding_rule(self, name: str) -> bool:
        """Remove a forwarding rule"""
        try:
            self.rules = [rule for rule in self.rules if rule.name != name]
            
            # Clear cache
            self.clear_cache()
            
            # Save to configuration
            self._save_rules()
            
            self.logger.info(f"Removed forwarding rule: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing forwarding rule: {e}")
            return False
    
    def update_forwarding_rule(self, name: str, **kwargs) -> bool:
        """Update a forwarding rule"""
        try:
            for i, rule in enumerate(self.rules):
                if rule.name == name:
                    # Update rule properties
                    for key, value in kwargs.items():
                        if hasattr(rule, key):
                            setattr(rule, key, value)
                    
                    # Re-sort rules by priority
                    self.rules.sort(key=lambda r: r.priority)
                    
                    # Clear cache
                    self.clear_cache()
                    
                    # Save to configuration
                    self._save_rules()
                    
                    self.logger.info(f"Updated forwarding rule: {name}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating forwarding rule: {e}")
            return False
    
    def enable_rule(self, name: str) -> bool:
        """Enable a forwarding rule"""
        return self.update_forwarding_rule(name, enabled=True)
    
    def disable_rule(self, name: str) -> bool:
        """Disable a forwarding rule"""
        return self.update_forwarding_rule(name, enabled=False)
    
    def get_forwarding_statistics(self) -> Dict[str, Any]:
        """Get forwarding statistics"""
        stats = {
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules if r.enabled]),
            'cache_entries': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'rules': []
        }
        
        for rule in self.rules:
            stats['rules'].append({
                'name': rule.name,
                'type': rule.rule_type.value,
                'servers': rule.target_servers,
                'priority': rule.priority,
                'enabled': rule.enabled,
                'usage_count': rule.usage_count,
                'last_used': rule.last_used,
                'created_at': rule.created_at
            })
        
        return stats
    
    def _save_rules(self):
        """Save forwarding rules to configuration"""
        try:
            config = Config()
            
            forwarding_config = {
                'rules': []
            }
            
            for rule in self.rules:
                rule_dict = {
                    'name': rule.name,
                    'type': rule.rule_type.value,
                    'servers': rule.target_servers,
                    'conditions': rule.conditions,
                    'priority': rule.priority,
                    'ttl': rule.ttl,
                    'enabled': rule.enabled,
                    'created_at': rule.created_at,
                    'last_used': rule.last_used,
                    'usage_count': rule.usage_count
                }
                forwarding_config['rules'].append(rule_dict)
            
            config.set('forwarding', forwarding_config)
            
            # Save forwarders
            config.set('forwarding.forwarders', self.forwarders)
            
            self.logger.info("Saved forwarding configuration")
            
        except Exception as e:
            self.logger.error(f"Error saving forwarding configuration: {e}")
    
    def clear_cache(self):
        """Clear forwarding cache"""
        self.cache.clear()
        self.logger.info("Forwarding cache cleared")
    
    def refresh_cache(self):
        """Refresh forwarding cache"""
        self.clear_cache()
        self._load_forwarding_rules()
        self.logger.info("Forwarding cache refreshed")
