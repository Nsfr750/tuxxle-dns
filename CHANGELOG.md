# Changelog

All notable changes to DNS Server Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial menu system with File, Edit, Tools, and Help menus
- About dialog with application information
- Help dialog with comprehensive user guide
- Sponsor dialog with support information
- Version information dialog
- Clear logs functionality
- Export configuration placeholder
- Preferences placeholder

### Changed
- Updated PySide6 from version 6.6.0 to 6.10.1 for compatibility

## [1.0.0] - 2024-01-21

### Added
- Initial release of DNS Server Manager
- DNS server core functionality
- Graphical user interface with PySide6
- DNS records management (A, AAAA, CNAME, MX, TXT, NS)
- Real-time statistics monitoring
- Configuration management
- Log monitoring and display
- Database management interface
- Server start/stop controls
- Tab-based interface organization
- Status bar with real-time updates
- Header widget with server controls

### Features
- DNS server with configurable port and bind address
- Support for multiple DNS record types
- Real-time query statistics
- Configurable logging system
- Database integration for record storage
- Modern Qt-based GUI
- Responsive design with minimum size constraints
- Auto-refresh functionality for statistics
- Log file monitoring with color-coded levels
- Configuration persistence

### Technical Details
- Python 3.11+ compatibility
- PySide6 GUI framework
- Modular architecture with separate UI, core, and utility modules
- Thread-safe log monitoring
- Event-driven architecture
- Exception handling and error reporting
- Clean shutdown procedures

---

## Version History

### Development Phase
- Project initialization and structure setup
- Core DNS server implementation
- UI framework selection and integration
- Database schema design
- Configuration system implementation
- Testing and debugging

### Future Plans
- Enhanced security features
- Advanced filtering and search capabilities
- Import/export functionality
- Plugin system support
- Multi-language support
- Performance optimizations
- Advanced monitoring and alerting

---

## Support

For bug reports, feature requests, or support:
- Email: info@tuxxle.org
- Website: https://www.tuxxle.org
- GitHub: https://github.com/Nsfr750

## License

This project is licensed under the GPLv3 License - see the LICENSE file for details.

## Copyright

© Copyright 2024-2026 Nsfr750 - All rights reserved.
