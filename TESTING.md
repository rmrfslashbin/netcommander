# Testing Guide

## Overview

The NetCommander project includes comprehensive test coverage:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test with real hardware (optional)
- **Test Coverage**: Measure code coverage and identify gaps

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures and mocks
├── test_client.py               # API client unit tests
├── test_models.py               # Data model tests
├── test_ha_coordinator.py       # Home Assistant coordinator tests
├── test_ha_config_flow.py       # Config flow tests
└── test_integration.py          # Integration tests (require device)
```

## Quick Start

### Install Test Dependencies

```bash
# Using uv
uv pip install -e ".[dev,cli,ha]"

# Or using make
make install-dev
```

### Run All Unit Tests

```bash
# Using pytest directly
pytest -m "not integration"

# Or using make
make test
```

### Run Specific Test Files

```bash
# Test API client only
pytest tests/test_client.py -v

# Test models only
pytest tests/test_models.py -v

# Test Home Assistant components
pytest tests/test_ha_coordinator.py tests/test_ha_config_flow.py -v
```

### Run with Coverage

```bash
# Generate coverage report
make test-cov

# View HTML report
open htmlcov/index.html
```

## Unit Tests

Unit tests mock all external dependencies and test components in isolation.

### API Client Tests (`test_client.py`)

Tests the NetCommanderClient class:
- Client initialization
- Context manager usage
- Status retrieval and parsing
- Device info retrieval and parsing
- Outlet control (on/off/toggle)
- Batch operations (all on/off)
- Error handling (authentication, connection, commands)
- Invalid input validation

**Example:**
```bash
pytest tests/test_client.py::TestNetCommanderClient::test_get_status_success -v
```

### Model Tests (`test_models.py`)

Tests Pydantic data models:
- DeviceStatus creation and properties
- DeviceInfo creation with optional fields
- OutletState enum values
- Property methods (outlets_on, outlets_off)

**Example:**
```bash
pytest tests/test_models.py::TestDeviceStatus -v
```

### Coordinator Tests (`test_ha_coordinator.py`)

Tests the Home Assistant data coordinator:
- Coordinator initialization
- Data update cycle
- Device info caching
- Outlet control methods
- Reboot functionality
- Error handling and UpdateFailed

**Example:**
```bash
pytest tests/test_ha_coordinator.py -v
```

### Config Flow Tests (`test_ha_config_flow.py`)

Tests the Home Assistant config flow:
- Form display
- Successful configuration
- Connection error handling
- Authentication error handling
- Input validation
- Unique ID generation (MAC or IP fallback)

**Example:**
```bash
pytest tests/test_ha_config_flow.py -v
```

## Integration Tests

Integration tests connect to a real device and verify end-to-end functionality.

### Prerequisites

1. **Physical Device**: NetCommander PDU on your network
2. **Environment Variables**:
   ```bash
   export NETCOMMANDER_HOST=192.168.1.100
   export NETCOMMANDER_PASSWORD=admin
   export NETCOMMANDER_USER=admin  # optional, defaults to 'admin'
   export RUN_INTEGRATION_TESTS=1
   ```

### Running Integration Tests

```bash
# Using make (recommended)
make test-integration

# Using pytest directly
RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py -v -s

# Run specific integration test
RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py::TestIntegration::test_get_status -v -s
```

### What Integration Tests Cover

- **Device Info**: Fetch real device information
- **Status Retrieval**: Get current outlet states
- **Outlet Control**: Turn outlets on/off and verify
- **Toggle**: Test toggle functionality
- **Current Monitoring**: Monitor current draw changes
- **Error Handling**: Invalid outlet numbers
- **Session Management**: Multiple calls with same session

**Note:** Integration tests modify outlet states but restore them afterward.

## Test Coverage

### Generate Coverage Report

```bash
# HTML report (recommended)
make test-cov
open htmlcov/index.html

# Terminal report
pytest --cov=src/netcommander --cov=custom_components/netcommander --cov-report=term-missing
```

### Coverage Goals

- **API Client**: >90% coverage
- **Models**: 100% coverage
- **Coordinator**: >85% coverage
- **Config Flow**: >80% coverage

### View Coverage by File

```bash
pytest --cov=src/netcommander --cov-report=term-missing
```

## Test Fixtures

Located in `tests/conftest.py`:

### Available Fixtures

- **`device_info`**: Sample DeviceInfo object
- **`device_status`**: Sample DeviceStatus object
- **`mock_client`**: Mocked NetCommanderClient
- **`mock_response`**: Mocked aiohttp response
- **`mock_session`**: Mocked aiohttp session
- **`connection_params`**: Standard connection parameters
- **`hass`**: Mock Home Assistant instance (HA tests)

### Using Fixtures

```python
def test_example(device_status, mock_client):
    """Test using fixtures."""
    assert device_status.outlets[1] is True
    assert mock_client.host == "192.168.1.100"
```

## Continuous Integration

### GitHub Actions (recommended)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -e ".[dev,cli,ha]"
      - name: Run tests
        run: make test
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Debugging Tests

### Run with Verbose Output

```bash
pytest -v -s tests/test_client.py
```

### Run Single Test

```bash
pytest tests/test_client.py::TestNetCommanderClient::test_get_status_success -v
```

### Drop into Debugger on Failure

```bash
pytest --pdb tests/test_client.py
```

### Print Statements

```bash
# -s flag shows print output
pytest -s tests/test_integration.py
```

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'netcommander'`

**Solution**: Ensure you've installed the package in editable mode:
```bash
uv pip install -e .
```

### Async Test Warnings

**Problem**: `RuntimeWarning: coroutine was never awaited`

**Solution**: Ensure async tests use `@pytest.mark.asyncio` decorator:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is True
```

### Integration Tests Skipped

**Problem**: Integration tests are skipped

**Solution**: Set the required environment variable:
```bash
export RUN_INTEGRATION_TESTS=1
```

## Writing New Tests

### Unit Test Template

```python
"""Tests for new feature."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netcommander import NetCommanderClient


class TestNewFeature:
    """Test new feature."""

    @pytest.mark.asyncio
    async def test_feature_success(self, mock_client):
        """Test successful feature operation."""
        # Arrange
        mock_client.new_method = AsyncMock(return_value=True)

        # Act
        result = await mock_client.new_method()

        # Assert
        assert result is True
        mock_client.new_method.assert_called_once()
```

### Integration Test Template

```python
@pytest.mark.asyncio
async def test_new_feature_integration(self, integration_config):
    """Test new feature with real device."""
    async with NetCommanderClient(**integration_config) as client:
        result = await client.new_method()
        assert result is not None
```

## Best Practices

1. **Test Names**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests clearly
3. **One Assertion**: Focus each test on one behavior
4. **Mock External Calls**: Don't rely on network in unit tests
5. **Clean Up**: Restore state in integration tests
6. **Document**: Add docstrings explaining test purpose

## Make Commands Summary

```bash
make test              # Run unit tests only
make test-unit         # Run specific unit tests
make test-integration  # Run integration tests (requires device)
make test-cov          # Run with coverage report
make lint              # Check code style
make format            # Auto-format code
make type-check        # Run type checking
make clean             # Clean test artifacts
```

## Test Results

After running tests, you'll find:
- **`.coverage`**: Coverage data file
- **`htmlcov/`**: HTML coverage report
- **`.pytest_cache/`**: Pytest cache

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Home Assistant testing](https://developers.home-assistant.io/docs/development_testing/)
