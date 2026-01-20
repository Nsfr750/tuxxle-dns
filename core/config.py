"""
Configuration management for DNS Server
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for DNS server"""
    
    DEFAULT_CONFIG = {
        "dns": {
            "port": 53,
            "bind_address": "0.0.0.0",
            "timeout": 5,
            "max_connections": 1000
        },
        "logging": {
            "level": "INFO",
            "file": "dns_server.log",
            "max_size": 10485760,  # 10MB
            "backup_count": 5
        },
        "ui": {
            "window_width": 1200,
            "window_height": 800,
            "theme": "light"
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger(__name__)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path"""
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_config(self._config)
    
    @property
    def dns_port(self) -> int:
        return self.get("dns.port", 53)
    
    @property
    def bind_address(self) -> str:
        return self.get("dns.bind_address", "0.0.0.0")
    
    @property
    def dns_timeout(self) -> int:
        return self.get("dns.timeout", 5)
    
    @property
    def max_connections(self) -> int:
        return self.get("dns.max_connections", 1000)
