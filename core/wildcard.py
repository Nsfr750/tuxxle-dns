#!/usr/bin/env python3
"""
Wildcard DNS records support for DNS Server Manager
"""

import re
import fnmatch
import logging
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from .dns_records import DNSRecord, DNSRecordType

class WildcardManager:
    """Wildcard DNS records management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.wildcard_records: Dict[str, List[DNSRecord]] = {}
        self.wildcard_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
        self._load_wildcard_records()
    
    def _load_wildcard_records(self):
        """Load wildcard records from database"""
        try:
            # Load all records that contain wildcards
            all_records = self._get_all_records_from_db()
            
            for record in all_records:
                if self._is_wildcard_name(record.name):
                    if record.name not in self.wildcard_records:
                        self.wildcard_records[record.name] = []
                    self.wildcard_records[record.name].append(record)
                    self.logger.info(f"Loaded wildcard record: {record.name} {record.record_type} {record.value}")
            
            self.logger.info(f"Loaded {len(self.wildcard_records)} wildcard record sets")
            
        except Exception as e:
            self.logger.error(f"Error loading wildcard records: {e}")
    
    def _get_all_records_from_db(self) -> List[DNSRecord]:
        """Get all records from database (placeholder)"""
        # This would normally query the database
        # For now, return empty list - records are loaded by the main DNS server
        return []
    
    def _is_wildcard_name(self, name: str) -> bool:
        """Check if a name contains wildcards"""
        return '*' in name or '?' in name
    
    def match_wildcard(self, query_name: str, wildcard_name: str) -> bool:
        """Check if query name matches wildcard pattern"""
        try:
            # Convert DNS wildcard patterns to glob patterns
            # DNS wildcards are similar to shell globs but with some differences
            pattern = wildcard_name.replace('.', r'\.')
            
            # Handle DNS-specific wildcard rules
            # 1. Leading wildcard matches any number of labels
            # 2. Single label wildcard matches within that label only
            # 3. Trailing wildcard matches any number of labels
            
            if pattern.startswith('*'):
                # Leading wildcard - can match any number of labels
                if pattern == '*':
                    return True  # Matches everything
                elif pattern.startswith('*.'):
                    # *.example.com - matches any subdomain of example.com
                    remaining = pattern[2:]  # Remove '*.'
                    if query_name == remaining:
                        return True
                    elif query_name.endswith('.' + remaining):
                        return True
                    else:
                        # Check if query_name has more labels than pattern
                        query_labels = query_name.split('.')
                        pattern_labels = remaining.split('.')
                        return len(query_labels) >= len(pattern_labels) and query_name.endswith('.' + remaining)
            
            elif pattern.endswith('*'):
                # Trailing wildcard
                base_pattern = pattern[:-1]  # Remove trailing '*'
                if query_name.startswith(base_pattern):
                    return True
                else:
                    # Check if query_name has more labels
                    query_labels = query_name.split('.')
                    pattern_labels = base_pattern.split('.')
                    return len(query_labels) >= len(pattern_labels) and query_name.startswith(base_pattern)
            
            else:
                # Wildcard in the middle - use fnmatch
                return fnmatch.fnmatch(query_name, pattern)
            
        except Exception as e:
            self.logger.error(f"Error matching wildcard {wildcard_name} against {query_name}: {e}")
            return False
    
    def find_matching_records(self, query_name: str, record_type: Optional[str] = None) -> List[DNSRecord]:
        """Find all records that match the query name using wildcards"""
        matching_records = []
        
        try:
            # Check exact matches first (cache)
            cache_key = f"{query_name}:{record_type or '*'}"
            if cache_key in self.wildcard_cache:
                cached = self.wildcard_cache[cache_key]
                if cached['expires_at'] > time.time():
                    matching_records = cached['records']
                else:
                    del self.wildcard_cache[cache_key]
            
            # If not in cache, search wildcard records
            if not matching_records:
                for wildcard_name, records in self.wildcard_records.items():
                    if self.match_wildcard(query_name, wildcard_name):
                        for record in records:
                            if record_type is None or record.record_type == record_type or record_type == "ANY":
                                matching_records.append(record)
                
                # Cache the result
                self.wildcard_cache[cache_key] = {
                    'records': matching_records,
                    'expires_at': time.time() + self.cache_ttl
                }
            
            self.logger.debug(f"Wildcard match for {query_name}: found {len(matching_records)} records")
            
        except Exception as e:
            self.logger.error(f"Error finding matching records: {e}")
        
        return matching_records
    
    def add_wildcard_record(self, name: str, record_type: str, value: str, ttl: int = 300) -> bool:
        """Add a wildcard record"""
        try:
            if not self._is_wildcard_name(name):
                self.logger.warning(f"Name {name} is not a wildcard pattern")
                return False
            
            record = DNSRecord(name, record_type, value, ttl)
            
            if name not in self.wildcard_records:
                self.wildcard_records[name] = []
            
            self.wildcard_records[name].append(record)
            
            # Clear cache for this pattern
            patterns_to_clear = []
            for cache_key in self.wildcard_cache:
                if self.match_wildcard(cache_key.split(':')[0], name):
                    patterns_to_clear.append(cache_key)
            
            for pattern in patterns_to_clear:
                del self.wildcard_cache[pattern]
            
            # Save to database
            self._save_wildcard_record(record)
            
            self.logger.info(f"Added wildcard record: {name} {record_type} {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding wildcard record: {e}")
            return False
    
    def remove_wildcard_record(self, name: str, record_type: str, value: str) -> bool:
        """Remove a wildcard record"""
        try:
            if name not in self.wildcard_records:
                return False
            
            records_to_remove = []
            for i, record in enumerate(self.wildcard_records[name]):
                if record.record_type == record_type and record.value == value:
                    records_to_remove.append(i)
            
            for i in reversed(records_to_remove):
                del self.wildcard_records[name][i]
            
            if not self.wildcard_records[name]:
                del self.wildcard_records[name]
            
            # Clear cache
            patterns_to_clear = []
            for cache_key in self.wildcard_cache:
                if self.match_wildcard(cache_key.split(':')[0], name):
                    patterns_to_clear.append(cache_key)
            
            for pattern in patterns_to_clear:
                del self.wildcard_cache[pattern]
            
            # Remove from database
            self._delete_wildcard_record(name, record_type, value)
            
            self.logger.info(f"Removed wildcard record: {name} {record_type} {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing wildcard record: {e}")
            return False
    
    def _save_wildcard_record(self, record: DNSRecord):
        """Save wildcard record to database"""
        # This would save to the actual database
        pass
    
    def _delete_wildcard_record(self, name: str, record_type: str, value: str):
        """Delete wildcard record from database"""
        # This would delete from the actual database
        pass
    
    def get_wildcard_info(self, name: str) -> Dict[str, Any]:
        """Get information about wildcard patterns for a name"""
        info = {
            'name': name,
            'is_wildcard': self._is_wildcard_name(name),
            'matching_records': [],
            'pattern_type': 'none'
        }
        
        if self._is_wildcard_name(name):
            if name.startswith('*'):
                if name == '*':
                    info['pattern_type'] = 'universal'
                elif name.startswith('*.'):
                    info['pattern_type'] = 'subdomain'
                else:
                    info['pattern_type'] = 'leading'
            elif name.endswith('*'):
                info['pattern_type'] = 'trailing'
            else:
                info['pattern_type'] = 'middle'
            
            if name in self.wildcard_records:
                info['matching_records'] = [
                    {
                        'type': r.record_type,
                        'value': r.value,
                        'ttl': r.ttl
                    } for r in self.wildcard_records[name]
                ]
        
        return info
    
    def expand_wildcard(self, wildcard_name: str, known_names: List[str]) -> List[str]:
        """Expand wildcard pattern to match known names"""
        expanded = []
        
        try:
            if not self._is_wildcard_name(wildcard_name):
                return [wildcard_name]
            
            if wildcard_name == '*':
                # Universal wildcard - return all known names
                return known_names.copy()
            
            for name in known_names:
                if self.match_wildcard(name, wildcard_name):
                    expanded.append(name)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_expanded = []
            for name in expanded:
                if name not in seen:
                    seen.add(name)
                    unique_expanded.append(name)
            
            return unique_expanded
            
        except Exception as e:
            self.logger.error(f"Error expanding wildcard {wildcard_name}: {e}")
            return []
    
    def validate_wildcard_pattern(self, pattern: str) -> Tuple[bool, str]:
        """Validate a wildcard pattern"""
        try:
            # Basic validation
            if not pattern:
                return False, "Empty pattern"
            
            # Check for invalid characters
            invalid_chars = ['<', '>', '|', '"', "'", '`', '^', '$', '{', '}', '[', ']', '\\']
            for char in invalid_chars:
                if char in pattern:
                    return False, f"Invalid character: {char}"
            
            # Check wildcard syntax
            if pattern.count('*') > len(pattern.split('.')):
                return False, "Too many wildcards for number of labels"
            
            # Check for consecutive wildcards
            if '**' in pattern:
                return False, "Consecutive wildcards not allowed"
            
            # Check label length (DNS labels max 63 characters)
            labels = pattern.split('.')
            for label in labels:
                if len(label) > 63:
                    return False, f"Label too long: {label}"
            
            # Check total name length (DNS names max 255 characters)
            if len(pattern) > 255:
                return False, "Name too long"
            
            return True, "Valid wildcard pattern"
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def get_wildcard_statistics(self) -> Dict[str, Any]:
        """Get statistics about wildcard records"""
        stats = {
            'total_wildcard_sets': len(self.wildcard_records),
            'total_wildcard_records': sum(len(records) for records in self.wildcard_records.values()),
            'cache_entries': len(self.wildcard_cache),
            'cache_ttl': self.cache_ttl,
            'patterns': {}
        }
        
        for pattern, records in self.wildcard_records.items():
            stats['patterns'][pattern] = {
                'record_count': len(records),
                'record_types': list(set(r.record_type for r in records)),
                'pattern_type': self.get_wildcard_info(pattern)['pattern_type']
            }
        
        return stats
    
    def clear_cache(self):
        """Clear wildcard cache"""
        self.wildcard_cache.clear()
        self.logger.info("Wildcard cache cleared")
    
    def refresh_cache(self):
        """Refresh wildcard cache"""
        self.clear_cache()
        self._load_wildcard_records()
        self.logger.info("Wildcard cache refreshed")
