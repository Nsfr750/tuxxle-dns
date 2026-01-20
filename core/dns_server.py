"""
DNS Server implementation
"""

import socket
import struct
import threading
import logging
import time
from typing import Dict, List, Optional, Tuple
from .dns_records import DNSRecord, DNSRecordType, DNSResponse
from .config import Config
from .database import DNSSQLiteDatabase

class DNSServer:
    """DNS Server implementation"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        
        # Database for persistent storage
        self.database = DNSSQLiteDatabase()
        
        # DNS records storage (in-memory cache)
        self.records: Dict[str, List[DNSRecord]] = {}
        
        # Statistics
        self.stats = {
            'queries_received': 0,
            'responses_sent': 0,
            'errors': 0,
            'start_time': None
        }
        
        self._load_records_from_database()
    
    def _load_records_from_database(self) -> None:
        """Load DNS records from database"""
        try:
            records = self.database.list_records()
            for record in records:
                self._add_record_to_cache(record)
            self.logger.info(f"Loaded {len(records)} records from database")
            
            # Add default records if database is empty
            if len(records) == 0:
                self._load_default_records()
                
        except Exception as e:
            self.logger.error(f"Failed to load records from database: {e}")
            self._load_default_records()
    
    def _load_default_records(self) -> None:
        """Load default DNS records"""
        # Add some default records for testing
        default_records = [
            DNSRecord("localhost", DNSRecordType.A, "127.0.0.1", 300),
            DNSRecord("example.com", DNSRecordType.A, "93.184.216.34", 300),
            DNSRecord("google.com", DNSRecordType.A, "142.250.180.142", 300)
        ]
        
        for record in default_records:
            self.add_record(record)
    
    def add_record(self, record: DNSRecord) -> bool:
        """Add a DNS record"""
        try:
            # Save to database first
            if not self.database.add_record(record):
                self.logger.error(f"Failed to save record to database: {record}")
                return False
            
            # Add to in-memory cache
            self._add_record_to_cache(record)
            
            self.logger.info(f"Added DNS record: {record}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add DNS record: {e}")
            return False
    
    def _add_record_to_cache(self, record: DNSRecord) -> None:
        """Add DNS record to in-memory cache"""
        if record.name not in self.records:
            self.records[record.name] = []
        
        # Remove existing record of same type
        self.records[record.name] = [r for r in self.records[record.name] if r.record_type != record.record_type]
        self.records[record.name].append(record)
    
    def remove_record(self, name: str, record_type: DNSRecordType) -> bool:
        """Remove a DNS record"""
        try:
            # Remove from database first
            if not self.database.remove_record(name, record_type):
                self.logger.warning(f"Record not found in database: {name} {record_type.name}")
                return False
            
            # Remove from in-memory cache
            return self._remove_record_from_cache(name, record_type)
                
        except Exception as e:
            self.logger.error(f"Failed to remove DNS record: {e}")
            return False
    
    def _remove_record_from_cache(self, name: str, record_type: DNSRecordType) -> bool:
        """Remove DNS record from in-memory cache"""
        if name in self.records:
            original_count = len(self.records[name])
            self.records[name] = [r for r in self.records[name] if r.record_type != record_type]
            
            if len(self.records[name]) == 0:
                del self.records[name]
            
            removed = original_count > len(self.records[name])
            if removed:
                self.logger.info(f"Removed DNS record from cache: {name} {record_type.name}")
            return removed
        return False
    
    def get_record(self, name: str, record_type: DNSRecordType) -> Optional[DNSRecord]:
        """Get a specific DNS record"""
        if name in self.records:
            for record in self.records[name]:
                if record.record_type == record_type:
                    return record
        return None
    
    def list_records(self) -> List[DNSRecord]:
        """List all DNS records"""
        all_records = []
        for records in self.records.values():
            all_records.extend(records)
        return all_records
    
    def start(self) -> bool:
        """Start the DNS server"""
        if self.running:
            self.logger.warning("DNS server is already running")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.bind_address, self.config.dns_port))
            
            self.running = True
            self.stats['start_time'] = time.time()
            
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            self.logger.info(f"DNS server started on {self.config.bind_address}:{self.config.dns_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start DNS server: {e}")
            self.running = False
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            return False
    
    def stop(self) -> bool:
        """Stop the DNS server"""
        if not self.running:
            return False
        
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.logger.info("DNS server stopped")
        return True
    
    def _server_loop(self) -> None:
        """Main server loop"""
        while self.running:
            try:
                data, client_address = self.server_socket.recvfrom(512)
                self.stats['queries_received'] += 1
                
                # Process DNS query in separate thread
                threading.Thread(
                    target=self._handle_query,
                    args=(data, client_address),
                    daemon=True
                ).start()
                
            except socket.error as e:
                if self.running:
                    self.logger.error(f"Socket error: {e}")
                    self.stats['errors'] += 1
                break
            except Exception as e:
                self.logger.error(f"Server loop error: {e}")
                self.stats['errors'] += 1
    
    def _handle_query(self, data: bytes, client_address: Tuple[str, int]) -> None:
        """Handle a DNS query"""
        try:
            # Parse DNS query
            query = self._parse_dns_query(data)
            if not query:
                self.stats['errors'] += 1
                return
            
            # Generate response
            response = self._generate_response(query)
            
            # Send response
            self.server_socket.sendto(response, client_address)
            self.stats['responses_sent'] += 1
            
            self.logger.debug(f"Responded to query from {client_address}")
            
        except Exception as e:
            self.logger.error(f"Error handling query from {client_address}: {e}")
            self.stats['errors'] += 1
    
    def _parse_dns_query(self, data: bytes) -> Optional[Dict]:
        """Parse DNS query packet"""
        try:
            if len(data) < 12:
                return None
            
            # Parse header
            header = struct.unpack('!HHHHHH', data[:12])
            transaction_id = header[0]
            flags = header[1]
            questions = header[2]
            
            # Check if it's a query (QR bit = 0)
            if flags & 0x8000:
                return None  # It's a response, not a query
            
            # Parse question section
            offset = 12
            questions_list = []
            
            for _ in range(questions):
                # Parse domain name
                name_parts = []
                while offset < len(data):
                    length = data[offset]
                    if length == 0:
                        offset += 1
                        break
                    offset += 1
                    if offset + length > len(data):
                        return None
                    name_parts.append(data[offset:offset+length].decode('ascii', errors='ignore'))
                    offset += length
                
                domain_name = '.'.join(name_parts)
                
                # Parse QTYPE and QCLASS
                if offset + 4 > len(data):
                    return None
                
                qtype, qclass = struct.unpack('!HH', data[offset:offset+4])
                offset += 4
                
                questions_list.append({
                    'name': domain_name.lower(),
                    'type': qtype,
                    'class': qclass
                })
            
            return {
                'transaction_id': transaction_id,
                'flags': flags,
                'questions': questions_list
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing DNS query: {e}")
            return None
    
    def _generate_response(self, query: Dict) -> bytes:
        """Generate DNS response"""
        transaction_id = query['transaction_id']
        flags = query['flags']
        questions = query['questions']
        
        # Build response header
        response_flags = 0x8000 | (flags & 0x0100)  # QR=1, RD preserved
        answer_count = 0
        
        # Build response sections
        question_section = b''
        answer_section = b''
        
        for question in questions:
            # Rebuild question section
            qname = self._encode_domain_name(question['name'])
            question_section += qname + struct.pack('!HH', question['type'], question['class'])
            
            # Look for answer
            record = self.get_record(question['name'], DNSRecordType(question['type']))
            if record:
                answer_count += 1
                answer_section += qname  # Name
                answer_section += struct.pack('!HHIH', 
                    question['type'],  # Type
                    question['class'],  # Class
                    record.ttl,        # TTL
                    len(record.value)  # Data length
                )
                answer_section += record.value.encode('ascii')  # Data
        
        # Build complete response
        header = struct.pack('!HHHHHH',
            transaction_id,
            response_flags,
            len(questions),     # QDCount
            answer_count,       # ANCount
            0,                  # NSCount
            0                   # ARCount
        )
        
        return header + question_section + answer_section
    
    def _encode_domain_name(self, domain: str) -> bytes:
        """Encode domain name for DNS packet"""
        if domain == '.':
            return b'\x00'
        
        parts = domain.split('.')
        encoded = b''
        
        for part in parts:
            if part:
                encoded += bytes([len(part)]) + part.encode('ascii')
        
        encoded += b'\x00'  # End of name
        return encoded
    
    def get_stats(self) -> Dict:
        """Get server statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['uptime'] = time.time() - stats['start_time']
        else:
            stats['uptime'] = 0
        return stats
