#!/usr/bin/env python3
"""
DNSSEC (DNS Security Extensions) implementation for DNS Server Manager
"""

import hashlib
import time
import base64
import struct
import logging
from typing import Dict, List, Optional, Tuple, Union
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, dsa, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import dns.rdatatype
import dns.rrset
import dns.message
import dns.name

class DNSSECKey:
    """DNSSEC key management"""
    
    def __init__(self, key_name: str, key_type: str = "RSA", key_size: int = 2048):
        self.key_name = key_name
        self.key_type = key_type
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self.key_tag = None
        self.algorithm = None
        self.created_at = time.time()
        self.logger = logging.getLogger(__name__)
        
        self._generate_key()
    
    def _generate_key(self):
        """Generate cryptographic key"""
        try:
            if self.key_type.upper() == "RSA":
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=self.key_size,
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()
                self.algorithm = 8  # RSASHA256
                
            elif self.key_type.upper() == "ECDSA":
                self.private_key = ec.generate_private_key(
                    ec.SECP256R1(),
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()
                self.algorithm = 13  # ECDSAP256SHA256
                
            elif self.key_type.upper() == "ED25519":
                self.private_key = ec.generate_private_key(
                    ec.Ed25519(),
                    backend=default_backend()
                )
                self.public_key = self.private_key.public_key()
                self.algorithm = 15  # ED25519
                
            else:
                raise ValueError(f"Unsupported key type: {self.key_type}")
            
            self._calculate_key_tag()
            
        except Exception as e:
            self.logger.error(f"Error generating DNSSEC key: {e}")
            raise
    
    def _calculate_key_tag(self):
        """Calculate DNSSEC key tag"""
        try:
            # Simplified key tag calculation
            key_data = self.public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # DNSSEC key tag algorithm (RFC 4034)
            ac = 0
            for i in range(0, len(key_data), 2):
                if i + 1 < len(key_data):
                    ac += (key_data[i] << 8) + key_data[i + 1]
                else:
                    ac += key_data[i] << 8
            
            self.key_tag = (ac + (ac >> 16)) & 0xFFFF
            
        except Exception as e:
            self.logger.error(f"Error calculating key tag: {e}")
            self.key_tag = hash(self.key_name) & 0xFFFF
    
    def sign_data(self, data: bytes) -> bytes:
        """Sign data with private key"""
        try:
            if self.key_type.upper() == "RSA":
                signature = self.private_key.sign(
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            elif self.key_type.upper() == "ECDSA":
                signature = self.private_key.sign(
                    data,
                    ec.ECDSA(hashes.SHA256())
                )
            elif self.key_type.upper() == "ED25519":
                signature = self.private_key.sign(data)
            else:
                raise ValueError(f"Unsupported key type for signing: {self.key_type}")
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Error signing data: {e}")
            raise
    
    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify signature with public key"""
        try:
            if self.key_type.upper() == "RSA":
                self.public_key.verify(
                    signature,
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            elif self.key_type.upper() == "ECDSA":
                self.public_key.verify(
                    signature,
                    data,
                    ec.ECDSA(hashes.SHA256())
                )
            elif self.key_type.upper() == "ED25519":
                self.public_key.verify(signature, data)
            else:
                raise ValueError(f"Unsupported key type for verification: {self.key_type}")
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def get_dnskey_record(self) -> Dict:
        """Get DNSKEY record data"""
        try:
            public_bytes = self.public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Remove ASN.1 header for DNSKEY format
            if self.key_type.upper() == "RSA":
                # RSA: extract modulus and exponent
                from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
                if isinstance(self.public_key, RSAPublicKey):
                    public_numbers = self.public_key.public_numbers()
                    modulus = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')
                    exponent = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')
                    key_data = b'\x00\x01' + exponent + modulus
                else:
                    key_data = public_bytes
            else:
                key_data = public_bytes
            
            return {
                "name": self.key_name,
                "type": "DNSKEY",
                "flags": 256,  # Zone key
                "protocol": 3,
                "algorithm": self.algorithm,
                "key": base64.b64encode(key_data).decode('ascii'),
                "key_tag": self.key_tag
            }
            
        except Exception as e:
            self.logger.error(f"Error creating DNSKEY record: {e}")
            raise
    
    def export_private_key(self, password: Optional[str] = None) -> str:
        """Export private key in PEM format"""
        try:
            encryption = serialization.NoEncryption()
            if password:
                encryption = serialization.BestAvailableEncryption(password.encode())
            
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            )
            
            return pem.decode('ascii')
            
        except Exception as e:
            self.logger.error(f"Error exporting private key: {e}")
            raise
    
    def import_private_key(self, pem_data: str, password: Optional[str] = None):
        """Import private key from PEM format"""
        try:
            self.private_key = serialization.load_pem_private_key(
                pem_data.encode('ascii'),
                password=password.encode() if password else None,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            self._calculate_key_tag()
            
        except Exception as e:
            self.logger.error(f"Error importing private key: {e}")
            raise

class DNSSECManager:
    """DNSSEC management and signing operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keys: Dict[str, DNSSECKey] = {}
        self.zone_signatures: Dict[str, Dict] = {}
        self.nsec_records: Dict[str, List[str]] = {}
        self.enabled = False
    
    def enable_dnssec(self):
        """Enable DNSSEC for the server"""
        self.enabled = True
        self.logger.info("DNSSEC enabled")
    
    def disable_dnssec(self):
        """Disable DNSSEC for the server"""
        self.enabled = False
        self.logger.info("DNSSEC disabled")
    
    def create_zone_key(self, zone_name: str, key_type: str = "RSA", key_size: int = 2048) -> str:
        """Create a new DNSSEC zone key"""
        try:
            key_id = f"{zone_name}_{int(time.time())}"
            key = DNSSECKey(key_id, key_type, key_size)
            self.keys[key_id] = key
            
            self.logger.info(f"Created DNSSEC key for zone {zone_name}: {key_id}")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Error creating zone key: {e}")
            raise
    
    def sign_zone(self, zone_name: str, records: List[Dict]) -> List[Dict]:
        """Sign a zone with DNSSEC"""
        if not self.enabled:
            return records
        
        try:
            signed_records = []
            
            # Get zone keys
            zone_keys = [key for key in self.keys.values() if zone_name in key.key_name]
            if not zone_keys:
                raise ValueError(f"No keys found for zone {zone_name}")
            
            # Create RRSIG records for each record set
            record_sets = self._group_records_by_name_type(records)
            
            for (name, record_type), record_set in record_sets.items():
                signed_records.extend(record_set)
                
                # Create RRSIG
                for key in zone_keys:
                    rrsig = self._create_rrsig(name, record_type, record_set, key)
                    if rrsig:
                        signed_records.append(rrsig)
            
            # Create NSEC records
            nsec_records = self._create_nsec_records(records)
            signed_records.extend(nsec_records)
            
            # Add DNSKEY records
            for key in zone_keys:
                dnskey = key.get_dnskey_record()
                dnskey["name"] = zone_name
                signed_records.append(dnskey)
            
            # Cache signatures
            self.zone_signatures[zone_name] = {
                "signed_at": time.time(),
                "expires_at": time.time() + (30 * 24 * 3600),  # 30 days
                "key_count": len(zone_keys)
            }
            
            self.logger.info(f"Successfully signed zone {zone_name} with {len(zone_keys)} keys")
            return signed_records
            
        except Exception as e:
            self.logger.error(f"Error signing zone {zone_name}: {e}")
            raise
    
    def verify_signature(self, name: str, record_type: str, records: List[Dict], rrsig: Dict) -> bool:
        """Verify DNSSEC signature for records"""
        try:
            if not self.enabled:
                return True  # Pass through if DNSSEC is disabled
            
            # Find the key that signed this
            key_tag = rrsig.get("key_tag")
            signing_key = None
            
            for key in self.keys.values():
                if key.key_tag == key_tag:
                    signing_key = key
                    break
            
            if not signing_key:
                self.logger.warning(f"No key found for key tag {key_tag}")
                return False
            
            # Create signature data
            signature_data = self._create_signature_data(name, record_type, records, rrsig)
            
            # Decode signature
            signature = base64.b64decode(rrsig["signature"])
            
            # Verify signature
            return signing_key.verify_signature(signature_data, signature)
            
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False
    
    def _group_records_by_name_type(self, records: List[Dict]) -> Dict[Tuple[str, str], List[Dict]]:
        """Group records by name and type for signing"""
        grouped = {}
        
        for record in records:
            name = record.get("name", "")
            record_type = record.get("type", "")
            
            if (name, record_type) not in grouped:
                grouped[(name, record_type)] = []
            
            grouped[(name, record_type)].append(record)
        
        return grouped
    
    def _create_rrsig(self, name: str, record_type: str, records: List[Dict], key: DNSSECKey) -> Optional[Dict]:
        """Create RRSIG record"""
        try:
            # Create signature data
            signature_data = self._create_signature_data(name, record_type, records, {})
            
            # Sign the data
            signature = key.sign_data(signature_data)
            
            # Create RRSIG record
            rrsig = {
                "name": name,
                "type": "RRSIG",
                "type_covered": record_type,
                "algorithm": key.algorithm,
                "labels": len(name.split('.')) if name else 1,
                "original_ttl": records[0].get("ttl", 300),
                "signature_expiration": int(time.time() + (30 * 24 * 3600)),
                "signature_inception": int(time.time()),
                "key_tag": key.key_tag,
                "signer_name": key.key_name.split('_')[0],  # Extract zone name
                "signature": base64.b64encode(signature).decode('ascii')
            }
            
            return rrsig
            
        except Exception as e:
            self.logger.error(f"Error creating RRSIG: {e}")
            return None
    
    def _create_signature_data(self, name: str, record_type: str, records: List[Dict], rrsig: Dict) -> bytes:
        """Create data to be signed"""
        try:
            data = bytearray()
            
            # Add RRSIG data (if verifying) or default values (if signing)
            if rrsig:
                data.extend(struct.pack("!H", rrsig.get("type_covered", 0)))
                data.extend(struct.pack("!B", rrsig.get("algorithm", 0)))
                data.extend(struct.pack("!B", rrsig.get("labels", 0)))
                data.extend(struct.pack("!I", rrsig.get("original_ttl", 0)))
                data.extend(struct.pack("!I", rrsig.get("signature_expiration", 0)))
                data.extend(struct.pack("!I", rrsig.get("signature_inception", 0)))
                data.extend(struct.pack("!H", rrsig.get("key_tag", 0)))
                data.extend(rrsig.get("signer_name", "").encode('ascii') + b'\x00')
            else:
                # Default values for signing
                data.extend(struct.pack("!H", self._get_record_type_code(record_type)))
                data.extend(struct.pack("!B", 8))  # RSASHA256
                data.extend(struct.pack("!B", len(name.split('.')) if name else 1))
                data.extend(struct.pack("!I", records[0].get("ttl", 300)))
                data.extend(struct.pack("!I", int(time.time() + (30 * 24 * 3600))))
                data.extend(struct.pack("!I", int(time.time())))
                data.extend(struct.pack("!H", list(self.keys.values())[0].key_tag if self.keys else 0))
                data.extend(name.encode('ascii') + b'\x00')
            
            # Add record data
            for record in records:
                record_data = self._encode_record(record)
                data.extend(record_data)
            
            return bytes(data)
            
        except Exception as e:
            self.logger.error(f"Error creating signature data: {e}")
            raise
    
    def _create_nsec_records(self, records: List[Dict]) -> List[Dict]:
        """Create NSEC records for authenticated denial of existence"""
        try:
            nsec_records = []
            
            # Get all unique names
            names = set()
            for record in records:
                name = record.get("name", "")
                if name:
                    names.add(name)
            
            # Sort names
            sorted_names = sorted(names)
            
            # Create NSEC records
            for i, name in enumerate(sorted_names):
                next_name = sorted_names[(i + 1) % len(sorted_names)]
                
                # Get types for this name
                types = set()
                for record in records:
                    if record.get("name") == name:
                        types.add(record.get("type", ""))
                
                # Always include NSEC and RRSIG
                types.add("NSEC")
                types.add("RRSIG")
                
                # Create type bitmap
                type_bitmap = self._create_type_bitmap(list(types))
                
                nsec_record = {
                    "name": name,
                    "type": "NSEC",
                    "next_domain_name": next_name,
                    "type_bitmap": type_bitmap,
                    "ttl": 300
                }
                
                nsec_records.append(nsec_record)
            
            return nsec_records
            
        except Exception as e:
            self.logger.error(f"Error creating NSEC records: {e}")
            return []
    
    def _create_type_bitmap(self, types: List[str]) -> str:
        """Create type bitmap for NSEC records"""
        try:
            # Convert type names to numbers
            type_numbers = []
            for type_name in types:
                type_code = self._get_record_type_code(type_name)
                if type_code > 0:
                    type_numbers.append(type_code)
            
            # Sort and create bitmap
            type_numbers.sort()
            
            bitmap = bytearray(32)  # 256 bits = 32 bytes
            for type_num in type_numbers:
                window = type_num // 256
                if window >= len(bitmap):
                    bitmap.extend(bytearray(window + 1 - len(bitmap)))
                
                byte_pos = (type_num % 256) // 8
                bit_pos = 7 - (type_num % 8)
                bitmap[window * 32 + byte_pos] |= (1 << bit_pos)
            
            return base64.b64encode(bytes(bitmap)).decode('ascii')
            
        except Exception as e:
            self.logger.error(f"Error creating type bitmap: {e}")
            return ""
    
    def _get_record_type_code(self, record_type: str) -> int:
        """Get DNS record type code"""
        type_codes = {
            "A": 1, "NS": 2, "CNAME": 5, "SOA": 6, "PTR": 12,
            "MX": 15, "TXT": 16, "AAAA": 28, "SRV": 33,
            "DNSKEY": 48, "RRSIG": 46, "NSEC": 47, "DS": 43
        }
        return type_codes.get(record_type.upper(), 0)
    
    def _encode_record(self, record: Dict) -> bytes:
        """Encode a DNS record for signing"""
        try:
            data = bytearray()
            
            # Add record name
            name = record.get("name", "")
            data.extend(name.encode('ascii') + b'\x00')
            
            # Add record type
            record_type = record.get("type", "")
            data.extend(struct.pack("!H", self._get_record_type_code(record_type)))
            
            # Add record class (IN)
            data.extend(struct.pack("!H", 1))
            
            # Add TTL
            data.extend(struct.pack("!I", record.get("ttl", 300)))
            
            # Add record data
            record_data = self._encode_record_data(record)
            data.extend(struct.pack("!H", len(record_data)))
            data.extend(record_data)
            
            return bytes(data)
            
        except Exception as e:
            self.logger.error(f"Error encoding record: {e}")
            return b""
    
    def _encode_record_data(self, record: Dict) -> bytes:
        """Encode record-specific data"""
        try:
            record_type = record.get("type", "").upper()
            value = record.get("value", "")
            
            if record_type == "A":
                import socket
                return socket.inet_aton(value)
            
            elif record_type == "AAAA":
                import socket
                return socket.inet_pton(socket.AF_INET6, value)
            
            elif record_type == "TXT":
                return len(value).to_bytes(1, 'big') + value.encode('ascii')
            
            elif record_type == "CNAME" or record_type == "NS" or record_type == "PTR":
                return value.encode('ascii') + b'\x00'
            
            else:
                # Default: encode as string
                return value.encode('ascii')
                
        except Exception as e:
            self.logger.error(f"Error encoding record data: {e}")
            return b""
    
    def get_zone_status(self, zone_name: str) -> Dict:
        """Get DNSSEC status for a zone"""
        try:
            if zone_name in self.zone_signatures:
                signature_info = self.zone_signatures[zone_name]
                return {
                    "zone": zone_name,
                    "dnssec_enabled": True,
                    "signed_at": signature_info["signed_at"],
                    "expires_at": signature_info["expires_at"],
                    "key_count": signature_info["key_count"],
                    "status": "valid" if time.time() < signature_info["expires_at"] else "expired"
                }
            else:
                return {
                    "zone": zone_name,
                    "dnssec_enabled": False,
                    "status": "unsigned"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting zone status: {e}")
            return {"zone": zone_name, "status": "error", "error": str(e)}
    
    def rotate_keys(self, zone_name: str) -> bool:
        """Rotate DNSSEC keys for a zone"""
        try:
            # Create new key
            new_key_id = self.create_zone_key(zone_name, "RSA", 2048)
            
            # Mark old keys for retirement (simplified - in production would use KSK/ZSK separation)
            self.logger.info(f"Key rotation initiated for zone {zone_name}: {new_key_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rotating keys for zone {zone_name}: {e}")
            return False
