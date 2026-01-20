"""
DNS Record types and response handling
"""

from enum import Enum
from dataclasses import dataclass
from typing import Union
import ipaddress

class DNSRecordType(Enum):
    """DNS record types"""
    A = 1      # IPv4 address
    AAAA = 28  # IPv6 address
    CNAME = 5  # Canonical name
    MX = 15    # Mail exchange
    TXT = 16   # Text record
    NS = 2     # Name server
    SOA = 6    # Start of authority
    PTR = 12   # Pointer record

@dataclass
class DNSRecord:
    """DNS record data structure"""
    name: str
    record_type: DNSRecordType
    value: str
    ttl: int = 300
    
    def __post_init__(self):
        """Validate record data"""
        self.name = self.name.lower().rstrip('.')
        
        # Validate record value based on type
        if self.record_type == DNSRecordType.A:
            try:
                ipaddress.IPv4Address(self.value)
            except ipaddress.AddressValueError:
                raise ValueError(f"Invalid IPv4 address: {self.value}")
        
        elif self.record_type == DNSRecordType.AAAA:
            try:
                ipaddress.IPv6Address(self.value)
            except ipaddress.AddressValueError:
                raise ValueError(f"Invalid IPv6 address: {self.value}")
        
        elif self.record_type == DNSRecordType.CNAME:
            # CNAME should be a domain name
            if not self._is_valid_domain_name(self.value):
                raise ValueError(f"Invalid domain name for CNAME: {self.value}")
        
        elif self.record_type == DNSRecordType.MX:
            # MX format: "priority domain"
            if ' ' not in self.value:
                raise ValueError(f"Invalid MX record format: {self.value}")
            priority, domain = self.value.split(' ', 1)
            try:
                int(priority)
            except ValueError:
                raise ValueError(f"Invalid MX priority: {priority}")
            if not self._is_valid_domain_name(domain):
                raise ValueError(f"Invalid MX domain: {domain}")
    
    def _is_valid_domain_name(self, name: str) -> bool:
        """Validate domain name format"""
        if not name or len(name) > 253:
            return False
        
        # Remove trailing dot if present
        name = name.rstrip('.')
        
        # Check each label
        for label in name.split('.'):
            if not label or len(label) > 63:
                return False
            # Check if label starts/ends with hyphen
            if label.startswith('-') or label.endswith('-'):
                return False
            # Check valid characters
            for char in label:
                if not (char.isalnum() or char == '-'):
                    return False
        
        return True
    
    def __str__(self) -> str:
        """String representation of DNS record"""
        return f"{self.name} {self.ttl} IN {self.record_type.name} {self.value}"

class DNSResponse:
    """DNS response builder"""
    
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        self.questions = []
        self.answers = []
        self.authorities = []
        self.additional = []
        self.flags = 0x8000  # QR=1 (response)
    
    def add_question(self, name: str, qtype: int, qclass: int = 1):
        """Add a question section"""
        self.questions.append({
            'name': name,
            'type': qtype,
            'class': qclass
        })
    
    def add_answer(self, record: DNSRecord):
        """Add an answer record"""
        self.answers.append(record)
    
    def set_authoritative(self, authoritative: bool = True):
        """Set authoritative answer flag"""
        if authoritative:
            self.flags |= 0x0400  # AA bit
        else:
            self.flags &= ~0x0400
    
    def set_recursion_available(self, available: bool = True):
        """Set recursion available flag"""
        if available:
            self.flags |= 0x0080  # RA bit
        else:
            self.flags &= ~0x0080
    
    def set_response_code(self, rcode: int):
        """Set response code (0=NOERROR, 1=FORMERR, 2=SERVFAIL, 3=NXDOMAIN, etc.)"""
        self.flags = (self.flags & 0xFFF0) | (rcode & 0x000F)
