# LAS Testing Guide

This directory contains comprehensive tests for the Local Agent System (LAS).

## Test Structure

```
tests/
├── test_llm_service.py      # LLM Service & Caching tests
├── test_memory_service.py   # Memory System tests (4-Tier)
├── test_rag_service.py      # RAG Service tests
├── test_tool_service.py     # Tool Service & MCP Client tests
├── test_agents.py           # Agent tests (Supervisor, Planner, Coder)
├── test_api_routers.py      # API Router & Security tests
├── test_integration.py      # Integration & E2E tests
├── e2e_test.py             # Simple E2E test script
└── README_TESTING.md       # This file
```

## Test Categories

### Unit Tests
Test individual components in isolation:
- **Services**: LLM, Memory, RAG, Tools
- **Agents**: Supervisor, Planner, Coder
- **Routers**: Query, Stream
- **Utilities**: Cache, Security

### Integration Tests
Test component interactions:
- Database connections (PostgreSQL, Qdrant)
- Service-to-service communication
- Agent collaboration

### End-to-End Tests
Test complete workflows:
- Full query processing
- Multi-agent tasks
- Streaming responses

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run All Unit Tests
```bash
pytest -m unit
```

### Run All Tests (Excluding Integration/E2E)
```bash
pytest -m "not integration and not e2e"
```

### Run Specific Test File
```bash
pytest tests/test_llm_service.py -v
```

### Run Integration Tests (Requires Running Services)
```bash
# Start services first
docker-compose up -d

# Run integration tests
pytest -m integration
```

### Run E2E Tests (Requires Full System)
```bash
# Start all services
docker-compose up -d

# Run E2E tests
pytest -m e2e

# Or use the simple E2E script
python tests/e2e_test.py
```

### Run with Coverage Report
```bash
pytest --cov=services --cov=agents --cov=routers --cov-report=html
```

View coverage report: `open htmlcov/index.html`

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.slow` - Long-running tests

## Environment Configuration

Tests use environment variables:

- `LAS_API_URL`: API base URL (default: `http://localhost:8000`)
- `LAS_API_KEY`: API key for authentication (default: `las-secret-key`)

Set in `.env` or export before running:
```bash
export LAS_API_KEY="my-secret-key"
pytest
```

## Writing New Tests

### Unit Test Template
```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    @pytest.fixture
    def component(self):
        return MyComponent()
    
    def test_basic_functionality(self, component):
        result = component.do_something()
        assert result == expected_value
```

### Async Test Template
```python
import pytest

class TestAsyncComponent:
    @pytest.mark.asyncio
    async def test_async_operation(self):
        result = await async_function()
        assert result is not None
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
pip install -r requirements.txt -r requirements-test.txt

# Run unit tests only (fast)
pytest -m "not integration and not e2e" --tb=short

# Run with coverage
pytest --cov=services --cov=agents --cov-report=xml
```

## Troubleshooting

### Tests Fail with "Connection Refused"
- Ensure Docker services are running: `docker-compose up -d`
- Check service health: `docker-compose ps`

### Import Errors
- Install test dependencies: `pip install -r requirements-test.txt`
- Ensure you're in the correct directory: `cd las_core`

### Async Tests Fail
- Install pytest-asyncio: `pip install pytest-asyncio`
- Check pytest.ini has `asyncio_mode = auto`

## Test Coverage Goals

- **Services**: >80% coverage
- **Agents**: >70% coverage
- **Routers**: >90% coverage
- **Overall**: >75% coverage

## Performance Benchmarks

Run performance tests:
```bash
pytest -m performance -v
```

Expected benchmarks:
- Cache hit: <1ms
- API response: <100ms
- Query processing: <5s

---

For questions or issues, refer to the main project documentation.
