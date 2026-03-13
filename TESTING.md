# Testing Guide

This guide explains how to set up and run tests for the Krog & Co Calendar integration.

## Prerequisites

- Python 3.11 or later
- PyCharm (or any Python IDE)

## Setup in PyCharm

### 1. Install Dependencies

Install the test dependencies:

```bash
pip install -r requirements_test.txt
```

**Note:** The `krog-company-ics` library is installed directly from GitHub since it's not available on PyPI.

Or if you're using a virtual environment in PyCharm:

1. Go to **File** → **Settings** → **Project** → **Python Interpreter**
2. Click the **+** button to add packages
3. Install these packages:
   - `pytest`
   - `pytest-asyncio`
   - `pytest-homeassistant-custom-component`
   - `freezegun`
4. For `krog-company-ics`, use the terminal:
   ```bash
   pip install git+https://github.com/jonnybergdahl/Python-Krogoco-Ics.git@main
   ```

### 2. Configure PyCharm Test Runner

1. Go to **File** → **Settings** → **Tools** → **Python Integrated Tools**
2. Set **Default test runner** to **pytest**
3. Click **OK**

### 3. Run Tests

#### Run All Tests

Right-click on the `tests` folder and select **Run 'pytest in tests'**

#### Run Individual Test Files

Right-click on any test file (e.g., `test_calendar.py`) and select **Run 'pytest in test_calendar.py'**

#### Run Individual Test Functions

Click the green play button next to any test function

## Command Line Testing

You can also run tests from the command line:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_calendar.py

# Run specific test function
pytest tests/test_calendar.py::test_calendar_entity_attributes

# Run with coverage
pytest --cov=custom_components.krog_company_calendar --cov-report=html
```

## Test Structure

- `tests/conftest.py` - Shared fixtures and mocks
- `tests/test_init.py` - Tests for integration setup/unload
- `tests/test_config_flow.py` - Tests for configuration flow
- `tests/test_coordinator.py` - Tests for data coordinator
- `tests/test_calendar.py` - Tests for calendar entity

## Common Issues

### ModuleNotFoundError

If you see `ModuleNotFoundError: No module named 'krog_company_ics'`:

1. Make sure you've installed the test dependencies: `pip install -r requirements_test.txt`
2. Verify your PyCharm interpreter is using the correct virtual environment

### Import Errors

If you see import errors for `homeassistant`:

1. Make sure `pytest-homeassistant-custom-component` is installed
2. This package provides the necessary Home Assistant test dependencies

### Async Test Warnings

The tests use `pytest-asyncio` for async test support. If you see warnings about async mode, they can be safely ignored as `pytest.ini` is configured with `asyncio_mode = auto`.

## Writing New Tests

When adding new tests:

1. Use the fixtures from `conftest.py`
2. Use `@freeze_time` for time-dependent tests
3. Mock external dependencies (like the `KrogocoIcs` scraper)
4. Follow the existing test patterns for consistency

Example:

```python
from freezegun import freeze_time

@freeze_time("2026-03-14 12:00:00")
async def test_my_feature(calendar_entity):
    """Test my new feature."""
    result = calendar_entity.my_feature()
    assert result == expected_value
```
