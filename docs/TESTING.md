# Testing Guide

This document provides comprehensive guidelines for testing the DNS Server Manager project. It covers testing strategies, tools, and best practices to ensure code quality and reliability.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Testing Tools](#testing-tools)
- [Test Structure](#test-structure)
- [Types of Tests](#types-of-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Mocking and Fixtures](#mocking-and-fixtures)
- [Running Tests](#running-tests)
- [Continuous Integration](#continuous-integration)
- [Debugging Tests](#debugging-tests)

## Testing Philosophy

### Principles

1. **Test Early, Test Often**: Write tests alongside code, not after
2. **Comprehensive Coverage**: Test all public interfaces and edge cases
3. **Isolation**: Tests should be independent and not affect each other
4. **Clarity**: Tests should be easy to read and understand
5. **Maintainability**: Tests should be easy to maintain and update

### Test Pyramid

```
    E2E Tests (Few)
   ─────────────────
   Integration Tests (Some)
  ─────────────────────────
 Unit Tests (Many)
─────────────────────────
```

- **Unit Tests**: 70-80% - Test individual components in isolation
- **Integration Tests**: 15-20% - Test component interactions
- **End-to-End Tests**: 5-10% - Test complete user workflows

## Testing Tools

### Core Testing Framework

We use **pytest** as our primary testing framework:

```bash
# Install pytest
pip install pytest

# Install with additional plugins
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Essential Plugins

- **pytest-cov**: Coverage reporting
- **pytest-mock**: Enhanced mocking capabilities
- **pytest-asyncio**: Async test support
- **pytest-xdist**: Parallel test execution
- **pytest-html**: HTML test reports

### Configuration

Create `pytest.ini` in project root:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=core
    --cov=ui
    --cov=lang
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    network: Tests requiring network access
```

## Test Structure

### Directory Layout

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── test_config.py
│   ├── test_dns_records.py
│   ├── test_dns_server.py
│   └── test_language_manager.py
├── integration/                # Integration tests
│   ├── test_database_integration.py
│   ├── test_server_integration.py
│   └── test_ui_integration.py
├── e2e/                       # End-to-end tests
│   ├── test_user_workflows.py
│   └── test_server_scenarios.py
├── fixtures/                  # Test data and fixtures
│   ├── sample_configs.json
│   ├── sample_records.json
│   └── mock_servers.py
└── helpers/                   # Test utilities
    ├── test_helpers.py
    └── assertion_helpers.py
```

### Test File Organization

Each test file should focus on a specific module or component:

```python
#!/usr/bin/env python3
"""
Tests for DNS Server functionality
"""

import pytest
from unittest.mock import Mock, patch

from core.dns_server import DNSServer
from core.config import Config

class TestDNSServer:
    """Test cases for DNSServer class"""
    
    def test_server_initialization(self):
        """Test DNS server initialization"""
        pass
    
    def test_start_server(self):
        """Test starting the DNS server"""
        pass
```

## Types of Tests

### Unit Tests

Unit tests test individual components in isolation:

```python
def test_dns_record_validation():
    """Test DNS record IP address validation"""
    # Valid IPv4
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    assert record.is_valid()
    
    # Invalid IPv4
    record = DNSRecord("example.com", DNSRecordType.A, "256.256.256.256", 300)
    assert not record.is_valid()
```

### Integration Tests

Integration tests test component interactions:

```python
def test_server_database_integration():
    """Test DNS server integration with database"""
    # Setup
    config = Config()
    server = DNSServer(config)
    
    # Test
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    result = server.add_record(record)
    
    # Verify
    assert result is True
    retrieved = server.query_record("example.com", DNSRecordType.A)
    assert retrieved is not None
```

### End-to-End Tests

E2E tests test complete user workflows:

```python
def test_complete_dns_resolution_workflow():
    """Test complete DNS resolution workflow"""
    # Setup server
    config = Config()
    server = DNSServer(config)
    server.start()
    
    try:
        # Add record
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        server.add_record(record)
        
        # Query record
        response = server.query_record("example.com", DNSRecordType.A)
        
        # Verify
        assert response is not None
        assert len(response.records) == 1
        assert response.records[0].value == "192.168.1.1"
    finally:
        server.stop()
```

## Writing Tests

### Test Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_a_record_creation_with_valid_ipv4_address():
    pass

def test_server_start_fails_when_port_already_in_use():
    pass

# Bad
def test_record():
    pass

def test_server():
    pass
```

### Test Structure

Follow the Arrange-Act-Assert (AAA) pattern:

```python
def test_add_record_to_database():
    """Test adding a record to the database"""
    # Arrange
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    database = MockDatabase()
    expected_id = 1
    
    # Act
    result = database.add_record(record)
    
    # Assert
    assert result == expected_id
    assert database.contains_record(expected_id)
```

### Test Data

Use realistic test data:

```python
@pytest.fixture
def sample_dns_records():
    """Provide sample DNS records for testing"""
    return [
        DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300),
        DNSRecord("example.com", DNSRecordType.AAAA, "2001:db8::1", 300),
        DNSRecord("mail.example.com", DNSRecordType.MX, "10 mail.example.com", 300),
    ]
```

### Assertions

Use specific assertions with clear messages:

```python
# Good
assert response.response_code == 0, f"Expected NOERROR, got {response.response_code}"
assert len(records) == 3, f"Expected 3 records, got {len(records)}"

# Bad
assert response.response_code == 0
assert len(records) == 3
```

## Test Coverage

### Coverage Goals

- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ line coverage
- **Overall**: 85%+ line coverage

### Coverage Reports

Generate coverage reports:

```bash
# HTML report
pytest --cov=core --cov-report=html

# Terminal report
pytest --cov=core --cov-report=term-missing

# Combined report
pytest --cov=core --cov=ui --cov-report=html --cov-report=term-missing
```

### Coverage Exclusions

Exclude appropriate code from coverage:

```python
# .coveragerc
[run]
omit = 
    */tests/*
    */venv/*
    setup.py
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Mocking and Fixtures

### Fixtures

Use fixtures for common test setup:

```python
# conftest.py
@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file"""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "dns": {"port": 5353, "bind_address": "127.0.0.1"},
        "logging": {"level": "DEBUG"}
    }
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    return config_file

@pytest.fixture
def mock_dns_server():
    """Create a mock DNS server"""
    server = Mock()
    server.is_running.return_value = False
    server.start.return_value = True
    server.stop.return_value = True
    return server
```

### Mocking

Use mocks for external dependencies:

```python
def test_server_start_with_mock_socket():
    """Test server start with mocked socket"""
    with patch('socket.socket') as mock_socket:
        mock_sock_instance = Mock()
        mock_socket.return_value = mock_sock_instance
        
        server = DNSServer(config)
        result = server.start()
        
        assert result is True
        mock_sock_instance.bind.assert_called_once()
        mock_sock_instance.listen.assert_called_once()
```

### Database Mocking

Mock database operations for unit tests:

```python
@pytest.fixture
def mock_database():
    """Create a mock database"""
    db = Mock(spec=DNSSQLiteDatabase)
    db.list_records.return_value = []
    db.add_record.return_value = True
    db.delete_record.return_value = True
    return db

def test_add_record_with_mock_database(mock_database):
    """Test adding record with mocked database"""
    with patch('core.dns_server.DNSSQLiteDatabase', return_value=mock_database):
        server = DNSServer(config)
        record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
        
        result = server.add_record(record)
        
        assert result is True
        mock_database.add_record.assert_called_once_with(record)
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_dns_server.py

# Run specific test class
pytest tests/test_dns_server.py::TestDNSServer

# Run specific test method
pytest tests/test_dns_server.py::TestDNSServer::test_start_server

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=core
```

### Running by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run network-dependent tests
pytest -m network
```

### Parallel Execution

```bash
# Run tests in parallel
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Continuous Testing

```bash
# Watch for changes and re-run tests
pytest-watch

# Alternative with pytest-xdist
pytest -f --looponfail
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
    
    - name: Run tests
      run: |
        pytest --cov=core --cov=ui --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Quality Gates

Set quality gates in your CI pipeline:

- **Minimum Coverage**: 85%
- **All Tests Pass**: 100%
- **No Linting Errors**: 0
- **Security Scan**: Pass

## Debugging Tests

### Debugging Failed Tests

```bash
# Run with pdb on failure
pytest --pdb

# Run specific test with pdb
pytest tests/test_dns_server.py::TestDNSServer::test_start_server --pdb

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Test Logging

Enable logging in tests:

```python
import logging

def test_with_logging(caplog):
    """Test with logging capture"""
    with caplog.at_level(logging.DEBUG):
        server = DNSServer(config)
        server.start()
    
    # Check log messages
    assert "Server started" in caplog.text
```

### Print Debugging

Use print statements for quick debugging:

```python
def test_debug_example():
    """Debug example with print statements"""
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    print(f"Record: {record}")
    print(f"Valid: {record.is_valid()}")
    assert record.is_valid()
```

### Test Isolation

Ensure tests don't interfere with each other:

```python
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test"""
    yield
    # Cleanup code here
    temp_files = glob.glob("temp_*.json")
    for file in temp_files:
        os.remove(file)
```

## Performance Testing

### Benchmarking

Use pytest-bench for performance tests:

```python
def test_dns_query_performance(benchmark):
    """Benchmark DNS query performance"""
    server = DNSServer(config)
    record = DNSRecord("example.com", DNSRecordType.A, "192.168.1.1", 300)
    server.add_record(record)
    
    result = benchmark(server.query_record, "example.com", DNSRecordType.A)
    assert result is not None
```

### Load Testing

For load testing, use dedicated tools:

```python
def test_concurrent_queries():
    """Test handling concurrent queries"""
    import concurrent.futures
    
    server = DNSServer(config)
    server.start()
    
    def query_domain():
        return server.query_record("example.com", DNSRecordType.A)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(query_domain) for _ in range(100)]
        results = [f.result() for f in futures]
    
    assert all(r is not None for r in results)
```

## Best Practices

### General Guidelines

1. **Test One Thing**: Each test should verify one specific behavior
2. **Use Descriptive Names**: Test names should explain what they test
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Execution**: Unit tests should be fast (< 100ms)

### Common Pitfalls

1. **Testing Implementation**: Test behavior, not implementation details
2. **Over-Mocking**: Only mock external dependencies
3. **Brittle Tests**: Avoid tests that break with minor changes
4. **Missing Edge Cases**: Test error conditions and edge cases
5. **No Cleanup**: Clean up resources after tests

### Code Review Checklist

- [ ] Test follows naming conventions
- [ ] Test is isolated and independent
- [ ] Test has clear arrange-act-assert structure
- [ ] Assertions are specific and meaningful
- [ ] Test covers both success and failure cases
- [ ] Test data is realistic and appropriate
- [ ] Mocks are used correctly
- [ ] Test is fast and efficient

## Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Test Coverage Documentation](https://coverage.readthedocs.io/)

### Books and Articles

- "Test-Driven Development with Python" by Harry Percival
- "Effective Testing with RSpec, Minitest, and Capybara" (concepts applicable)
- "The Art of Unit Testing" by Roy Osherove

### Tools and Libraries

- [pytest](https://pytest.org/) - Testing framework
- [pytest-mock](https://github.com/pytest-dev/pytest-mock) - Mocking support
- [pytest-cov](https://github.com/pytest-dev/pytest-cov) - Coverage reporting
- [factory_boy](https://factoryboy.readthedocs.io/) - Test data factories
- [hypothesis](https://hypothesis.works/) - Property-based testing
