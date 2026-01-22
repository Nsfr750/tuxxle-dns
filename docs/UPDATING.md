# Updating Guide

This document provides comprehensive guidelines for updating the DNS Server Manager application. It covers version management, update procedures, and maintenance practices.

## Table of Contents

- [Update Philosophy](#update-philosophy)
- [Version Management](#version-management)
- [Update Types](#update-types)
- [Update Procedures](#update-procedures)
- [Automated Updates](#automated-updates)
- [Manual Updates](#manual-updates)
- [Rollback Procedures](#rollback-procedures)
- [Compatibility](#compatibility)
- [Testing Updates](#testing-updates)
- [Release Process](#release-process)

## Update Philosophy

### Principles

1. **Semantic Versioning**: Follow Semantic Versioning 2.0.0 strictly
2. **Backward Compatibility**: Maintain compatibility within major versions
3. **Incremental Updates**: Small, frequent updates are preferred
4. **User Safety**: Never compromise user data or configuration
5. **Transparent Communication**: Clear changelog and update notifications

### Update Strategy

- **Patch Releases** (x.x.X): Bug fixes, security updates, minor improvements
- **Minor Releases** (x.X.x): New features, improvements, deprecations
- **Major Releases** (X.x.x): Breaking changes, major new features

## Version Management

### Semantic Versioning

We follow Semantic Versioning 2.0.0:

```text
MAJOR.MINOR.PATCH
```

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

### Version File

Version information is stored in `version.py`:

```python
#!/usr/bin/env python3
"""
Version information for DNS Server Manager
"""

__version__ = "1.2.3"
__version_info__ = (1, 2, 3)
__build__ = "20240101-1234"
__release_date__ = "2024-01-01"
```

### Version Validation

```python
def validate_version(version_string: str) -> bool:
    """Validate semantic version string"""
    import re
    pattern = r'^\d+\.\d+\.\d+(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    return bool(re.match(pattern, version_string))
```

## Update Types

### Patch Updates (x.x.X)

**Characteristics:**
- Bug fixes only
- Security patches
- Performance improvements
- Documentation updates
- Translation updates

**Impact:**
- No breaking changes
- Safe to apply automatically
- No user intervention required

**Examples:**
- Fix DNS record validation bug
- Patch security vulnerability
- Improve query performance
- Add missing translations

### Minor Updates (x.X.x)

**Characteristics:**
- New features
- Enhancements
- Deprecations (with warnings)
- Configuration changes (backward-compatible)

**Impact:**
- No breaking changes
- May require user attention
- Optional automatic updates

**Examples:**
- Add new DNS record type support
- Implement UI theme system
- Add configuration backup feature
- Deprecate old configuration format

### Major Updates (X.x.x)

**Characteristics:**
- Breaking changes
- Major new features
- Architecture changes
- Database schema changes

**Impact:**
- Breaking changes
- Requires user intervention
- Manual update process
- Migration required

**Examples:**
- New database format
- Redesigned user interface
- Changed configuration format
- New API endpoints

## Update Procedures

### Automated Update System

The application includes an automated update system (`update.py`):

```python
class UpdateManager:
    """Manages application updates"""
    
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.update_server = "https://updates.tuxxle.org"
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check for available updates"""
        pass
    
    def download_update(self, update_info: UpdateInfo) -> bool:
        """Download update package"""
        pass
    
    def install_update(self, update_path: str) -> bool:
        """Install downloaded update"""
        pass
    
    def verify_update(self, update_path: str) -> bool:
        """Verify update integrity"""
        pass
```

### Update Check Process

1. **Version Check**: Compare current version with latest available
2. **Compatibility Check**: Verify update compatibility
3. **Dependency Check**: Check system requirements
4. **Permission Check**: Verify installation permissions
5. **Space Check**: Ensure sufficient disk space

### Update Download Process

1. **Metadata Download**: Fetch update information
2. **Signature Verification**: Verify update authenticity
3. **Package Download**: Download update package
4. **Integrity Check**: Verify checksum
5. **Virus Scan**: Security scan (optional)

### Update Installation Process

1. **Backup**: Create backup of current installation
2. **Preparation**: Prepare installation environment
3. **Installation**: Apply update files
4. **Migration**: Run migration scripts
5. **Verification**: Verify installation success
6. **Cleanup**: Remove temporary files

## Automated Updates

### Update Configuration

Configuration for automated updates:

```python
# config.json
{
    "updates": {
        "enabled": true,
        "auto_install": false,
        "check_interval": 86400,
        "beta_updates": false,
        "notify_before_install": true,
        "backup_before_update": true,
        "update_server": "https://updates.tuxxle.org"
    }
}
```

### Update Scheduler

```python
import threading
import time

class UpdateScheduler:
    """Schedules automatic update checks"""
    
    def __init__(self, update_manager: UpdateManager):
        self.update_manager = update_manager
        self.running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start the update scheduler"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                update_info = self.update_manager.check_for_updates()
                if update_info:
                    self._handle_available_update(update_info)
                
                # Sleep for configured interval
                time.sleep(self.update_manager.check_interval)
            
            except Exception as e:
                logging.error(f"Update scheduler error: {e}")
                time.sleep(3600)  # Wait 1 hour on error
```

### Update Notifications

```python
class UpdateNotifier:
    """Handles update notifications"""
    
    def notify_update_available(self, update_info: UpdateInfo):
        """Notify user about available update"""
        message = f"Update {update_info.version} is available"
        
        if update_info.is_critical:
            message += " (Critical Update)"
        
        # Show notification
        self._show_notification(message, update_info)
    
    def notify_update_installed(self, version: str):
        """Notify user about successful update"""
        self._show_notification(f"Successfully updated to version {version}")
    
    def notify_update_failed(self, error: str):
        """Notify user about update failure"""
        self._show_notification(f"Update failed: {error}", error=True)
```

## Manual Updates

### Manual Update Process

1. **Download**: Download update package from website
2. **Verify**: Verify package integrity and signature
3. **Backup**: Create backup of current installation
4. **Install**: Run manual installation process
5. **Migrate**: Run migration scripts if needed
6. **Verify**: Verify installation success

### Manual Update Commands

```bash
# Check for updates
python update.py --check

# Download specific version
python update.py --download 1.2.3

# Install downloaded update
python update.py --install update_package.zip

# Verify installation
python update.py --verify

# Rollback update
python update.py --rollback
```

### Update Package Structure

```text
dns-server-manager-update-1.2.3.zip
├── manifest.json          # Update metadata
├── files/                 # Updated files
│   ├── core/
│   ├── ui/
│   └── lang/
├── migrations/            # Database migrations
│   ├── migrate_1_2_0.sql
│   └── migrate_1_2_3.sql
├── scripts/               # Installation scripts
│   ├── install.py
│   ├── migrate.py
│   └── cleanup.py
├── checksums.txt          # File checksums
└── signature.sig          # Digital signature
```

### Update Manifest

```json
{
    "version": "1.2.3",
    "previous_version": "1.2.2",
    "release_date": "2024-01-01",
    "update_type": "patch",
    "critical": false,
    "description": "Bug fixes and performance improvements",
    "changes": [
        "Fix DNS record validation bug",
        "Improve query performance",
        "Add missing Spanish translations"
    ],
    "requirements": {
        "python": ">=3.8",
        "disk_space": "50MB",
        "memory": "256MB"
    },
    "files": [
        {
            "path": "core/dns_server.py",
            "checksum": "sha256:abc123...",
            "size": 12345
        }
    ],
    "migrations": [
        "migrate_1_2_3.sql"
    ]
}
```

## Rollback Procedures

### Automatic Rollback

```python
class RollbackManager:
    """Manages update rollbacks"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.current_backup = None
    
    def create_backup(self) -> str:
        """Create backup of current installation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup
        self._create_backup(backup_path)
        
        return backup_name
    
    def rollback_to_backup(self, backup_name: str) -> bool:
        """Rollback to specific backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return False
        
        # Stop application
        self._stop_application()
        
        try:
            # Restore from backup
            self._restore_backup(backup_path)
            
            # Restart application
            self._restart_application()
            
            return True
        
        except Exception as e:
            logging.error(f"Rollback failed: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """List available backups"""
        backups = []
        
        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir():
                backup_info = self._load_backup_info(backup_dir)
                backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x.created_at, reverse=True)
```

### Manual Rollback

1. **Stop Application**: Stop the DNS server application
2. **Select Backup**: Choose appropriate backup version
3. **Restore Files**: Restore files from backup
4. **Restore Database**: Restore database from backup
5. **Verify**: Verify rollback success
6. **Restart**: Restart the application

### Rollback Safety

- **Automatic Backup**: Always create backup before update
- **Verification**: Verify backup integrity
- **Test Rollback**: Test rollback procedure
- **Multiple Backups**: Keep multiple backup versions
- **Cleanup**: Clean up old backups periodically

## Compatibility

### Version Compatibility Matrix

| Current Version | Can Update To | Auto Update | Notes |
|------------------|---------------|-------------|-------|
| 1.0.x | 1.0.y, 1.1.x | Yes | Patch and minor updates |
| 1.1.x | 1.1.y, 1.2.x | Yes | Patch and minor updates |
| 1.2.x | 1.2.y, 2.0.x | Patch only | Major update requires manual |

### API Compatibility

```python
class APICompatibility:
    """Manages API compatibility across versions"""
    
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.compatibility_matrix = {
            "1.0": {"1.0": True, "1.1": True, "1.2": True},
            "1.1": {"1.1": True, "1.2": True, "2.0": False},
            "1.2": {"1.2": True, "2.0": False}
        }
    
    def is_compatible(self, target_version: str) -> bool:
        """Check if target version is compatible"""
        current_major = self.current_version.split('.')[0]
        target_major = target_version.split('.')[0]
        
        return self.compatibility_matrix.get(current_major, {}).get(target_major, False)
```

### Configuration Compatibility

```python
class ConfigCompatibility:
    """Manages configuration compatibility"""
    
    def migrate_config(self, config_path: str, from_version: str, to_version: str) -> bool:
        """Migrate configuration from one version to another"""
        try:
            # Load current configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Apply migration rules
            migrated_config = self._apply_migrations(config, from_version, to_version)
            
            # Save migrated configuration
            with open(config_path, 'w') as f:
                json.dump(migrated_config, f, indent=2)
            
            return True
        
        except Exception as e:
            logging.error(f"Config migration failed: {e}")
            return False
    
    def _apply_migrations(self, config: dict, from_version: str, to_version: str) -> dict:
        """Apply configuration migrations"""
        # Migration rules based on version
        if from_version == "1.0" and to_version == "1.1":
            # Add new configuration options
            config.setdefault("ui", {}).setdefault("theme", "light")
            config.setdefault("updates", {}).setdefault("enabled", True)
        
        elif from_version == "1.1" and to_version == "1.2":
            # Update configuration structure
            if "dns" in config and "port" in config["dns"]:
                config["dns"]["bind_address"] = config["dns"].get("bind_address", "0.0.0.0")
        
        return config
```

## Testing Updates

### Update Testing Process

1. **Unit Tests**: Run all unit tests
2. **Integration Tests**: Run integration tests
3. **UI Tests**: Test user interface functionality
4. **Performance Tests**: Verify performance impact
5. **Compatibility Tests**: Test backward compatibility
6. **Security Tests**: Verify security implications

### Test Environment

```python
class UpdateTestEnvironment:
    """Test environment for updates"""
    
    def __init__(self):
        self.test_dir = Path("test_updates")
        self.original_dir = Path.cwd()
    
    def setup_test_environment(self, version: str):
        """Setup test environment for specific version"""
        test_env = self.test_dir / f"test_{version}"
        test_env.mkdir(parents=True, exist_ok=True)
        
        # Copy application files
        self._copy_application_files(test_env)
        
        # Setup test database
        self._setup_test_database(test_env)
        
        # Create test configuration
        self._create_test_config(test_env)
        
        return test_env
    
    def test_update(self, from_version: str, to_version: str) -> TestResult:
        """Test update from one version to another"""
        from_env = self.setup_test_environment(from_version)
        
        try:
            # Apply update
            update_result = self._apply_update(from_env, to_version)
            
            # Run tests
            test_results = self._run_tests(from_env)
            
            return TestResult(
                update_success=update_result.success,
                test_results=test_results,
                errors=update_result.errors + test_results.errors
            )
        
        finally:
            # Cleanup
            self._cleanup_test_environment(from_env)
```

### Automated Testing Pipeline

```yaml
# .github/workflows/update-testing.yml
name: Update Testing

on:
  push:
    tags: ['v*']

jobs:
  test-update:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        from-version: ['1.0.0', '1.1.0', '1.2.0']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install Dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Setup Test Environment
      run: |
        python tests/setup_test_env.py --version ${{ matrix.from-version }}
    
    - name: Apply Update
      run: |
        python update.py --install latest --test-mode
    
    - name: Run Tests
      run: |
        pytest tests/ --cov=core --cov=ui --cov-report=xml
    
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.from-version }}
        path: test-results.xml
```

## Release Process

### Pre-Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number updated
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Compatibility testing completed
- [ ] Update packages created
- [ ] Release notes prepared

### Release Steps

1. **Create Release Branch**

   ```bash
   git checkout -b release/v1.2.3
   ```

2. **Update Version**

   ```python
   # Update version.py
   __version__ = "1.2.3"
   ```

3. **Update Changelog**

   ```markdown
   ## [1.2.3] - 2024-01-01
   
   ### Fixed
   - DNS record validation bug
   - Memory leak in query handler
   
   ### Changed
   - Improved query performance
   - Updated dependencies
   ```

4. **Run Tests**

   ```bash
   pytest tests/ --cov=core --cov=ui
   ```

5. **Build Update Packages**

   ```bash
   python build_update.py --version 1.2.3
   ```

6. **Create Git Tag**

   ```bash
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   ```

7. **Create GitHub Release**
   - Upload update packages
   - Add release notes
   - Link to documentation

8. **Deploy Update Server**
   - Upload packages to update server
   - Update update metadata
   - Test update availability

### Post-Release Tasks

- [ ] Monitor update downloads
- [ ] Track user feedback
- [ ] Monitor bug reports
- [ ] Update documentation website
- [ ] Announce release
- [ ] Plan next release

### Release Automation

```python
class ReleaseManager:
    """Manages the release process"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.update_server = "https://updates.tuxxle.org"
    
    def create_release(self, version: str) -> bool:
        """Create a new release"""
        try:
            # Validate version
            if not self._validate_version(version):
                return False
            
            # Run tests
            if not self._run_tests():
                return False
            
            # Build packages
            packages = self._build_packages(version)
            
            # Create GitHub release
            release_id = self._create_github_release(version, packages)
            
            # Deploy to update server
            self._deploy_to_update_server(packages)
            
            # Update documentation
            self._update_documentation(version)
            
            return True
        
        except Exception as e:
            logging.error(f"Release failed: {e}")
            return False
    
    def _validate_version(self, version: str) -> bool:
        """Validate version number"""
        # Check semantic versioning
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            return False
        
        # Check if version already exists
        if self._version_exists(version):
            return False
        
        return True
    
    def _run_tests(self) -> bool:
        """Run all tests"""
        result = subprocess.run(['pytest', 'tests/', '--cov=core', '--cov=ui'])
        return result.returncode == 0
    
    def _build_packages(self, version: str) -> List[str]:
        """Build update packages"""
        packages = []
        
        # Build for different platforms
        platforms = ['windows', 'linux', 'macos']
        
        for platform in platforms:
            package = self._build_platform_package(version, platform)
            packages.append(package)
        
        return packages
```

## Update Security

### Security Considerations

1. **Package Signing**: All update packages must be digitally signed
2. **Signature Verification**: Verify package signatures before installation
3. **Checksum Verification**: Verify file checksums
4. **Secure Download**: Use HTTPS for all downloads
5. **Permission Check**: Verify installation permissions
6. **Sandbox Installation**: Install updates in sandbox environment

### Security Implementation

```python
class UpdateSecurity:
    """Handles update security"""
    
    def __init__(self):
        self.public_key = self._load_public_key()
        self.trusted_sources = [
            "https://updates.tuxxle.org",
            "https://github.com/Nsfr750/tuxxle-dns"
        ]
    
    def verify_package(self, package_path: str, signature_path: str) -> bool:
        """Verify package signature"""
        try:
            # Load signature
            with open(signature_path, 'rb') as f:
                signature = f.read()
            
            # Load package hash
            package_hash = self._calculate_package_hash(package_path)
            
            # Verify signature
            return self._verify_signature(package_hash, signature)
        
        except Exception as e:
            logging.error(f"Package verification failed: {e}")
            return False
    
    def verify_checksums(self, package_path: str, checksums_file: str) -> bool:
        """Verify file checksums"""
        try:
            with open(checksums_file, 'r') as f:
                checksums = f.read()
            
            # Parse checksums
            expected_checksums = self._parse_checksums(checksums)
            
            # Calculate actual checksums
            actual_checksums = self._calculate_checksums(package_path)
            
            # Compare checksums
            return expected_checksums == actual_checksums
        
        except Exception as e:
            logging.error(f"Checksum verification failed: {e}")
            return False
```

## Troubleshooting

### Common Update Issues

#### Update Download Fails

```python
def troubleshoot_download_failure():
    """Troubleshoot update download failures"""
    checks = [
        ("Network connection", check_network_connection),
        ("Update server availability", check_server_availability),
        ("Disk space", check_disk_space),
        ("Write permissions", check_write_permissions),
        ("Firewall settings", check_firewall_settings)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            logging.error(f"Check failed: {check_name}")
            return False
    
    return True
```

#### Update Installation Fails

```python
def troubleshoot_installation_failure():
    """Troubleshoot update installation failures"""
    checks = [
        ("Package integrity", verify_package_integrity),
        ("Backup creation", verify_backup_created),
        ("File permissions", check_file_permissions),
        ("Running processes", check_running_processes),
        ("Database connectivity", check_database_connection)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            logging.error(f"Check failed: {check_name}")
            return False
    
    return True
```

#### Update Verification Fails

```python
def troubleshoot_verification_failure():
    """Troubleshoot update verification failures"""
    checks = [
        ("Package signature", verify_package_signature),
        ("File checksums", verify_file_checksums),
        ("Version compatibility", check_version_compatibility),
        ("System requirements", check_system_requirements)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            logging.error(f"Check failed: {check_name}")
            return False
    
    return True
```

### Debug Mode

```python
class UpdateDebugger:
    """Debug update issues"""
    
    def __init__(self):
        self.debug_log = []
    
    def debug_update_process(self, update_info: UpdateInfo):
        """Debug the entire update process"""
        self._log_step("Starting update debug")
        
        # Check update availability
        self._debug_check_availability(update_info)
        
        # Download update
        self._debug_download(update_info)
        
        # Verify update
        self._debug_verification(update_info)
        
        # Install update
        self._debug_installation(update_info)
        
        self._log_step("Update debug completed")
    
    def _debug_check_availability(self, update_info: UpdateInfo):
        """Debug update availability check"""
        self._log_step("Checking update availability")
        
        # Log system information
        self._log_system_info()
        
        # Log network status
        self._log_network_status()
        
        # Log server response
        self._log_server_response(update_info)
    
    def _debug_download(self, update_info: UpdateInfo):
        """Debug update download"""
        self._log_step("Starting update download")
        
        # Log download progress
        self._log_download_progress(update_info)
        
        # Log file information
        self._log_file_info(update_info)
    
    def _debug_verification(self, update_info: UpdateInfo):
        """Debug update verification"""
        self._log_step("Starting update verification")
        
        # Log signature verification
        self._log_signature_verification(update_info)
        
        # Log checksum verification
        self._log_checksum_verification(update_info)
    
    def _debug_installation(self, update_info: UpdateInfo):
        """Debug update installation"""
        self._log_step("Starting update installation")
        
        # Log backup creation
        self._log_backup_creation(update_info)
        
        # Log file installation
        self._log_file_installation(update_info)
        
        # Log migration process
        self._log_migration_process(update_info)
```

This updating guide provides comprehensive information for managing updates to the DNS Server Manager application, ensuring smooth and secure update processes for all users.
