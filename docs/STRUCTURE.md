# DNS Server Manager - Project Structure

This document describes the complete structure of the DNS Server Manager project.

## Directory Structure

```text
tuxxle-dns/
├── README.md                # Project overview and getting started guide
├── CHANGELOG.md             # Version history and changes
├── requirements.txt         # Python dependencies
├── main.py                  # Application entry point
│
├── config/                  # Configuration files
│   ├── config.json          # Default configuration file
│   ├── dsn_records.db       # DNS records database
│   └── dns_server.log       # DNS server log file (generated)
|
├── core/                    # Core DNS server functionality
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── version.py           # Version information
│   ├── database.py          # Database operations and models
│   ├── dns_records.py       # DNS record types and operations
│   └── dns_server.py        # Main DNS server implementation
│
├── ui/                      # User interface components
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── records_widget.py    # DNS records management widget
│   ├── stats_widget.py      # Statistics display widget
│   ├── config_widget.py     # Configuration management widget
│   ├── logs_widget.py       # Log monitoring widget
│   ├── preferences_dialog.py # Preferences configuration dialog
|   ├── about.py             # About dialog
|   ├── help.py              # Help dialog
|   ├── sponsor.py           # Sponsor dialog
|   ├── menu.py              # Menu bar
|   ├── themes.py            # Theme management
│   └── database_widget.py   # Database management widget
│
├── lang/                    # Internationalization (future)
│   ├── __init__.py
│   ├── language_manager.py  # Language management system
│   └── translations.py      # Translation strings
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_dns_server.py   # DNS server tests
│   ├── test_records.py      # DNS records tests
│   ├── test_config.py       # Configuration tests
│   └── test_ui.py           # UI component tests
│
├── docs/                    # Documentation
│   ├── __init__.py
│   ├── API.md               # API documentation
│   ├── BUILDING.md          # Building instructions
│   ├── INSTALLATION.md      # Installation guide
│   ├── ROADMAP.md           # Development roadmap
│   ├── SECURITY.md          # Security information
│   ├── STRUCTURE.md         # This file - project structure
│   ├── STYLE.md             # Code style guidelines
│   ├── TESTING.md           # Testing guidelines
│   ├── TRANSLATIONS.md      # Translations guide
|   ├── UPDATING.md          # Updating guide
│   ├── USER_GUIDE.md        # User guide
│   └── VERSIONING.md        # Versioning guide
│
├── setup/                   # Setup and maintenance scripts
│   ├── clean_pycache.py     # Clean Python cache files
|   └── setup.py             # Package setup and installation
│
└── assets/                  # Static assets (future)
    ├── icons/               # Application icons
    ├── images/              # Images and graphics
    └── themes/              # UI themes
```

## Core Components

### `/core/` - DNS Server Core

#### `config.py`

- Configuration file management
- Settings validation and defaults
- Runtime configuration updates
- Environment variable support

#### `database.py`

- Database connection management
- ORM models for DNS records
- Migration system
- Backup and restore functionality

#### `dns_records.py`

- DNS record type definitions
- Record validation and parsing
- Serialization/deserialization
- Record operations (CRUD)

#### `dns_server.py`

- Main DNS server implementation
- Request handling and routing
- Response generation
- Server lifecycle management

### `/ui/` - User Interface

#### `main_window.py`

- Main application window
- Menu bar and status bar
- Tab management
- Window events and lifecycle

#### `records_widget.py`

- DNS records management interface
- Table view with sorting/filtering
- Add/Edit/Delete operations
- Bulk operations support

#### `stats_widget.py`

- Real-time statistics display
- Charts and graphs
- Performance metrics
- Historical data views

#### `config_widget.py`

- Configuration interface
- Settings forms and validation
- Import/export functionality
- Profile management

#### `logs_widget.py`

- Real-time log monitoring
- Log filtering and search
- Export functionality
- Color-coded log levels

#### `database_widget.py`

- Database management interface
- Table inspection
- Query execution
- Maintenance operations

### `/lang/` - Internationalization

#### `language_manager.py`

- Language detection and switching
- Translation loading
- Locale management
- RTL language support

#### `translations.py`

- Translation strings
- Language packs
- Pluralization rules
- Context-aware translations

## Configuration Files

### `config.json`

Default configuration with sections for:

- DNS server settings (port, bind address, timeout)
- Logging configuration (level, file, rotation)
- UI preferences (theme, layout, window size)
- Database settings (type, connection, backup)

### `requirements.txt`

Python package dependencies:

- PySide6 (GUI framework)
- Database drivers
- Logging utilities
- Testing frameworks

## Application Entry Points

### `main.py`

- Application initialization
- Dependency injection setup
- Error handling and logging
- GUI startup and lifecycle

### `setup.py`

- Package installation
- Dependency management
- Entry point configuration
- Distribution metadata

## Supporting Files

### `version.py`

- Version information and metadata
- Build information
- License and copyright details
- Application constants

### `about.py`, `help.py`, `sponsor.py`

- Dialog implementations
- Static content management
- User guidance and support
- Legal and attribution information

## Development Structure

### `/tests/`

Comprehensive test suite covering:

- Unit tests for core functionality
- Integration tests for components
- UI testing and validation
- Performance benchmarks

### `/docs/`

Complete documentation including:

- API reference
- User guides
- Developer documentation
- Security and deployment guides

### `/setup/`

Maintenance and setup utilities:

- Environment preparation
- Dependency installation
- Cache cleaning
- Development tools

## Data Flow

```text
User Interface (ui/)
    ↓ User ActionsApplication Logic (main.py)
    ↓ Configuration
Core Components (core/)
    ↓ DNS Operations
Network Layer
    ↓ Responses
User Interface (ui/)
```

## Dependencies

### External Dependencies
- **PySide6**: Qt GUI framework
- **Python 3.11+**: Runtime environment
- **Database**: SQLite (default), extensible to others

### Internal Dependencies

- Core components are independent

- UI components depend on core
- Configuration system is central
- Logging is used throughout

## Extension Points

### Plugin System (Future)
- Custom DNS record types
- Authentication modules
- Database backends
- UI themes and components

### API Integration (Future)
- REST API endpoints
- Webhook support
- Third-party integrations
- Monitoring hooks

## Security Considerations

- Input validation at all layers
- Secure configuration storage
- Database connection security
- Network request validation
- User permission management

## Performance Optimizations

- Lazy loading of UI components
- Database connection pooling
- Efficient DNS caching
- Asynchronous operations
- Resource cleanup

## Testing Strategy

- Unit tests for business logic
- Integration tests for workflows
- UI tests for user interactions
- Performance tests for scalability
- Security tests for vulnerabilities

---

This structure is designed to be modular, maintainable, and extensible while following Python best practices and security guidelines.
