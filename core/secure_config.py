#!/usr/bin/env python3
"""
Secure configuration storage and management for DNS Server Manager
"""

import json
import os
import hashlib
import hmac
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import threading

class SecureConfigManager:
    """Secure configuration manager with encryption"""
    
    def __init__(self, config_file: str = "config/secure_config.enc"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.lock = threading.RLock()
        
        # Encryption key management
        self.key_file = Path("config/.secure_key")
        self.cipher = None
        self._init_encryption()
        
        # In-memory configuration cache
        self._config_cache: Dict[str, Any] = {}
        self._load_config()
    
    def _init_encryption(self):
        """Initialize encryption with key derivation"""
        try:
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key_data = f.read()
            else:
                # Generate new key
                password = self._get_or_create_master_password()
                salt = os.urandom(16)
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key_data = kdf.derive(password.encode())
                
                # Store salt and key hash for verification
                with open(self.key_file, 'wb') as f:
                    f.write(salt + b':' + hashlib.sha256(key_data).digest())
                
                # Set restrictive permissions
                os.chmod(self.key_file, 0o600)
            
            # Extract salt and verify key
            with open(self.key_file, 'rb') as f:
                stored_data = f.read()
            
            if b':' in stored_data:
                salt, stored_hash = stored_data.split(b':', 1)
                
                # Derive key again with master password
                password = self._get_or_create_master_password()
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key_data = kdf.derive(password.encode())
                
                # Verify key
                if hmac.compare_digest(hashlib.sha256(key_data).digest(), stored_hash):
                    self.cipher = Fernet(base64.urlsafe_b64encode(key_data))
                else:
                    raise ValueError("Invalid master password")
            else:
                # Legacy key format
                self.cipher = Fernet(base64.urlsafe_b64encode(stored_data))
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {e}")
            raise
    
    def _get_or_create_master_password(self) -> str:
        """Get or create master password from environment or file"""
        # Try environment variable first
        password = os.environ.get('DNS_MANAGER_MASTER_PASSWORD')
        if password:
            return password
        
        # Try password file
        password_file = Path("config/.master_password")
        if password_file.exists():
            try:
                with open(password_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        # Generate and store new password
        password = base64.b64encode(os.urandom(32)).decode('ascii')
        try:
            with open(password_file, 'w') as f:
                f.write(password)
            os.chmod(password_file, 0o600)
        except:
            pass
        
        return password
    
    def _load_config(self):
        """Load configuration from encrypted file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'rb') as f:
                    encrypted_data = f.read()
                
                if self.cipher:
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    self._config_cache = json.loads(decrypted_data.decode('utf-8'))
                else:
                    self.logger.error("No cipher available for decryption")
                    self._config_cache = {}
            else:
                self._config_cache = self._get_default_config()
                self._save_config()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._config_cache = self._get_default_config()
    
    def _save_config(self):
        """Save configuration to encrypted file"""
        try:
            if not self.cipher:
                raise ValueError("No cipher available for encryption")
            
            config_data = json.dumps(self._config_cache, indent=2).encode('utf-8')
            encrypted_data = self.cipher.encrypt(config_data)
            
            # Write to temporary file first
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Atomic move
            temp_file.rename(self.config_file)
            
            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default secure configuration"""
        return {
            "server": {
                "bind_address": "0.0.0.0",
                "port": 53,
                "max_connections": 1000,
                "timeout": 5,
                "enable_ipv6": False
            },
            "security": {
                "dnssec_enabled": False,
                "rate_limiting_enabled": True,
                "max_requests_per_second": 100,
                "max_requests_per_minute": 1000,
                "ip_filtering_enabled": True,
                "audit_logging_enabled": True,
                "log_retention_days": 90
            },
            "dnssec": {
                "algorithm": "RSASHA256",
                "key_size": 2048,
                "signature_validity_days": 30,
                "key_rotation_days": 90,
                "nsec_enabled": True
            },
            "database": {
                "path": "config/dns_records.db",
                "backup_enabled": True,
                "backup_interval_hours": 24,
                "max_backups": 7
            },
            "logging": {
                "level": "INFO",
                "file_path": "config/dns_server.log",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "enable_console": True
            },
            "api": {
                "enabled": False,
                "bind_address": "127.0.0.1",
                "port": 8080,
                "require_auth": True,
                "api_key": None,
                "cors_enabled": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        with self.lock:
            try:
                keys = key.split('.')
                value = self._config_cache
                
                for k in keys:
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        return default
                
                return value
                
            except Exception as e:
                self.logger.error(f"Error getting config key '{key}': {e}")
                return default
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Set configuration value by key (supports dot notation)"""
        with self.lock:
            try:
                keys = key.split('.')
                config = self._config_cache
                
                # Navigate to parent
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                
                # Set value
                config[keys[-1]] = value
                
                if save:
                    self._save_config()
                
                self.logger.info(f"Configuration updated: {key} = {value}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error setting config key '{key}': {e}")
                return False
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """Update multiple configuration values"""
        with self.lock:
            try:
                for key, value in updates.items():
                    self.set(key, value, save=False)
                
                if save:
                    self._save_config()
                
                self.logger.info(f"Configuration updated with {len(updates)} changes")
                return True
                
            except Exception as e:
                self.logger.error(f"Error updating configuration: {e}")
                return False
    
    def delete(self, key: str, save: bool = True) -> bool:
        """Delete configuration key"""
        with self.lock:
            try:
                keys = key.split('.')
                config = self._config_cache
                
                # Navigate to parent
                for k in keys[:-1]:
                    if k not in config:
                        return False
                    config = config[k]
                
                # Delete key
                if keys[-1] in config:
                    del config[keys[-1]]
                    
                    if save:
                        self._save_config()
                    
                    self.logger.info(f"Configuration key deleted: {key}")
                    return True
                else:
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error deleting config key '{key}': {e}")
                return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        with self.lock:
            return self._config_cache.copy()
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of configuration"""
        try:
            if not backup_path:
                timestamp = int(time.time())
                backup_path = f"config/secure_config_backup_{timestamp}.enc"
            
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(exist_ok=True)
            
            # Copy encrypted config file
            import shutil
            shutil.copy2(self.config_file, backup_file)
            
            self.logger.info(f"Configuration backed up to: {backup_path}")
            return str(backup_file)
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    def restore(self, backup_path: str) -> bool:
        """Restore configuration from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create backup of current config first
            self.backup()
            
            # Restore from backup
            import shutil
            shutil.copy2(backup_file, self.config_file)
            
            # Reload configuration
            self._load_config()
            
            self.logger.info(f"Configuration restored from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup: {e}")
            return False
    
    def export_plaintext(self, export_path: str, password: Optional[str] = None) -> bool:
        """Export configuration as plaintext (for migration)"""
        try:
            if not password:
                password = self._get_or_create_master_password()
            
            # Verify password
            if not self._verify_password(password):
                raise ValueError("Invalid password")
            
            export_file = Path(export_path)
            export_file.parent.mkdir(exist_ok=True)
            
            with open(export_file, 'w') as f:
                json.dump(self._config_cache, f, indent=2)
            
            self.logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_plaintext(self, import_path: str, password: Optional[str] = None) -> bool:
        """Import configuration from plaintext file"""
        try:
            if not password:
                password = self._get_or_create_master_password()
            
            # Verify password
            if not self._verify_password(password):
                raise ValueError("Invalid password")
            
            import_file = Path(import_path)
            if not import_file.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
            
            with open(import_file, 'r') as f:
                imported_config = json.load(f)
            
            # Validate configuration structure
            if not self._validate_config(imported_config):
                raise ValueError("Invalid configuration structure")
            
            # Create backup first
            self.backup()
            
            # Update configuration
            with self.lock:
                self._config_cache = imported_config
                self._save_config()
            
            self.logger.info(f"Configuration imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def _verify_password(self, password: str) -> bool:
        """Verify master password"""
        try:
            with open(self.key_file, 'rb') as f:
                stored_data = f.read()
            
            if b':' in stored_data:
                salt, stored_hash = stored_data.split(b':', 1)
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key_data = kdf.derive(password.encode())
                
                return hmac.compare_digest(hashlib.sha256(key_data).digest(), stored_hash)
            
            return False
            
        except:
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration structure"""
        try:
            required_sections = ['server', 'security', 'dnssec', 'database', 'logging']
            
            for section in required_sections:
                if section not in config:
                    return False
            
            # Validate server section
            server_config = config['server']
            if not isinstance(server_config.get('port'), int) or not (1 <= server_config.get('port') <= 65535):
                return False
            
            # Validate security section
            security_config = config['security']
            if not isinstance(security_config.get('max_requests_per_second'), int):
                return False
            
            return True
            
        except:
            return False
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change master password"""
        try:
            # Verify old password
            if not self._verify_password(old_password):
                raise ValueError("Invalid old password")
            
            # Generate new salt and key
            salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key_data = kdf.derive(new_password.encode())
            
            # Update key file
            with open(self.key_file, 'wb') as f:
                f.write(salt + b':' + hashlib.sha256(key_data).digest())
            
            # Reinitialize cipher
            self.cipher = Fernet(base64.urlsafe_b64encode(key_data))
            
            # Re-encrypt config with new key
            self._save_config()
            
            self.logger.info("Master password changed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error changing password: {e}")
            return False
    
    def get_config_hash(self) -> str:
        """Get hash of current configuration for integrity checking"""
        try:
            config_str = json.dumps(self._config_cache, sort_keys=True)
            return hashlib.sha256(config_str.encode()).hexdigest()
        except:
            return ""
    
    def verify_integrity(self) -> bool:
        """Verify configuration integrity"""
        try:
            if not self.config_file.exists():
                return False
            
            # Calculate hash of current config
            current_hash = self.get_config_hash()
            
            # Get stored hash (if available)
            stored_hash = self.get("security.config_hash", "")
            
            if stored_hash:
                return current_hash == stored_hash
            else:
                # First time verification, store hash
                self.set("security.config_hash", current_hash)
                return True
                
        except Exception as e:
            self.logger.error(f"Error verifying integrity: {e}")
            return False
