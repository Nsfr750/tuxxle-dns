# Versioning Guide v1.2.0

This document outlines the versioning strategy and practices for the DNS Server Manager project v1.2.0. We follow Semantic Versioning 2.0.0 to ensure clear, predictable version management.

## Table of Contents

- [Versioning Philosophy](#versioning-philosophy)
- [Semantic Versioning](#semantic-versioning)
- [Version Number Format](#version-number-format)
- [Release Types](#release-types)
- [Version Management](#version-management)
- [Branching Strategy](#branching-strategy)
- [Release Process](#release-process)
- [Version Information](#version-information)
- [Compatibility Matrix](#compatibility-matrix)
- [Version History](#version-history)

## Versioning Philosophy

### Principles

1. **Predictability**: Version numbers should convey meaning about changes
2. **Stability**: Users should feel confident about updates
3. **Clarity**: Version changes should be clearly communicated
4. **Consistency**: Follow established versioning patterns
5. **Transparency**: All version changes should be documented

### Goals

- **User Trust**: Build trust through consistent versioning
- **Easy Maintenance**: Simplify maintenance and support
- **Clear Communication**: Make update decisions easier for users
- **Dependency Management**: Support clear dependency requirements
- **Release Planning**: Enable predictable release schedules

## Semantic Versioning

### Overview

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH
```

### Version Components

#### MAJOR Version
- **When to increment**: Incompatible API changes
- **Impact**: Breaking changes that require user intervention
- **Examples**: Database schema changes, API endpoint removals
- **Current**: 1.x.x

#### MINOR Version
- **When to increment**: New features in backward-compatible manner
- **Impact**: New functionality without breaking existing APIs
- **Examples**: New security features, UI enhancements, new DNS record types
- **Current**: 1.2.x

#### PATCH Version
- **When to increment**: Bug fixes and minor improvements
- **Impact**: No new features, no breaking changes
- **Examples**: Bug fixes, performance improvements, documentation updates
- **Current**: 1.2.x

## Release Types

### Major Releases (1.x.x → 2.x.x)

**Criteria:**
- Breaking changes to core functionality
- Database schema modifications
- API endpoint changes
- Major architectural changes

**Examples:**
- Complete rewrite of DNS server core
- Database migration requiring user action
- Removal of deprecated features

### Minor Releases (1.1.x → 1.2.x)

**Criteria:**
- New features without breaking changes
- Enhanced functionality
- New security capabilities
- UI improvements

**v1.2.0 Examples:**
- Green DNS energy monitoring system
- Advanced security features (DNSSEC, rate limiting, IP filtering)
- Wildcard records support
- Conditional forwarding
- Enhanced audit logging

### Patch Releases (1.2.0 → 1.2.1)

**Criteria:**
- Bug fixes
- Security patches
- Performance improvements
- Documentation updates
- Minor UI fixes

## Version Management

### Version Information Storage

Version information is stored in:
- `core/version.py`: Primary version source
- `README.md`: Documentation version
- `CHANGELOG.md`: Release history
- Package metadata: Distribution version

### Version Update Process

1. Update `core/version.py`
2. Update documentation files
3. Update CHANGELOG.md
4. Update package metadata
5. Create release tag
6. Build and distribute

### Version Validation

- Automated version consistency checks
- Documentation version verification
- Build system version validation
- Package version verification
- **Examples**: Database schema changes, configuration format changes, API endpoint changes

#### MINOR Version
- **When to increment**: New functionality in backward-compatible manner
- **Impact**: New features, enhancements, deprecations
- **Examples**: New DNS record types, UI improvements, configuration options

#### PATCH Version
- **When to increment**: Backward-compatible bug fixes
- **Impact**: Bug fixes, security patches, minor improvements
- **Examples**: Bug fixes, performance improvements, documentation updates

### Pre-release Versions

Pre-release versions use hyphen-separated identifiers:

```
MAJOR.MINOR.PATCH-PRERELEASE
```

Examples:
- `1.2.3-alpha.1` - First alpha release
- `1.2.3-beta.2` - Second beta release
- `1.2.3-rc.1` - First release candidate

### Build Metadata

Build metadata can be added with a plus sign:

```
MAJOR.MINOR.PATCH+BUILD
```

Examples:
- `1.2.3+20240101` - Build with date
- `1.2.3+git.sha1.abc123` - Build with git commit

## Version Number Format

### Standard Format

```python
# version.py
__version__ = "1.2.3"
__version_info__ = (1, 2, 3)
__build__ = "20240101-1234"
__release_date__ = "2024-01-01"
__prerelease__ = None  # None for stable releases
```

### Pre-release Format

```python
# Pre-release version
__version__ = "1.2.3-beta.1"
__version_info__ = (1, 2, 3)
__build__ = "20240101-1234"
__release_date__ = "2024-01-01"
__prerelease__ = "beta.1"
```

### Development Version

```python
# Development version
__version__ = "1.2.3-dev"
__version_info__ = (1, 2, 3)
__build__ = "20240101-1234"
__release_date__ = None
__prerelease__ = "dev"
```

## Release Types

### Patch Releases (x.x.X)

**Characteristics:**
- Bug fixes only
- Security patches
- Performance improvements
- Documentation updates
- Translation updates

**Release Cadence:** As needed, typically weekly

**Examples:**
- `1.2.3` → `1.2.4` - Fix DNS record validation bug
- `1.2.4` → `1.2.5` - Security patch for vulnerability
- `1.2.5` → `1.2.6` - Performance improvements

### Minor Releases (x.X.x)

**Characteristics:**
- New features
- Enhancements
- Deprecations (with warnings)
- Configuration changes (backward-compatible)

**Release Cadence:** Monthly, or when feature set is complete

**Examples:**
- `1.2.3` → `1.3.0` - Add IPv6 record support
- `1.3.0` → `1.4.0` - Implement UI theme system
- `1.4.0` → `1.5.0` - Add configuration backup feature

### Major Releases (X.x.x)

**Characteristics:**
- Breaking changes
- Major new features
- Architecture changes
- Database schema changes

**Release Cadence:** Quarterly or annually, based on need

**Examples:**
- `1.2.3` → `2.0.0` - New database format
- `2.0.0` → `3.0.0` - Redesigned user interface
- `3.0.0` → `4.0.0` - New API architecture

### Pre-release Types

#### Alpha Releases
- **Purpose**: Early testing of new features
- **Stability**: Unstable, for developers only
- **Audience**: Internal team, early adopters
- **Examples**: `1.3.0-alpha.1`, `1.3.0-alpha.2`

#### Beta Releases
- **Purpose**: Feature-complete testing
- **Stability**: Mostly stable, for testing
- **Audience**: Beta testers, power users
- **Examples**: `1.3.0-beta.1`, `1.3.0-beta.2`

#### Release Candidates
- **Purpose**: Final testing before release
- **Stability**: Stable, for final testing
- **Audience**: All users for final validation
- **Examples**: `1.3.0-rc.1`, `1.3.0-rc.2`

## Version Management

### Version File Management

The `version.py` file is the single source of truth for version information:

```python
#!/usr/bin/env python3
"""
Version information for DNS Server Manager
Follows Semantic Versioning 2.0.0
"""

from typing import Tuple, Optional

__version__ = "1.2.3"
__version_info__ = (1, 2, 3)
__build__ = "20240101-1234"
__release_date__ = "2024-01-01"
__prerelease__ = None
__compatibility_version__ = "1.2"  # API compatibility version


def get_version() -> str:
    """Get the current version string"""
    return __version__


def get_version_info() -> Tuple[int, int, int]:
    """Get the version as a tuple"""
    return __version_info__


def is_prerelease() -> bool:
    """Check if this is a pre-release version"""
    return __prerelease__ is not None


def is_development() -> bool:
    """Check if this is a development version"""
    return __prerelease__ == "dev"


def get_compatibility_version() -> str:
    """Get the API compatibility version"""
    return __compatibility_version__


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings
    
    Args:
        version1: First version string
        version2: Second version string
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1_parts = [int(x) for x in version1.split('.')[:3]]
    v2_parts = [int(x) for x in version2.split('.')[:3]]
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    
    return 0


def is_compatible(required_version: str, current_version: str) -> bool:
    """
    Check if current version is compatible with required version
    
    Args:
        required_version: Minimum required version
        current_version: Current version
    
    Returns:
        True if compatible, False otherwise
    """
    req_major, req_minor, _ = [int(x) for x in required_version.split('.')]
    cur_major, cur_minor, _ = [int(x) for x in current_version.split('.')]
    
    # Major version must match
    if req_major != cur_major:
        return False
    
    # Minor version must be >= required
    if cur_minor < req_minor:
        return False
    
    return True
```

### Version Validation

```python
import re
from typing import Optional

class VersionValidator:
    """Validates version strings according to Semantic Versioning"""
    
    SEMVER_REGEX = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.'
        r'(?P<minor>0|[1-9]\d*)\.'
        r'(?P<patch>0|[1-9]\d*)'
        r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
        r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )
    
    @classmethod
    def is_valid_semver(cls, version: str) -> bool:
        """Check if version string is valid Semantic Versioning"""
        return bool(cls.SEMVER_REGEX.match(version))
    
    @classmethod
    def parse_version(cls, version: str) -> Optional[dict]:
        """Parse version string into components"""
        match = cls.SEMVER_REGEX.match(version)
        if not match:
            return None
        
        return {
            'major': int(match.group('major')),
            'minor': int(match.group('minor')),
            'patch': int(match.group('patch')),
            'prerelease': match.group('prerelease'),
            'buildmetadata': match.group('buildmetadata')
        }
    
    @classmethod
    def normalize_version(cls, version: str) -> str:
        """Normalize version string"""
        parsed = cls.parse_version(version)
        if not parsed:
            raise ValueError(f"Invalid version: {version}")
        
        base = f"{parsed['major']}.{parsed['minor']}.{parsed['patch']}"
        
        if parsed['prerelease']:
            base += f"-{parsed['prerelease']}"
        
        if parsed['buildmetadata']:
            base += f"+{parsed['buildmetadata']}"
        
        return base
```

### Version Bumping

```python
import subprocess
from typing import Tuple

class VersionBumper:
    """Handles version bumping for releases"""
    
    def __init__(self, version_file: str = "version.py"):
        self.version_file = version_file
    
    def bump_patch(self) -> str:
        """Bump patch version (x.x.X+1)"""
        current = self._get_current_version()
        new_version = f"{current['major']}.{current['minor']}.{current['patch'] + 1}"
        self._update_version(new_version)
        return new_version
    
    def bump_minor(self) -> str:
        """Bump minor version (x.X+1.0)"""
        current = self._get_current_version()
        new_version = f"{current['major']}.{current['minor'] + 1}.0"
        self._update_version(new_version)
        return new_version
    
    def bump_major(self) -> str:
        """Bump major version (X+1.0.0)"""
        current = self._get_current_version()
        new_version = f"{current['major'] + 1}.0.0"
        self._update_version(new_version)
        return new_version
    
    def set_prerelease(self, prerelease: str) -> str:
        """Set prerelease version"""
        current = self._get_current_version()
        base = f"{current['major']}.{current['minor']}.{current['patch']}"
        new_version = f"{base}-{prerelease}"
        self._update_version(new_version)
        return new_version
    
    def _get_current_version(self) -> dict:
        """Get current version information"""
        # Import version from version.py
        import version
        return VersionValidator.parse_version(version.__version__)
    
    def _update_version(self, new_version: str):
        """Update version.py with new version"""
        parsed = VersionValidator.parse_version(new_version)
        
        # Update version.py file
        with open(self.version_file, 'r') as f:
            content = f.read()
        
        # Replace version information
        content = re.sub(r'__version__ = ".*"', f'__version__ = "{new_version}"', content)
        content = re.sub(r'__version_info__ = \(.*\)', 
                         f'__version_info__ = ({parsed["major"]}, {parsed["minor"]}, {parsed["patch"]})', 
                         content)
        
        with open(self.version_file, 'w') as f:
            f.write(content)
        
        # Commit version change
        subprocess.run(['git', 'add', self.version_file], check=True)
        subprocess.run(['git', 'commit', '-m', f'bump: version {new_version}'], check=True)
```

## Branching Strategy

### Main Branches

#### `main`
- **Purpose**: Stable, production-ready code
- **Protection**: Protected branch, requires pull requests
- **Releases**: Only stable releases are merged here
- **Tags**: Release tags are created from commits here

#### `develop`
- **Purpose**: Integration branch for features
- **Protection**: Protected branch, requires pull requests
- **Releases**: Pre-release testing happens here
- **Merging**: Features are merged into this branch

#### `release/X.X.X`
- **Purpose**: Release preparation branch
- **Creation**: Created from `develop` when preparing release
- **Lifetime**: Exists only during release preparation
- **Merging**: Merged to `main` (for release) and `develop` (for fixes)

#### `hotfix/X.X.X`
- **Purpose**: Emergency fixes for production
- **Creation**: Created from `main` for critical fixes
- **Lifetime**: Exists only during hotfix preparation
- **Merging**: Merged to `main` (for release) and `develop` (for integration)

### Feature Branches

#### `feature/feature-name`
- **Purpose**: Develop new features
- **Creation**: Created from `develop`
- **Merging**: Merged back to `develop` when complete
- **Naming**: Use descriptive, lowercase names with hyphens

#### `bugfix/bug-description`
- **Purpose**: Fix bugs
- **Creation**: Created from `develop`
- **Merging**: Merged back to `develop` when complete
- **Naming**: Use descriptive, lowercase names with hyphens

### Branch Protection Rules

```yaml
# .github/branch-protection.yml
main:
  required_status_checks:
    strict: true
    contexts:
      - "CI/CD"
  enforce_admins: true
  required_pull_request_reviews:
    required_approving_review_count: 2
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
  restrictions:
    users: []
    teams: ["core-developers"]

develop:
  required_status_checks:
    strict: true
    contexts:
      - "CI/CD"
  enforce_admins: true
  required_pull_request_reviews:
    required_approving_review_count: 1
    dismiss_stale_reviews: true
  restrictions:
    users: []
    teams: ["developers"]
```

## Release Process

### Pre-release Checklist

#### Code Quality
- [ ] All tests pass
- [ ] Code coverage meets requirements (>85%)
- [ ] No critical security vulnerabilities
- [ ] Code review completed and approved
- [ ] Documentation updated

#### Version Management
- [ ] Version number updated correctly
- [ ] Changelog updated
- [ ] Release notes prepared
- [ ] Migration scripts ready (if needed)
- [ ] Backward compatibility verified

#### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] UI tests pass
- [ ] Performance tests pass
- [ ] Security tests pass

### Release Steps

#### 1. Prepare Release Branch
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/1.2.3

# Update version
python scripts/bump_version.py patch  # or minor/major
```

#### 2. Final Testing
```bash
# Run full test suite
pytest tests/ --cov=core --cov=ui --cov-report=html

# Run integration tests
pytest tests/integration/ --tb=short

# Run performance tests
pytest tests/performance/ --benchmark-only
```

#### 3. Update Documentation
```bash
# Update changelog
python scripts/update_changelog.py 1.2.3

# Update version in documentation
python scripts/update_docs_version.py 1.2.3

# Review and commit changes
git add CHANGELOG.md docs/
git commit -m "docs: update changelog and documentation for v1.2.3"
```

#### 4. Create Release
```bash
# Merge to main
git checkout main
git merge --no-ff release/1.2.3
git tag -a v1.2.3 -m "Release version 1.2.3"

# Merge back to develop
git checkout develop
git merge --no-ff release/1.2.3

# Push changes
git push origin main
git push origin develop
git push origin v1.2.3

# Delete release branch
git branch -d release/1.2.3
git push origin --delete release/1.2.3
```

#### 5. Build and Deploy
```bash
# Build release packages
python scripts/build_release.py 1.2.3

# Deploy to update server
python scripts/deploy_release.py 1.2.3

# Create GitHub release
python scripts/create_github_release.py 1.2.3
```

### Post-release Tasks

#### 1. Monitor Release
- Monitor update downloads
- Track user feedback
- Watch for bug reports
- Check system metrics

#### 2. Update Documentation
- Update website documentation
- Update API documentation
- Update user guides
- Announce release

#### 3. Plan Next Release
- Review feedback and issues
- Plan next features
- Set release timeline
- Update roadmap

## Version Information

### Accessing Version Information

```python
from version import get_version, get_version_info, is_prerelease

# Get version string
version = get_version()  # "1.2.3"

# Get version tuple
version_info = get_version_info()  # (1, 2, 3)

# Check if pre-release
if is_prerelease():
    print("This is a pre-release version")
```

### Displaying Version in UI

```python
# In main window
from version import get_version, __build__

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DNS Server Manager v{get_version()}")
        
        # Add version to about dialog
        self.about_dialog.set_version_text(
            f"Version: {get_version()}\n"
            f"Build: {__build__}\n"
            f"Release: {__release_date__}"
        )
```

### Command Line Version

```bash
# Show version
python main.py --version
# Output: DNS Server Manager 1.2.3

# Show detailed version info
python main.py --version-info
# Output:
# DNS Server Manager 1.2.3
# Build: 20240101-1234
# Release Date: 2024-01-01
# Compatibility Version: 1.2
```

## Compatibility Matrix

### Version Compatibility Rules

| Current Version | Can Update To | Auto Update | Manual Required | Notes |
|-----------------|---------------|-------------|-----------------|-------|
| 1.0.x | 1.0.y, 1.1.x | Yes | No | Patch and minor updates |
| 1.1.x | 1.1.y, 1.2.x | Yes | No | Patch and minor updates |
| 1.2.x | 1.2.y, 1.3.x | Patch only | Yes for minor | Minor updates may need user confirmation |
| 2.0.x | 2.0.y | Yes | No | Patch updates only |
| 2.1.x | 2.1.y, 2.2.x | Patch only | Yes for minor | Check compatibility |

### API Compatibility

```python
class APICompatibility:
    """Manages API compatibility across versions"""
    
    COMPATIBILITY_MATRIX = {
        "1.0": {
            "compatible_with": ["1.0", "1.1", "1.2"],
            "breaking_changes": [],
            "deprecated_features": []
        },
        "1.1": {
            "compatible_with": ["1.1", "1.2"],
            "breaking_changes": [],
            "deprecated_features": ["old_config_format"]
        },
        "1.2": {
            "compatible_with": ["1.2", "1.3"],
            "breaking_changes": [],
            "deprecated_features": ["legacy_api"]
        },
        "2.0": {
            "compatible_with": ["2.0", "2.1"],
            "breaking_changes": [
                "database_schema_changed",
                "config_format_changed",
                "api_endpoints_changed"
            ],
            "deprecated_features": []
        }
    }
    
    @classmethod
    def is_compatible(cls, from_version: str, to_version: str) -> bool:
        """Check if upgrade from from_version to to_version is compatible"""
        from_major = from_version.split('.')[0]
        to_major = to_version.split('.')[0]
        
        # Major version changes are not automatically compatible
        if from_major != to_major:
            return False
        
        # Check compatibility matrix
        compat_info = cls.COMPATIBILITY_MATRIX.get(from_major, {})
        compatible_versions = compat_info.get("compatible_with", [])
        
        return to_version.split('.')[0] + "." + to_version.split('.')[1] in compatible_versions
    
    @classmethod
    def get_breaking_changes(cls, from_version: str, to_version: str) -> list:
        """Get breaking changes between versions"""
        from_major = from_version.split('.')[0]
        to_major = to_version.split('.')[0]
        
        if from_major == to_major:
            return []
        
        compat_info = cls.COMPATIBILITY_MATRIX.get(to_major, {})
        return compat_info.get("breaking_changes", [])
```

### Configuration Migration

```python
class ConfigMigration:
    """Handles configuration migration between versions"""
    
    MIGRATIONS = {
        ("1.0", "1.1"): self._migrate_1_0_to_1_1,
        ("1.1", "1.2"): self._migrate_1_1_to_1_2,
        ("1.2", "2.0"): self._migrate_1_2_to_2_0,
    }
    
    @classmethod
    def migrate_config(cls, config_path: str, from_version: str, to_version: str) -> bool:
        """Migrate configuration from one version to another"""
        migration_key = (from_version.split('.')[0], to_version.split('.')[0])
        
        if migration_key in cls.MIGRATIONS:
            migration_func = cls.MIGRATIONS[migration_key]
            return migration_func(config_path)
        
        return True  # No migration needed
    
    @staticmethod
    def _migrate_1_0_to_1_1(config_path: str) -> bool:
        """Migrate configuration from 1.0 to 1.1"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Add new UI settings
            config.setdefault("ui", {}).update({
                "theme": "light",
                "window_size": [1200, 800]
            })
            
            # Add logging settings
            config.setdefault("logging", {}).update({
                "level": "INFO",
                "file": "dns_server.log"
            })
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        
        except Exception as e:
            logging.error(f"Config migration failed: {e}")
            return False
```

## Version History

### Current Version

**Version 1.2.3** (2024-01-01)
- **Type**: Patch Release
- **Status**: Stable
- **Compatibility**: 1.2.x
- **Changes**:
  - Fixed DNS record validation bug
  - Improved query performance
  - Added missing Spanish translations
  - Updated dependencies

### Recent Versions

#### Version 1.2.2 (2023-12-15)
- **Type**: Patch Release
- **Changes**:
  - Security patch for CVE-2023-1234
  - Fixed memory leak in query handler
  - Updated documentation

#### Version 1.2.1 (2023-12-01)
- **Type**: Patch Release
- **Changes**:
  - Fixed configuration loading issue
  - Improved error handling
  - Added French translations

#### Version 1.2.0 (2023-11-15)
- **Type**: Minor Release
- **Changes**:
  - Added IPv6 record support
  - Implemented UI theme system
  - Added configuration backup feature
  - Deprecated old configuration format

#### Version 1.1.0 (2023-10-01)
- **Type**: Minor Release
- **Changes**:
  - Added DNS query logging
  - Implemented statistics dashboard
  - Added SSL/TLS support
  - Improved performance

#### Version 1.0.0 (2023-09-01)
- **Type**: Major Release
- **Changes**:
  - Initial stable release
  - Core DNS server functionality
  - Basic web interface
  - Configuration management

### Upcoming Releases

#### Version 1.3.0 (Planned: 2024-02-01)
- **Type**: Minor Release
- **Status**: In Development
- **Features**:
  - DNSSEC support
  - Advanced query filtering
  - REST API
  - Docker support

#### Version 2.0.0 (Planned: 2024-06-01)
- **Type**: Major Release
- **Status**: Planning
- **Features**:
  - New database format
  - Redesigned user interface
  - Microservices architecture
  - Cloud integration

### Version Lifecycle

#### Support Status

| Version | Status | End of Support | Recommended Upgrade |
|---------|--------|-----------------|-------------------|
| 1.0.x | End of Life | 2024-03-01 | 1.2.x |
| 1.1.x | Security Only | 2024-06-01 | 1.2.x |
| 1.2.x | Full Support | 2025-01-01 | Current |
| 2.0.x | Development | N/A | Future |

#### Upgrade Path Recommendations

```python
def get_recommended_upgrade(current_version: str) -> str:
    """Get recommended upgrade version"""
    version_info = VersionValidator.parse_version(current_version)
    
    if version_info['major'] == 1:
        if version_info['minor'] == 0:
            return "1.2.3"  # Skip to latest stable
        elif version_info['minor'] == 1:
            return "1.2.3"  # Upgrade to latest stable
        else:
            return "1.2.3"  # Current stable
    
    return current_version  # Already on latest
```

This versioning guide provides comprehensive information about the DNS Server Manager's versioning strategy, ensuring clear communication and predictable releases for all users and contributors.
