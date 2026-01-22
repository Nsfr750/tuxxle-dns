# Code Style Guide

This document outlines the coding standards and conventions for the DNS Server Manager project. All contributors should follow these guidelines to maintain consistency and code quality.

## Table of Contents

- [Python Style](#python-style)
- [Code Organization](#code-organization)
- [Naming Conventions](#naming-conventions)
- [Documentation](#documentation)
- [Type Hints](#type-hints)
- [Error Handling](#error-handling)
- [Testing Style](#testing-style)
- [UI Code Style](#ui-code-style)
- [Git Commit Style](#git-commit-style)

## Python Style

### Code Formatting

We use **Black** for code formatting. All Python code should be formatted with Black before committing.

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Line Length

- Maximum line length: **88 characters** (Black default)
- Use line breaks and parentheses for long statements
- Prefer readable code over compact code

### Imports

- Import standard library modules first
- Import third-party modules second
- Import local application modules third
- Use absolute imports for local modules
- Group imports by type with blank lines between groups

```python
# Standard library
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import pytest
from PySide6.QtWidgets import QWidget, QVBoxLayout

# Local application
from core.config import Config
from core.dns_server import DNSServer
from ui.main_window import MainWindow
```

### String Formatting

- Use f-strings for string formatting (Python 3.6+)
- Use `.format()` for complex formatting
- Avoid `%` formatting except for logging

```python
# Good
name = "example"
result = f"Processing {name} completed"

# Acceptable for complex cases
result = "Processing {name} completed in {time:.2f}s".format(
    name=name, time=elapsed_time
)

# Logging (use % formatting)
logger.info("Processing %s completed", name)
```

## Code Organization

### File Structure

Each module should follow this structure:

```python
#!/usr/bin/env python3
"""
Module docstring - brief description

More detailed description if needed.
"""

# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import pytest
from PySide6.QtWidgets import QWidget

# Local imports
from core.config import Config

# Constants (if any)
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Classes
class ExampleClass:
    """Class docstring"""
    
    def __init__(self):
        """Initialize the class"""
        pass

# Functions
def example_function():
    """Function docstring"""
    pass

# Main execution (if applicable)
if __name__ == "__main__":
    pass
```

### Class Organization

1. Class docstring
2. Class variables and constants
3. `__init__` method
4. Public methods (in logical order)
5. Private methods (prefixed with `_`)
6. Special methods (`__str__`, `__repr__`, etc.)

```python
class DNSServer:
    """
    DNS Server implementation
    
    Provides DNS server functionality with record management,
    query handling, and statistics tracking.
    """
    
    DEFAULT_PORT = 53
    MAX_CONNECTIONS = 1000
    
    def __init__(self, config: Config):
        """Initialize the DNS server"""
        self.config = config
        self.running = False
    
    def start(self) -> bool:
        """Start the DNS server"""
        return self._start_server()
    
    def stop(self) -> bool:
        """Stop the DNS server"""
        return self._stop_server()
    
    def _start_server(self) -> bool:
        """Internal server start logic"""
        pass
    
    def _stop_server(self) -> bool:
        """Internal server stop logic"""
        pass
    
    def __str__(self) -> str:
        """String representation"""
        return f"DNSServer(running={self.running})"
```

## Naming Conventions

### Variables and Functions

- Use **snake_case** for variables and functions
- Use descriptive names that indicate purpose
- Avoid single-letter variables except for loops or mathematical operations

```python
# Good
user_name = "john_doe"
max_connections = 1000
def calculate_response_time():
    pass

# Bad
n = "john_doe"
max_conn = 1000
def calc_rt():
    pass
```

### Classes

- Use **PascalCase** for class names
- Use descriptive names that represent the object's purpose

```python
# Good
class DNSRecordManager:
    pass

class DatabaseConnection:
    pass

# Bad
class dnsrecmgr:
    pass

class dbconn:
    pass
```

### Constants

- Use **UPPER_SNAKE_CASE** for constants
- Define at module level or class level

```python
# Module level
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Class level
class DNSServer:
    DEFAULT_PORT = 53
    BIND_ADDRESS = "0.0.0.0"
```

### Private Members

- Use **single underscore prefix** for protected members
- Use **double underscore prefix** for private members (name mangling)
- Avoid using private members unless necessary

```python
class Example:
    def __init__(self):
        self._protected_var = "protected"
        self.__private_var = "private"
    
    def _protected_method(self):
        """Protected method"""
        pass
    
    def __private_method(self):
        """Private method"""
        pass
```

## Documentation

### Docstrings

All public modules, classes, and functions should have docstrings following the Google style:

```python
def get_dns_record(domain: str, record_type: str) -> Optional[DNSRecord]:
    """
    Retrieve a DNS record for the specified domain and type.
    
    Args:
        domain: The domain name to search for
        record_type: The type of DNS record (A, AAAA, CNAME, etc.)
    
    Returns:
        The DNS record if found, None otherwise
    
    Raises:
        ValueError: If the domain name is invalid
        DatabaseError: If there's an error accessing the database
    
    Example:
        >>> record = get_dns_record("example.com", "A")
        >>> if record:
        ...     print(record.value)
        192.168.1.1
    """
    pass
```

### Comments

- Use comments to explain **why**, not **what**
- Keep comments concise and relevant
- Update comments when code changes
- Avoid obvious comments

```python
# Bad - explains what
x = x + 1  # Increment x by 1

# Good - explains why
x = x + 1  # Account for the header size in the total length
```

### TODO Comments

Use TODO comments for temporary or incomplete code:

```python
# TODO: Implement IPv6 support
# TODO: Add input validation
# TODO: Refactor this method for better performance
```

## Type Hints

### Mandatory Type Hints

All function signatures should include type hints:

```python
from typing import Dict, List, Optional, Union

def process_records(
    records: List[DNSRecord],
    options: Optional[Dict[str, str]] = None
) -> Union[bool, str]:
    """Process DNS records with optional configuration"""
    pass
```

### Complex Types

Use appropriate types for complex data structures:

```python
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass

@dataclass
class ServerConfig:
    """Server configuration data class"""
    host: str
    port: int
    timeout: int
    max_connections: int

def create_server(
    config: ServerConfig,
    callback: Optional[Callable[[str], None]] = None
) -> Tuple[bool, Optional[str]]:
    """Create a server instance"""
    pass
```

### Forward References

Use forward references for circular imports:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dns_server import DNSServer

class RecordManager:
    def __init__(self, server: 'DNSServer'):
        pass
```

## Error Handling

### Exception Hierarchy

Create custom exception classes for better error handling:

```python
class DNSServerError(Exception):
    """Base exception for DNS server errors"""
    pass

class ConfigurationError(DNSServerError):
    """Configuration related errors"""
    pass

class DatabaseError(DNSServerError):
    """Database related errors"""
    pass

class NetworkError(DNSServerError):
    """Network related errors"""
    pass
```

### Exception Handling

- Handle specific exceptions, not bare `except:`
- Use `finally` for cleanup code
- Log exceptions with context

```python
def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {config_file}")
        raise ConfigurationError(f"Config file not found: {config_file}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {config_file}")
        raise ConfigurationError(f"Invalid JSON in config file: {config_file}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        raise
```

## Testing Style

### Test Organization

- Use descriptive test method names
- Group related tests in test classes
- Use fixtures for common setup

```python
class TestDNSRecord:
    """Test cases for DNSRecord class"""
    
    def test_a_record_creation_with_valid_ip(self):
        """Test creating A record with valid IP address"""
        pass
    
    def test_a_record_creation_with_invalid_ip_raises_error(self):
        """Test that creating A record with invalid IP raises ValueError"""
        pass
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_add_record_to_database(self):
    """Test adding a record to the database"""
    # Arrange
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    expected_id = 1
    
    # Act
    result = self.database.add_record(record)
    
    # Assert
    assert result == expected_id
    assert self.database.get_record(expected_id) == record
```

### Mock Usage

Use mocks for external dependencies:

```python
from unittest.mock import Mock, patch

def test_server_start_with_mock_socket(self):
    """Test server start with mocked socket"""
    with patch('socket.socket') as mock_socket:
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        server = DNSServer(self.config)
        server.start()
        
        mock_sock_instance.bind.assert_called_once()
        mock_sock_instance.listen.assert_called_once()
```

## UI Code Style

### Widget Organization

- Separate UI logic from business logic
- Use signals and slots for communication
- Keep UI classes focused on presentation

```python
class RecordsWidget(QWidget):
    """Widget for managing DNS records"""
    
    # Signals
    record_added = Signal(DNSRecord)
    record_deleted = Signal(str)
    
    def __init__(self, dns_server: DNSServer):
        super().__init__()
        self.dns_server = dns_server
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface"""
        pass
    
    def _connect_signals(self):
        """Connect signals and slots"""
        pass
    
    def add_record(self, record: DNSRecord):
        """Add a record (business logic)"""
        if self.dns_server.add_record(record):
            self.record_added.emit(record)
            self._refresh_table()
```

### Signal and Slot Naming

- Use descriptive signal names
- Use past tense for completed actions
- Use present tense for ongoing actions

```python
# Good
record_added = Signal(DNSRecord)
server_started = Signal()
query_received = Signal(str)

# Bad
add_record = Signal(DNSRecord)
start_server = Signal()
receive_query = Signal(str)
```

## Git Commit Style

### Commit Message Format

Follow the Conventional Commits specification:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```text
feat(dns): add IPv6 record support

Add support for AAAA records in the DNS server.
Includes validation for IPv6 addresses and proper
record formatting in responses.

Closes #123
```

```text
fix(config): handle missing config file gracefully

Add proper error handling when config file doesn't exist.
Fallback to default configuration instead of crashing.
```

```text
docs(api): update DNSRecord documentation

Improve docstrings for DNSRecord class with better
examples and type hints.
```

## Code Review Guidelines

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All functions have proper docstrings
- [ ] Type hints are present and correct
- [ ] Error handling is appropriate
- [ ] Tests are included for new functionality
- [ ] No hardcoded values (use constants)
- [ ] No commented-out code
- [ ] Security considerations are addressed
- [ ] Performance implications are considered

### Review Process

1. Create pull request with descriptive title
2. Reference relevant issues
3. Ensure all tests pass
4. Request review from at least one team member
5. Address feedback promptly
6. Keep discussion focused and constructive

## Tools and Automation

### Pre-commit Hooks

Configure pre-commit hooks to enforce style:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

### IDE Configuration

Configure your IDE to follow these guidelines:

- Set line length to 88 characters
- Enable Black formatting on save
- Configure type checking with mypy
- Set up linting with flake8

## Resources

- [Black Code Formatter](https://black.readthedocs.io/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
