# API Reference

Complete reference for all Amega AI API endpoints.

## Authentication

All API requests require authentication using Bearer tokens.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.amega-ai.com/v1/predict
```

## Endpoints

### Prediction

```http
POST /api/v1/predict
```

Request body:
```json
{
    "text": "Your input text here",
    "model": "gpt-3",
    "options": {
        "temperature": 0.7,
        "max_tokens": 100
    }
}
```

Response:
```json
{
    "id": "pred_123",
    "prediction": "Generated text",
    "model": "gpt-3",
    "created_at": "2024-03-21T10:30:00Z"
}
```

### Model Management

```http
GET /api/v1/models
```

Response:
```json
{
    "models": [
        {
            "id": "gpt-3",
            "status": "active",
            "capabilities": ["text-generation", "translation"]
        }
    ]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request |
| 401  | Unauthorized |
| 403  | Forbidden |
| 429  | Rate Limit Exceeded |
| 500  | Server Error | 