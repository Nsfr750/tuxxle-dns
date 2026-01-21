#!/usr/bin/env python3
"""
Test for DNS Server functionality
"""

import pytest
import threading
import time
import socket
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from core.dns_server import DNSServer
from core.config import Config
from core.dns_records import DNSRecord, DNSRecordType, DNSResponse
from core.database import DNSSQLiteDatabase


class TestDNSServer:
    """Test cases for DNSServer class"""
    
    @pytest.fixture
    def temp_config(self, tmp_path):
        """Create a temporary configuration for testing"""
        config_file = tmp_path / "test_config.json"
        config = Config(str(config_file))
        return config
    
    @pytest.fixture
    def mock_database(self):
        """Create a mock database for testing"""
        db = Mock(spec=DNSSQLiteDatabase)
        db.list_records.return_value = []
        db.add_record.return_value = True
        db.delete_record.return_value = True
        db.update_record.return_value = True
        return db
    
    @pytest.fixture
    def dns_server(self, temp_config, mock_database):
        """Create a DNS server instance for testing"""
        with patch('core.dns_server.DNSSQLiteDatabase', return_value=mock_database):
            server = DNSServer(temp_config)
            return server
    
    def test_server_initialization(self, dns_server):
        """Test DNS server initialization"""
        assert dns_server.config is not None
        assert dns_server.running is False
        assert dns_server.server_socket is None
        assert dns_server.server_thread is None
        assert dns_server.database is not None
        assert isinstance(dns_server.records, dict)
        assert isinstance(dns_server.stats, dict)
        assert 'queries_received' in dns_server.stats
        assert 'responses_sent' in dns_server.stats
        assert 'errors' in dns_server.stats
        assert 'start_time' in dns_server.stats
    
    def test_load_records_from_database(self, dns_server, mock_database):
        """Test loading records from database"""
        # Mock database records
        mock_records = [
            DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300),
            DNSRecord("test.com", DNSRecordType.AAAA, "2001:db8::1", 300)
        ]
        mock_database.list_records.return_value = mock_records
        
        # Reload records
        dns_server._load_records_from_database()
        
        # Verify records were loaded
        assert len(dns_server.records) == 2
        assert "example.com" in dns_server.records
        assert "test.com" in dns_server.records
    
    def test_add_record_to_cache(self, dns_server):
        """Test adding records to cache"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        dns_server._add_record_to_cache(record)
        
        assert "example.com" in dns_server.records
        assert len(dns_server.records["example.com"]) == 1
        assert dns_server.records["example.com"][0] == record
    
    def test_remove_record_from_cache(self, dns_server):
        """Test removing records from cache"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        dns_server._add_record_to_cache(record)
        
        # Remove the record
        dns_server._remove_record_from_cache("example.com", DNSRecordType.A, "192.168.1.1")
        
        # Verify record was removed
        assert len(dns_server.records["example.com"]) == 0
    
    def test_start_server(self, dns_server):
        """Test starting the DNS server"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            
            # Start server
            result = dns_server.start()
            
            assert result is True
            assert dns_server.running is True
            assert dns_server.server_socket is not None
            assert dns_server.server_thread is not None
            assert dns_server.stats['start_time'] is not None
            
            # Verify socket was configured
            mock_sock_instance.bind.assert_called_once()
            mock_sock_instance.listen.assert_called_once()
    
    def test_start_server_already_running(self, dns_server):
        """Test starting server when already running"""
        dns_server.running = True
        
        result = dns_server.start()
        
        assert result is False
        assert dns_server.running is True
    
    def test_stop_server(self, dns_server):
        """Test stopping the DNS server"""
        # Mock server socket and thread
        dns_server.running = True
        dns_server.server_socket = Mock()
        dns_server.server_thread = Mock()
        
        # Stop server
        result = dns_server.stop()
        
        assert result is True
        assert dns_server.running is False
        assert dns_server.server_socket is None
        assert dns_server.server_thread is None
        
        # Verify socket was closed
        dns_server.server_socket.close.assert_called_once()
    
    def test_stop_server_not_running(self, dns_server):
        """Test stopping server when not running"""
        result = dns_server.stop()
        
        assert result is False
        assert dns_server.running is False
    
    def test_add_record(self, dns_server, mock_database):
        """Test adding a DNS record"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        result = dns_server.add_record(record)
        
        assert result is True
        mock_database.add_record.assert_called_once_with(record)
        assert "example.com" in dns_server.records
    
    def test_add_record_database_error(self, dns_server, mock_database):
        """Test adding record when database fails"""
        mock_database.add_record.return_value = False
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        result = dns_server.add_record(record)
        
        assert result is False
        assert "example.com" not in dns_server.records
    
    def test_delete_record(self, dns_server, mock_database):
        """Test deleting a DNS record"""
        # Add record first
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        dns_server._add_record_to_cache(record)
        
        result = dns_server.delete_record("example.com", DNSRecordType.A, "192.168.1.1")
        
        assert result is True
        mock_database.delete_record.assert_called_once()
        assert len(dns_server.records["example.com"]) == 0
    
    def test_delete_record_not_found(self, dns_server, mock_database):
        """Test deleting a record that doesn't exist"""
        result = dns_server.delete_record("nonexistent.com", DNSRecordType.A, "192.168.1.1")
        
        assert result is False
        mock_database.delete_record.assert_not_called()
    
    def test_update_record(self, dns_server, mock_database):
        """Test updating a DNS record"""
        # Add record first
        old_record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        dns_server._add_record_to_cache(old_record)
        
        new_record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.2", 300)
        
        result = dns_server.update_record(old_record, new_record)
        
        assert result is True
        mock_database.update_record.assert_called_once_with(old_record, new_record)
        # Verify cache was updated
        cached_records = dns_server.records["example.com"]
        assert len(cached_records) == 1
        assert cached_records[0].value == "192.168.1.2"
    
    def test_query_record_found(self, dns_server):
        """Test querying a record that exists"""
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        dns_server._add_record_to_cache(record)
        
        result = dns_server.query_record("example.com", DNSRecordType.A)
        
        assert result is not None
        assert isinstance(result, DNSResponse)
        assert len(result.records) == 1
        assert result.records[0] == record
    
    def test_query_record_not_found(self, dns_server):
        """Test querying a record that doesn't exist"""
        result = dns_server.query_record("nonexistent.com", DNSRecordType.A)
        
        assert result is None
    
    def test_get_statistics(self, dns_server):
        """Test getting server statistics"""
        stats = dns_server.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'queries_received' in stats
        assert 'responses_sent' in stats
        assert 'errors' in stats
        assert 'start_time' in stats
        assert 'uptime' in stats
    
    def test_reset_statistics(self, dns_server):
        """Test resetting server statistics"""
        # Set some stats
        dns_server.stats['queries_received'] = 100
        dns_server.stats['responses_sent'] = 95
        dns_server.stats['errors'] = 5
        
        dns_server.reset_statistics()
        
        assert dns_server.stats['queries_received'] == 0
        assert dns_server.stats['responses_sent'] == 0
        assert dns_server.stats['errors'] == 0
        assert dns_server.stats['start_time'] is not None
    
    def test_is_running(self, dns_server):
        """Test checking if server is running"""
        assert dns_server.is_running() is False
        
        dns_server.running = True
        assert dns_server.is_running() is True
    
    def test_get_records_by_domain(self, dns_server):
        """Test getting all records for a domain"""
        record1 = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        record2 = DNSRecord("example.com", DNSRecordType.AAAA, "2001:db8::1", 300)
        dns_server._add_record_to_cache(record1)
        dns_server._add_record_to_cache(record2)
        
        records = dns_server.get_records_by_domain("example.com")
        
        assert len(records) == 2
        assert record1 in records
        assert record2 in records
    
    def test_get_all_records(self, dns_server):
        """Test getting all records"""
        record1 = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        record2 = DNSRecord("test.com", DNSRecordType.AAAA, "2001:db8::1", 300)
        dns_server._add_record_to_cache(record1)
        dns_server._add_record_to_cache(record2)
        
        all_records = dns_server.get_all_records()
        
        assert len(all_records) == 2
        assert record1 in all_records
        assert record2 in all_records
    
    @patch('socket.socket')
    def test_handle_dns_query(self, mock_socket, dns_server):
        """Test handling DNS queries"""
        # Mock client socket and data
        mock_client_socket = Mock()
        mock_client_socket.recv.return_value = b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01'
        mock_client_socket.sendto.return_value = None
        
        # Add a record to respond with
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        dns_server._add_record_to_cache(record)
        
        # Handle the query
        dns_server._handle_dns_query(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify statistics were updated
        assert dns_server.stats['queries_received'] == 1
        assert dns_server.stats['responses_sent'] == 1
        
        # Verify response was sent
        mock_client_socket.sendto.assert_called_once()
    
    def test_server_thread_exception_handling(self, dns_server):
        """Test server thread exception handling"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_socket.return_value = mock_sock_instance
            mock_sock_instance.accept.side_effect = Exception("Test exception")
            
            # Start server
            dns_server.start()
            
            # Wait a bit for the thread to run
            time.sleep(0.1)
            
            # Stop server
            dns_server.stop()
            
            # Verify error was counted
            assert dns_server.stats['errors'] >= 0


if __name__ == "__main__":
    pytest.main([__file__])
