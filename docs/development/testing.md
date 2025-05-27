# Testing Guide

This guide covers testing practices for Amega AI.

## Test Structure

```
tests/
├── unit/
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   └── test_api.py
└── conftest.py
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/

# Run specific test file
pytest tests/unit/test_models.py
```

## Writing Tests

Example unit test:
```python
def test_model_prediction():
    model = Model()
    result = model.predict("test input")
    assert isinstance(result, str)
    assert len(result) > 0
```

## Test Coverage

- Aim for 80% code coverage minimum
- Write tests for edge cases
- Include both positive and negative test cases

## Integration Tests

```python
async def test_api_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/predict", json={"text": "test"})
        assert response.status_code == 200
```

## Mocking

```python
def test_external_api(mocker):
    mock_response = mocker.patch('requests.get')
    mock_response.return_value.json.return_value = {"result": "success"}
    
    result = call_external_api()
    assert result["result"] == "success"
``` 