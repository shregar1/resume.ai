# Testing Guide for CalCount

This directory contains all the tests for the CalCount project. We use pytest as our testing framework.

## Setup

### 1. Install Dependencies

First, install the testing dependencies:

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

The test environment is automatically configured by the test runner. However, you can set custom test environment variables:

```bash
export TEST_DATABASE_URL="sqlite:///:memory:"
export BCRYPT_SALT="test_salt_for_testing_only"
export JWT_SECRET_KEY="test_jwt_secret_key_for_testing_only"
```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner:

```bash
python run_tests.py
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/services/user/test_login.py

# Run specific test class
pytest tests/services/user/test_login.py::TestUserLoginService

# Run specific test method
pytest tests/services/user/test_login.py::TestUserLoginService::test_successful_login

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests excluding slow tests
pytest -m "not slow"
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── services/                # Service layer tests
│   └── user/
│       ├── test_login.py
│       ├── test_logout.py
│       └── test_register.py
├── controllers/             # Controller layer tests (future)
├── repositories/            # Repository layer tests (future)
└── integration/             # Integration tests (future)
```

## Writing Tests

### Test File Naming

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Example Test Structure

```python
import pytest
from unittest.mock import Mock

@pytest.mark.asyncio
class TestMyService:
    @pytest.fixture(autouse=True)
    def setup(self, db_session):
        """Setup runs before each test method"""
        self.service = MyService()
        self.service.repository.session = db_session

    async def test_successful_operation(self):
        # Arrange
        expected_result = {"status": "SUCCESS"}
        
        # Act
        result = await self.service.run()
        
        # Assert
        assert result == expected_result

    async def test_error_handling(self):
        # Arrange
        self.service.repository.some_method = Mock(side_effect=Exception("Error"))
        
        # Act & Assert
        with pytest.raises(Exception):
            await self.service.run()
```

### Using Fixtures

The `conftest.py` file provides several useful fixtures:

- `db_session`: Database session for tests
- `mock_user`: Mock user object
- `mock_meal_log`: Mock meal log object
- `mock_user_repository`: Mock user repository
- `mock_meal_log_repository`: Mock meal log repository
- `mock_jwt_utility`: Mock JWT utility
- `sample_login_data`: Sample login data
- `sample_registration_data`: Sample registration data
- `sample_meal_data`: Sample meal data

### Async Tests

For async tests, use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Test Categories

### Unit Tests

Unit tests test individual components in isolation. Use mocks for dependencies.

```python
@pytest.mark.unit
async def test_unit_test():
    # Test individual component
    pass
```

### Integration Tests

Integration tests test how components work together.

```python
@pytest.mark.integration
async def test_integration_test():
    # Test component interaction
    pass
```

### Slow Tests

Mark tests that take longer to run:

```python
@pytest.mark.slow
async def test_slow_test():
    # Test that takes time
    pass
```

## Coverage

The project is configured to require at least 80% code coverage. Coverage reports are generated in:

- Terminal output: `--cov-report=term-missing`
- HTML report: `htmlcov/index.html`
- XML report: `coverage.xml`

## Best Practices

1. **Arrange-Act-Assert**: Structure tests with clear sections
2. **Descriptive Names**: Use descriptive test and method names
3. **One Assertion**: Each test should test one thing
4. **Use Fixtures**: Reuse common setup code
5. **Mock Dependencies**: Mock external dependencies in unit tests
6. **Test Edge Cases**: Include error conditions and edge cases
7. **Keep Tests Fast**: Tests should run quickly
8. **Clean Up**: Always clean up after tests

## Debugging Tests

To debug a failing test:

```bash
# Run with more verbose output
pytest -vvv

# Run with print statements visible
pytest -s

# Run specific test with debugger
pytest tests/path/to/test.py::TestClass::test_method -s

# Run with pdb on failures
pytest --pdb
```

## Continuous Integration

Tests are automatically run in CI/CD pipelines. The pipeline will:

1. Install dependencies
2. Run all tests
3. Generate coverage reports
4. Fail if coverage is below 80%
5. Fail if any tests fail 