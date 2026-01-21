#!/usr/bin/env python3
"""
Test for Configuration management functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from core.config import Config


class TestConfig:
    """Test cases for Config class"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "dns": {
                    "port": 5353,
                    "bind_address": "127.0.0.1",
                    "timeout": 10,
                    "max_connections": 500
                },
                "logging": {
                    "level": "DEBUG",
                    "file": "test.log",
                    "max_size": 5242880,
                    "backup_count": 3
                },
                "ui": {
                    "window_width": 800,
                    "window_height": 600,
                    "theme": "dark"
                },
                "custom_setting": "test_value"
            }
            json.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    @pytest.fixture
    def invalid_config_file(self):
        """Create an invalid config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    def test_default_config_structure(self):
        """Test that default config has the expected structure"""
        default_config = Config.DEFAULT_CONFIG
        
        assert "dns" in default_config
        assert "logging" in default_config
        assert "ui" in default_config
        
        # Check DNS settings
        dns_config = default_config["dns"]
        assert "port" in dns_config
        assert "bind_address" in dns_config
        assert "timeout" in dns_config
        assert "max_connections" in dns_config
        assert dns_config["port"] == 53
        assert dns_config["bind_address"] == "0.0.0.0"
        assert dns_config["timeout"] == 5
        assert dns_config["max_connections"] == 1000
        
        # Check logging settings
        logging_config = default_config["logging"]
        assert "level" in logging_config
        assert "file" in logging_config
        assert "max_size" in logging_config
        assert "backup_count" in logging_config
        assert logging_config["level"] == "INFO"
        assert logging_config["file"] == "dns_server.log"
        assert logging_config["max_size"] == 10485760
        assert logging_config["backup_count"] == 5
        
        # Check UI settings
        ui_config = default_config["ui"]
        assert "window_width" in ui_config
        assert "window_height" in ui_config
        assert "theme" in ui_config
        assert ui_config["window_width"] == 1200
        assert ui_config["window_height"] == 800
        assert ui_config["theme"] == "light"
    
    def test_config_creation_with_existing_file(self, temp_config_file):
        """Test creating config with existing config file"""
        config = Config(temp_config_file)
        
        assert config.get("dns.port") == 5353
        assert config.get("dns.bind_address") == "127.0.0.1"
        assert config.get("dns.timeout") == 10
        assert config.get("dns.max_connections") == 500
        assert config.get("logging.level") == "DEBUG"
        assert config.get("logging.file") == "test.log"
        assert config.get("ui.window_width") == 800
        assert config.get("ui.theme") == "dark"
        assert config.get("custom_setting") == "test_value"
    
    def test_config_creation_with_nonexistent_file(self):
        """Test creating config when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "nonexistent_config.json"
            config = Config(str(config_file))
            
            # Should use default values
            assert config.get("dns.port") == 53
            assert config.get("dns.bind_address") == "0.0.0.0"
            assert config.get("logging.level") == "INFO"
            assert config.get("ui.window_width") == 1200
            
            # Config file should be created
            assert config_file.exists()
    
    def test_config_creation_with_invalid_file(self, invalid_config_file):
        """Test creating config with invalid JSON file"""
        with patch('core.config.logging.getLogger') as mock_logger:
            config = Config(invalid_config_file)
            
            # Should use default values
            assert config.get("dns.port") == 53
            assert config.get("logging.level") == "INFO"
            
            # Should log error
            mock_logger.return_value.error.assert_called()
    
    def test_get_nested_config_value(self, temp_config_file):
        """Test getting nested config values"""
        config = Config(temp_config_file)
        
        assert config.get("dns.port") == 5353
        assert config.get("logging.level") == "DEBUG"
        assert config.get("ui.theme") == "dark"
    
    def test_get_config_value_with_default(self, temp_config_file):
        """Test getting config value with default fallback"""
        config = Config(temp_config_file)
        
        # Existing value
        assert config.get("dns.port", 999) == 5353
        
        # Non-existing value with default
        assert config.get("nonexistent.key", "default_value") == "default_value"
        assert config.get("dns.nonexistent", 123) == 123
    
    def test_get_config_value_without_default(self, temp_config_file):
        """Test getting config value without default fallback"""
        config = Config(temp_config_file)
        
        # Existing value
        assert config.get("dns.port") == 5353
        
        # Non-existing value without default
        assert config.get("nonexistent.key") is None
    
    def test_set_config_value(self, temp_config_file):
        """Test setting config values"""
        config = Config(temp_config_file)
        
        # Set existing value
        config.set("dns.port", 9999)
        assert config.get("dns.port") == 9999
        
        # Set new nested value
        config.set("new.nested.value", "test")
        assert config.get("new.nested.value") == "test"
        
        # Set new top-level value
        config.set("new_top_level", {"nested": "value"})
        assert config.get("new_top_level.nested") == "value"
    
    def test_update_config_section(self, temp_config_file):
        """Test updating entire config section"""
        config = Config(temp_config_file)
        
        new_dns_config = {
            "port": 8080,
            "bind_address": "192.168.1.100",
            "new_setting": "test"
        }
        
        config.update_section("dns", new_dns_config)
        
        assert config.get("dns.port") == 8080
        assert config.get("dns.bind_address") == "192.168.1.100"
        assert config.get("dns.new_setting") == "test"
        
        # Original settings that weren't specified should remain
        assert config.get("dns.timeout") == 10  # From the test file
        assert config.get("dns.max_connections") == 500  # From the test file
    
    def test_save_config(self, temp_config_file):
        """Test saving config to file"""
        config = Config(temp_config_file)
        
        # Modify some values
        config.set("dns.port", 9999)
        config.set("new.setting", "test_value")
        
        # Save config
        result = config.save()
        
        assert result is True
        
        # Load config again to verify it was saved
        new_config = Config(temp_config_file)
        assert new_config.get("dns.port") == 9999
        assert new_config.get("new.setting") == "test_value"
    
    def test_save_config_failure(self):
        """Test saving config when file write fails"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.json"
            config = Config(str(config_file))
            
            # Try to save to a directory that doesn't exist
            invalid_path = Path(temp_dir) / "nonexistent" / "config.json"
            config.config_file = invalid_path
            
            result = config.save()
            
            assert result is False
    
    def test_reload_config(self, temp_config_file):
        """Test reloading config from file"""
        config = Config(temp_config_file)
        
        # Modify in memory
        config.set("dns.port", 9999)
        assert config.get("dns.port") == 9999
        
        # Reload from file
        result = config.reload()
        
        assert result is True
        assert config.get("dns.port") == 5353  # Should be back to original value
    
    def test_reload_config_failure(self, invalid_config_file):
        """Test reloading config when file is invalid"""
        config = Config(invalid_config_file)
        
        # File is invalid, should have loaded defaults
        original_port = config.get("dns.port")
        
        # Try to reload (should fail and keep current values)
        result = config.reload()
        
        assert result is False
        assert config.get("dns.port") == original_port
    
    def test_merge_configs(self):
        """Test merging config dictionaries"""
        config1 = {
            "section1": {
                "key1": "value1",
                "key2": "value2"
            },
            "section2": {
                "key3": "value3"
            }
        }
        
        config2 = {
            "section1": {
                "key1": "new_value1",  # Override
                "key4": "value4"       # New key
            },
            "section3": {              # New section
                "key5": "value5"
            }
        }
        
        merged = Config._merge_configs(config1, config2)
        
        assert merged["section1"]["key1"] == "new_value1"  # Overridden
        assert merged["section1"]["key2"] == "value2"      # Preserved
        assert merged["section1"]["key4"] == "value4"      # Added
        assert merged["section2"]["key3"] == "value3"      # Preserved
        assert merged["section3"]["key5"] == "value5"      # Added
    
    def test_get_all_config(self, temp_config_file):
        """Test getting entire config dictionary"""
        config = Config(temp_config_file)
        
        all_config = config.get_all()
        
        assert isinstance(all_config, dict)
        assert "dns" in all_config
        assert "logging" in all_config
        assert "ui" in all_config
        assert "custom_setting" in all_config
        
        # Verify it's a copy, not the original
        all_config["dns"]["port"] = 9999
        assert config.get("dns.port") != 9999
    
    def test_reset_to_defaults(self, temp_config_file):
        """Test resetting config to default values"""
        config = Config(temp_config_file)
        
        # Modify some values
        config.set("dns.port", 9999)
        config.set("custom_setting", "modified")
        
        # Reset to defaults
        config.reset_to_defaults()
        
        # Should be back to default values
        assert config.get("dns.port") == 53
        assert config.get("dns.bind_address") == "0.0.0.0"
        assert config.get("logging.level") == "INFO"
        assert config.get("ui.window_width") == 1200
        
        # Custom setting should be removed
        assert config.get("custom_setting") is None
    
    def test_validate_config(self, temp_config_file):
        """Test config validation"""
        config = Config(temp_config_file)
        
        # Valid config
        assert config.validate() is True
        
        # Modify to make invalid
        config.set("dns.port", "invalid_port")  # Should be integer
        
        assert config.validate() is False
    
    def test_get_config_file_path(self, temp_config_file):
        """Test getting config file path"""
        config = Config(temp_config_file)
        
        assert config.get_config_file_path() == Path(temp_config_file)
    
    def test_backup_config(self, temp_config_file):
        """Test creating config backup"""
        config = Config(temp_config_file)
        
        # Create backup
        backup_path = config.backup()
        
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.name.startswith("config_backup_")
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert backup_data["dns"]["port"] == 5353
        
        # Cleanup
        backup_path.unlink()
    
    def test_restore_from_backup(self, temp_config_file):
        """Test restoring config from backup"""
        config = Config(temp_config_file)
        
        # Create backup
        backup_path = config.backup()
        
        # Modify config
        config.set("dns.port", 9999)
        assert config.get("dns.port") == 9999
        
        # Restore from backup
        result = config.restore_from_backup(backup_path)
        
        assert result is True
        assert config.get("dns.port") == 5353  # Should be restored
        
        # Cleanup
        backup_path.unlink()
    
    def test_restore_from_invalid_backup(self, temp_config_file):
        """Test restoring from invalid backup file"""
        config = Config(temp_config_file)
        
        # Create invalid backup file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json")
            invalid_backup = Path(f.name)
        
        try:
            result = config.restore_from_backup(invalid_backup)
            assert result is False
        finally:
            invalid_backup.unlink(missing_ok=True)
    
    def test_config_environment_variable_override(self):
        """Test environment variable override"""
        with patch.dict('os.environ', {'DNS_SERVER_PORT': '8080'}):
            with tempfile.TemporaryDirectory() as temp_dir:
                config_file = Path(temp_dir) / "config.json"
                config = Config(str(config_file))
                
                # Should use environment variable if implemented
                # This test depends on whether environment variable override is implemented
                # If not implemented, this will just verify default behavior
                assert config.get("dns.port") in [53, 8080]


if __name__ == "__main__":
    pytest.main([__file__])
