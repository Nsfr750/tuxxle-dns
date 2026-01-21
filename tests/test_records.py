#!/usr/bin/env python3
"""
Test for DNS Records functionality
"""

import pytest
from unittest.mock import Mock, patch

from core.dns_records import DNSRecord, DNSRecordType, DNSResponse, DNSQuestion


class TestDNSRecordType:
    """Test cases for DNSRecordType enum"""
    
    def test_record_type_values(self):
        """Test DNS record type values"""
        assert DNSRecordType.A.value == 1
        assert DNSRecordType.AAAA.value == 28
        assert DNSRecordType.CNAME.value == 5
        assert DNSRecordType.MX.value == 15
        assert DNSRecordType.TXT.value == 16
        assert DNSRecordType.NS.value == 2
        assert DNSRecordType.SOA.value == 6
        assert DNSRecordType.PTR.value == 12
        assert DNSRecordType.SRV.value == 33
    
    def test_from_int(self):
        """Test creating record type from integer value"""
        assert DNSRecordType.from_int(1) == DNSRecordType.A
        assert DNSRecordType.from_int(28) == DNSRecordType.AAAA
        assert DNSRecordType.from_int(5) == DNSRecordType.CNAME
        
        # Test invalid value
        with pytest.raises(ValueError):
            DNSRecordType.from_int(999)
    
    def test_record_type_str(self):
        """Test string representation of record types"""
        assert str(DNSRecordType.A) == "A"
        assert str(DNSRecordType.AAAA) == "AAAA"
        assert str(DNSRecordType.CNAME) == "CNAME"


