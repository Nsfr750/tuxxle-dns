#!/usr/bin/env python3
"""
IPv4 to IPv6 converter utility module
"""

import ipaddress
import re
import logging
from typing import Tuple, Optional, List, Union

class IPConverter:
    """Utility class for IPv4/IPv6 conversion and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def ipv4_to_ipv6_mapped(self, ipv4: str) -> str:
        """Convert IPv4 address to IPv6-mapped address (::ffff:x.x.x.x)"""
        try:
            ipv4_obj = ipaddress.IPv4Address(ipv4)
            # Create IPv6-mapped address
            ipv6_mapped = ipaddress.IPv6Address(f"::ffff:{ipv4_obj}")
            return str(ipv6_mapped)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv4 address: {ipv4}") from e
    
    def ipv6_to_ipv4_mapped(self, ipv6: str) -> str:
        """Convert IPv6-mapped address to IPv4 (::ffff:x.x.x.x -> x.x.x.x)"""
        try:
            ipv6_obj = ipaddress.IPv6Address(ipv6)
            # Check if it's an IPv6-mapped address
            if ipv6_obj.ipv4_mapped:
                return str(ipv6_obj.ipv4_mapped)
            else:
                raise ValueError(f"IPv6 address {ipv6} is not an IPv6-mapped address")
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv6 address: {ipv6}") from e
    
    def ipv4_to_6to4(self, ipv4: str) -> str:
        """Convert IPv4 to 6to4 tunnel address (2002:xxxx::/48)"""
        try:
            ipv4_obj = ipaddress.IPv4Address(ipv4)
            # Convert to 6to4 format: 2002:xxxx::/48 where xxxx is hex representation of IPv4
            ipv4_hex = f"{int(ipv4_obj):08x}"
            prefix = f"2002:{ipv4_hex[:4]}:{ipv4_hex[4:]}::"
            return prefix
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv4 address: {ipv4}") from e
    
    def ipv4_to_teredo(self, ipv4: str) -> str:
        """Convert IPv4 to Teredo address format (simplified)"""
        try:
            ipv4_obj = ipaddress.IPv4Address(ipv4)
            # Teredo format: 2001:0000::xxxx where xxxx is hex representation
            ipv4_hex = f"{int(ipv4_obj):08x}"
            return f"2001:0000::{ipv4_hex}"
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv4 address: {ipv4}") from e
    
    def is_valid_ipv4(self, ip: str) -> bool:
        """Check if string is a valid IPv4 address"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def is_valid_ipv6(self, ip: str) -> bool:
        """Check if string is a valid IPv6 address"""
        try:
            ipaddress.IPv6Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False
    
    def is_ipv6_mapped_ipv4(self, ipv6: str) -> bool:
        """Check if IPv6 address is an IPv6-mapped address"""
        try:
            ipv6_obj = ipaddress.IPv6Address(ipv6)
            return ipv6_obj.ipv4_mapped is not None
        except ipaddress.AddressValueError:
            return False
    
    def compress_ipv6(self, ipv6: str) -> str:
        """Compress IPv6 address (remove leading zeros)"""
        try:
            ipv6_obj = ipaddress.IPv6Address(ipv6)
            return str(ipv6_obj.compressed)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv6 address: {ipv6}") from e
    
    def expand_ipv6(self, ipv6: str) -> str:
        """Expand IPv6 address (full notation)"""
        try:
            ipv6_obj = ipaddress.IPv6Address(ipv6)
            return str(ipv6_obj.exploded)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv6 address: {ipv6}") from e
    
    def get_ipv4_from_ipv6(self, ipv6: str) -> Optional[str]:
        """Extract IPv4 address from IPv6 if embedded"""
        try:
            ipv6_obj = ipaddress.IPv6Address(ipv6)
            
            # Check for IPv6-mapped address
            if ipv6_obj.ipv4_mapped:
                return str(ipv6_obj.ipv4_mapped)
            
            # Check for 6to4 address
            if ipv6_obj.sixtofour:
                return str(ipv6_obj.sixtofour)
            
            # Check for Teredo address (simplified extraction)
            if str(ipv6_obj).startswith("2001:0000::"):
                # Extract last 32 bits as IPv4
                parts = str(ipv6_obj.exploded).split(':')
                if len(parts) >= 8:
                    ipv4_hex = parts[-1]
                    if len(ipv4_hex) == 8:
                        try:
                            ipv4_int = int(ipv4_hex, 16)
                            return str(ipaddress.IPv4Address(ipv4_int))
                        except:
                            pass
            
            return None
        except ipaddress.AddressValueError:
            return None
    
    def batch_convert_ipv4_to_ipv6(self, ipv4_list: List[str], method: str = "mapped") -> List[Tuple[str, str, Optional[str]]]:
        """
        Batch convert IPv4 addresses to IPv6
        Returns list of (original_ipv4, converted_ipv6, error) tuples
        """
        results = []
        
        for ipv4 in ipv4_list:
            try:
                if method == "mapped":
                    ipv6 = self.ipv4_to_ipv6_mapped(ipv4)
                elif method == "6to4":
                    ipv6 = self.ipv4_to_6to4(ipv4)
                elif method == "teredo":
                    ipv6 = self.ipv4_to_teredo(ipv4)
                else:
                    raise ValueError(f"Unknown conversion method: {method}")
                
                results.append((ipv4, ipv6, None))
            except Exception as e:
                results.append((ipv4, "", str(e)))
        
        return results
    
    def validate_ip_range(self, ip: str, cidr: str) -> bool:
        """Check if IP address is within CIDR range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(cidr, strict=False)
            return ip_obj in network
        except (ipaddress.AddressValueError, ValueError):
            return False
    
    def get_ip_info(self, ip: str) -> dict:
        """Get comprehensive information about an IP address"""
        info = {
            "original": ip,
            "type": "unknown",
            "is_valid": False,
            "ipv4_equivalent": None,
            "ipv6_equivalent": None,
            "compressed": None,
            "expanded": None,
            "is_private": False,
            "is_loopback": False,
            "is_multicast": False
        }
        
        try:
            # Try IPv4 first
            if self.is_valid_ipv4(ip):
                ipv4_obj = ipaddress.IPv4Address(ip)
                info.update({
                    "type": "IPv4",
                    "is_valid": True,
                    "ipv6_equivalent": self.ipv4_to_ipv6_mapped(ip),
                    "is_private": ipv4_obj.is_private,
                    "is_loopback": ipv4_obj.is_loopback,
                    "is_multicast": ipv4_obj.is_multicast
                })
            
            # Try IPv6
            elif self.is_valid_ipv6(ip):
                ipv6_obj = ipaddress.IPv6Address(ip)
                info.update({
                    "type": "IPv6",
                    "is_valid": True,
                    "ipv4_equivalent": self.get_ipv4_from_ipv6(ip),
                    "compressed": self.compress_ipv6(ip),
                    "expanded": self.expand_ipv6(ip),
                    "is_private": ipv6_obj.is_private,
                    "is_loopback": ipv6_obj.is_loopback,
                    "is_multicast": ipv6_obj.is_multicast
                })
            
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def generate_ipv6_from_ipv4_subnet(self, ipv4_subnet: str, ipv6_prefix: str = "2001:db8::") -> List[str]:
        """Generate IPv6 addresses from IPv4 subnet"""
        try:
            network = ipaddress.ip_network(ipv4_subnet, strict=False)
            ipv6_base = ipaddress.IPv6Address(ipv6_prefix)
            
            ipv6_addresses = []
            for i, ipv4 in enumerate(network.hosts()):
                if i >= 256:  # Limit to first 256 hosts
                    break
                
                # Create IPv6 address by combining prefix with host portion
                ipv6_int = int(ipv6_base) + i
                ipv6_addr = ipaddress.IPv6Address(ipv6_int)
                ipv6_addresses.append(str(ipv6_addr))
            
            return ipv6_addresses
        except Exception as e:
            raise ValueError(f"Error generating IPv6 addresses: {e}") from e
    
    def convert_dns_record(self, record_type: str, value: str) -> Tuple[str, str]:
        """Convert DNS record value between IPv4 and IPv6 formats"""
        try:
            if record_type.upper() == "A":
                # IPv4 to IPv6-mapped
                if self.is_valid_ipv4(value):
                    return "AAAA", self.ipv4_to_ipv6_mapped(value)
                else:
                    raise ValueError(f"Invalid IPv4 address for A record: {value}")
            
            elif record_type.upper() == "AAAA":
                # IPv6 to IPv4 if mapped
                if self.is_valid_ipv6(value):
                    ipv4 = self.get_ipv4_from_ipv6(value)
                    if ipv4:
                        return "A", ipv4
                    else:
                        raise ValueError(f"IPv6 address {value} does not contain embedded IPv4")
                else:
                    raise ValueError(f"Invalid IPv6 address for AAAA record: {value}")
            
            else:
                raise ValueError(f"Unsupported record type for conversion: {record_type}")
        
        except Exception as e:
            raise ValueError(f"Error converting DNS record: {e}") from e
