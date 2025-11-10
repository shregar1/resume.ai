# Resume.AI Test Suite

## Overview
Comprehensive test suite for the Resume.AI application covering:
- Unit tests for all agents
- Service layer tests
- API endpoint tests
- Middleware tests
- Utility function tests
- Integration tests
- Performance tests

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only agent tests
pytest -m agents

# Run only API tests
pytest -m api

# Run fast tests only (exclude slow tests)
pytest -m "not slow"
```

### Run tests with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run tests in parallel (faster)
```bash
pytest -n auto
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── agents/                  # Agent component tests
│   ├── test_parser_agent.py
│   ├── test_jd_analyzer_agent.py
│   ├── test_scoring_agent.py
│   └── test_matching_ranking_orchestrator.py
├── services/                # Service layer tests
│   └── test_api_services.py
├── api/                     # API endpoint tests
│   └── test_endpoints.py
├── utilities/               # Utility function tests
│   └── test_utilities.py
├── middlewares/             # Middleware tests
│   └── test_middlewares.py
├── models/                  # Model tests
│   └── test_models.py
└── integration/             # Integration tests
    └── test_integration.py
```

## Test Markers

- `unit`: Unit tests (fast, isolated)
- `integration`: Integration tests (slower, test component interactions)
- `slow`: Slow-running tests (can be excluded for quick runs)
- `agents`: Tests for agent components
- `services`: Tests for service layer
- `controllers`: Tests for controllers
- `utilities`: Tests for utility functions
- `middlewares`: Tests for middlewares
- `api`: API endpoint tests

## Writing New Tests

### Example test structure:
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.unit
@pytest.mark.agents
class TestMyAgent:
    @pytest.fixture
    def my_agent(self, mock_logger):
        agent = MyAgent(urn="test-urn")
        agent._logger = mock_logger
        return agent
    
    @pytest.mark.asyncio
    async def test_process_success(self, my_agent):
        result = await my_agent.process({"data": "test"})
        assert result["success"] is True
```

## Coverage Goals

Target coverage: > 80% for all modules

Current coverage can be viewed by running:
```bash
pytest --cov=. --cov-report=term-missing
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:
- Fast unit tests run on every commit
- Integration tests run on PRs
- Full test suite runs before deployment

## Troubleshooting

### Tests failing due to missing dependencies
```bash
pip install -r requirements-test.txt
```

### Tests failing due to database
Ensure test database is configured or mocks are properly set up.

### Tests failing due to Redis
Redis connection tests will be skipped if Redis is not available in test environment.