class TestDNSRecord:
    """Test cases for DNSRecord class"""
    
    def test_record_creation(self):
        """Test creating a DNS record"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        assert record.name == "example.com"
        assert record.record_type == DNSRecordType.A
        assert record.value == "192.168.1.1"
        assert record.ttl == 300
        assert isinstance(record.created_at, float)
    
    def test_record_with_custom_timestamp(self):
        """Test creating a record with custom timestamp"""
        timestamp = 1234567890.0
        record = DNSRecord("test.com", DNSRecordType.AAAA, "2001:db8::1", 600, timestamp)
        
        assert record.created_at == timestamp
    
    def test_record_equality(self):
        """Test record equality comparison"""
        record1 = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        record2 = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        record3 = DNSRecord("example.com", DNSRecordType.A, "192.168.1.2", 300)
        
        assert record1 == record2
        assert record1 != record3
        assert hash(record1) == hash(record2)
        assert hash(record1) != hash(record3)
    
    def test_record_str_representation(self):
        """Test string representation of DNS record"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        str_repr = str(record)
        
        assert "example.com" in str_repr
        assert "A" in str_repr
        assert "192.168.1.1" in str_repr
        assert "300" in str_repr
    
    def test_record_repr(self):
        """Test repr representation of DNS record"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        repr_str = repr(record)
        
        assert "DNSRecord" in repr_str
        assert "example.com" in repr_str
        assert "A" in repr_str
    
    def test_a_record_validation(self):
        """Test A record IP address validation"""
        # Valid IPv4 addresses
        valid_ips = [
            "192.168.1.1",
            "8.8.8.8",
            "127.0.0.1",
            "255.255.255.255",
            "0.0.0.0"
        ]
        
        for ip in valid_ips:
            record = DNSRecord("example.com", DNSRecordType.A, ip, 300)
            assert record.is_valid()
        
        # Invalid IPv4 addresses
        invalid_ips = [
            "256.256.256.256",
            "192.168.1",
            "192.168.1.1.1",
            "not.an.ip.address",
            "",
            "192.168.1.-1"
        ]
        
        for ip in invalid_ips:
            record = DNSRecord("example.com", DNSRecordType.A, ip, 300)
            assert not record.is_valid()
    
    def test_aaaa_record_validation(self):
        """Test AAAA record IPv6 address validation"""
        # Valid IPv6 addresses
        valid_ips = [
            "2001:db8::1",
            "::1",
            "fe80::1",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
            "2001:db8:85a3::8a2e:370:7334",
            "::ffff:192.168.1.1"
        ]
        
        for ip in valid_ips:
            record = DNSRecord("example.com", DNSRecordType.AAAA, ip, 300)
            assert record.is_valid()
        
        # Invalid IPv6 addresses
        invalid_ips = [
            "2001:db8::1::1",
            "2001:db8:zzzz::1",
            "2001:db8::99999",
            "",
            "not.an.ipv6.address"
        ]
        
        for ip in invalid_ips:
            record = DNSRecord("example.com", DNSRecordType.AAAA, ip, 300)
            assert not record.is_valid()
    
    def test_cname_record_validation(self):
        """Test CNAME record validation"""
        # Valid CNAME values
        valid_cnames = [
            "www.example.com",
            "api.test.com",
            "sub.domain.example.com",
            "example.com"
        ]
        
        for cname in valid_cnames:
            record = DNSRecord("example.com", DNSRecordType.CNAME, cname, 300)
            assert record.is_valid()
        
        # Invalid CNAME values
        invalid_cnames = [
            "",
            " ",
            "invalid..domain",
            ".invalid.domain",
            "invalid.domain."
        ]
        
        for cname in invalid_cnames:
            record = DNSRecord("example.com", DNSRecordType.CNAME, cname, 300)
            assert not record.is_valid()
    
    def test_mx_record_validation(self):
        """Test MX record validation"""
        # Valid MX records (format: "priority mail.server.com")
        valid_mx = [
            "10 mail.example.com",
            "20 smtp.test.com",
            "5 mail.domain.com",
            "0 mail.server.com"
        ]
        
        for mx in valid_mx:
            record = DNSRecord("example.com", DNSRecordType.MX, mx, 300)
            assert record.is_valid()
        
        # Invalid MX records
        invalid_mx = [
            "mail.example.com",  # Missing priority
            "10",  # Missing server
            "999 mail.example.com",  # Priority too high
            "-1 mail.example.com",  # Negative priority
            "10 invalid..domain",  # Invalid domain
            ""
        ]
        
        for mx in invalid_mx:
            record = DNSRecord("example.com", DNSRecordType.MX, mx, 300)
            assert not record.is_valid()
    
    def test_txt_record_validation(self):
        """Test TXT record validation"""
        # Valid TXT records
        valid_txt = [
            "v=spf1 include:_spf.google.com ~all",
            "This is a text record",
            "key=value",
            "some-text-data-123",
            ""
        ]
        
        for txt in valid_txt:
            record = DNSRecord("example.com", DNSRecordType.TXT, txt, 300)
            assert record.is_valid()
        
        # TXT records accept most values, but test very long ones
        long_txt = "a" * 1000  # Very long TXT record
        record = DNSRecord("example.com", DNSRecordType.TXT, long_txt, 300)
        # Should still be valid (DNS TXT can be up to 65535 bytes in total)
        assert record.is_valid()
    
    def test_ns_record_validation(self):
        """Test NS record validation"""
        # Valid NS records
        valid_ns = [
            "ns1.example.com",
            "ns2.test.com",
            "ns.domain.com",
            "ns1.example.com."
        ]
        
        for ns in valid_ns:
            record = DNSRecord("example.com", DNSRecordType.NS, ns, 300)
            assert record.is_valid()
        
        # Invalid NS records
        invalid_ns = [
            "",
            "invalid..domain",
            ".invalid.domain",
            "not a domain"
        ]
        
        for ns in invalid_ns:
            record = DNSRecord("example.com", DNSRecordType.NS, ns, 300)
            assert not record.is_valid()
    
    def test_soa_record_validation(self):
        """Test SOA record validation"""
        # Valid SOA records (format: "primary admin serial refresh retry expire minimum")
        valid_soa = [
            "ns1.example.com admin.example.com 2024010101 7200 3600 604800 86400",
            "ns.test.com hostmaster.test.com 123456789 3600 1800 1209600 43200"
        ]
        
        for soa in valid_soa:
            record = DNSRecord("example.com", DNSRecordType.SOA, soa, 300)
            assert record.is_valid()
        
        # Invalid SOA records
        invalid_soa = [
            "",  # Empty
            "ns1.example.com",  # Missing parts
            "ns1.example.com admin.example.com",  # Missing serial and other fields
            "ns1.example.com admin.example.com notanumber 7200 3600 604800 86400",  # Invalid serial
        ]
        
        for soa in invalid_soa:
            record = DNSRecord("example.com", DNSRecordType.SOA, soa, 300)
            assert not record.is_valid()
    
    def test_ptr_record_validation(self):
        """Test PTR record validation"""
        # Valid PTR records
        valid_ptr = [
            "www.example.com",
            "mail.test.com",
            "server.domain.com"
        ]
        
        for ptr in valid_ptr:
            record = DNSRecord("1.168.192.in-addr.arpa", DNSRecordType.PTR, ptr, 300)
            assert record.is_valid()
        
        # Invalid PTR records
        invalid_ptr = [
            "",
            "invalid..domain",
            ".invalid.domain"
        ]
        
        for ptr in invalid_ptr:
            record = DNSRecord("1.168.192.in-addr.arpa", DNSRecordType.PTR, ptr, 300)
            assert not record.is_valid()
    
    def test_srv_record_validation(self):
        """Test SRV record validation"""
        # Valid SRV records (format: "priority weight port target")
        valid_srv = [
            "10 5 5060 sip.example.com",
            "0 100 443 www.example.com",
            "20 10 8080 api.test.com"
        ]
        
        for srv in valid_srv:
            record = DNSRecord("_service._tcp.example.com", DNSRecordType.SRV, srv, 300)
            assert record.is_valid()
        
        # Invalid SRV records
        invalid_srv = [
            "",  # Empty
            "10 5",  # Missing port and target
            "10 5 notaport target.com",  # Invalid port
            "10 5 5060",  # Missing target
            "10 5 5060 invalid..domain",  # Invalid domain
        ]
        
        for srv in invalid_srv:
            record = DNSRecord("_service._tcp.example.com", DNSRecordType.SRV, srv, 300)
            assert not record.is_valid()
    
    def test_get_mx_components(self):
        """Test extracting MX record components"""
        record = DNSRecord("example.com", DNSRecordType.MX, "10 mail.example.com", 300)
        
        priority, server = record.get_mx_components()
        
        assert priority == 10
        assert server == "mail.example.com"
    
    def test_get_soa_components(self):
        """Test extracting SOA record components"""
        soa_value = "ns1.example.com admin.example.com 2024010101 7200 3600 604800 86400"
        record = DNSRecord("example.com", DNSRecordType.SOA, soa_value, 300)
        
        components = record.get_soa_components()
        
        assert components.primary == "ns1.example.com"
        assert components.admin == "admin.example.com"
        assert components.serial == 2024010101
        assert components.refresh == 7200
        assert components.retry == 3600
        assert components.expire == 604800
        assert components.minimum == 86400
    
    def test_get_srv_components(self):
        """Test extracting SRV record components"""
        record = DNSRecord("_service._tcp.example.com", DNSRecordType.SRV, "10 5 5060 sip.example.com", 300)
        
        priority, weight, port, target = record.get_srv_components()
        
        assert priority == 10
        assert weight == 5
        assert port == 5060
        assert target == "sip.example.com"


class TestDNSQuestion:
    """Test cases for DNSQuestion class"""
    
    def test_question_creation(self):
        """Test creating a DNS question"""
        question = DNSQuestion("example.com", DNSRecordType.A)
        
        assert question.name == "example.com"
        assert question.question_type == DNSRecordType.A
        assert question.question_class == 1  # IN class
    
    def test_question_equality(self):
        """Test question equality"""
        q1 = DNSQuestion("example.com", DNSRecordType.A)
        q2 = DNSQuestion("example.com", DNSRecordType.A)
        q3 = DNSQuestion("test.com", DNSRecordType.A)
        
        assert q1 == q2
        assert q1 != q3
        assert hash(q1) == hash(q2)
        assert hash(q1) != hash(q3)
    
    def test_question_str(self):
        """Test string representation of DNS question"""
        question = DNSQuestion("example.com", DNSRecordType.A)
        str_repr = str(question)
        
        assert "example.com" in str_repr
        assert "A" in str_repr


class TestDNSResponse:
    """Test cases for DNSResponse class"""
    
    def test_response_creation(self):
        """Test creating a DNS response"""
        records = [
            DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        ]
        response = DNSResponse(records, authoritative=True)
        
        assert response.records == records
        assert response.authoritative is True
        assert response.response_code == 0  # NOERROR
    
    def test_response_creation_with_error(self):
        """Test creating a DNS response with error code"""
        response = DNSResponse([], response_code=3)  # NXDOMAIN
        
        assert response.records == []
        assert response.authoritative is False
        assert response.response_code == 3
    
    def test_response_add_record(self):
        """Test adding records to response"""
        response = DNSResponse([])
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        response.add_record(record)
        
        assert len(response.records) == 1
        assert response.records[0] == record
    
    def test_response_get_records_by_type(self):
        """Test getting records by type from response"""
        records = [
            DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300),
            DNSRecord("example.com", DNSRecordType.AAAA, "2001:db8::1", 300),
            DNSRecord("test.com", DNSRecordType.A, "192.168.1.2", 300)
        ]
        response = DNSResponse(records)
        
        a_records = response.get_records_by_type(DNSRecordType.A)
        aaaa_records = response.get_records_by_type(DNSRecordType.AAAA)
        
        assert len(a_records) == 2
        assert len(aaaa_records) == 1
        assert all(r.record_type == DNSRecordType.A for r in a_records)
        assert all(r.record_type == DNSRecordType.AAAA for r in aaaa_records)
    
    def test_response_is_success(self):
        """Test checking if response indicates success"""
        # Successful response
        response_success = DNSResponse([], response_code=0)
        assert response_success.is_success()
        
        # Error response
        response_error = DNSResponse([], response_code=3)
        assert not response_error.is_success()
    
    def test_response_str(self):
        """Test string representation of DNS response"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        response = DNSResponse([record])
        
        str_repr = str(response)
        
        assert "example.com" in str_repr
        assert "A" in str_repr
        assert "1 records" in str_repr


if __name__ == "__main__":
    pytest.main([__file__])
