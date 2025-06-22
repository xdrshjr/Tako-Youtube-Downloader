# API Tests

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src/youtube_downloader/api

# Run specific test categories
pytest tests/api/          # API endpoint tests
pytest tests/services/     # Service layer tests
pytest tests/models/       # Model validation tests
```

## Test Structure

- `tests/api/` - FastAPI endpoint tests
- `tests/services/` - Business logic service tests  
- `tests/models/` - Pydantic model validation tests
- `conftest.py` - Test fixtures and configuration

## Using Test Runner

```bash
python run_tests.py --coverage    # Run with coverage report
python run_tests.py --api         # Run only API tests
python run_tests.py --fast        # Skip slow tests
``` 