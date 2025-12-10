# LAS API Documentation

## Overview

The Local Agent System (LAS) provides a comprehensive REST API for AI-powered agent interactions, workflow management, and multi-provider LLM integration.

**Base URL:** `http://localhost:8080/api/v1`

## Quick Start

### 1. Register & Authenticate

```bash
# Register new user
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Login to get access token
curl -X POST "http://localhost:8080/api/v1/auth/login?username=myuser&password=securepass123"

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 2. Make Authenticated Request

```bash
# Use token in Authorization header
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Authentication

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout and invalidate token |
| GET | `/auth/me` | Get current user info |
| PUT | `/auth/me/password` | Change password |

### Roles

- **admin** - Full access to all endpoints
- **user** - Standard access to query and workflow endpoints
- **read-only** - View-only access

## LLM Providers

### Supported Providers

LAS supports 8 LLM providers:

1. **OpenAI** - GPT-4, GPT-3.5
2. **Anthropic (Claude)** - Claude 3.5 Sonnet, Opus
3. **Google (Gemini)** - Gemini Pro, Flash
4. **Groq** - Ultra-fast Llama 3.3
5. **OpenRouter** - Access to 100+ models
6. **HuggingFace** - Open-source models
7. **Ollama** - Local models
8. **DeepSeek** - Affordable models

### Query Endpoint

```bash
POST /api/v1/query
```

```json
{
  "query": "What is machine learning?",
  "provider": "openai",
  "model": "gpt-4-turbo",
  "stream": false
}
```

## HuggingFace Integration

### Chat

```bash
POST /api/v1/hf/chat

{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "model": "meta-llama/Llama-3.3-70B-Instruct"
}
```

### Text Generation

```bash
POST /api/v1/hf/generate

{
  "prompt": "Once upon a time",
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "max_new_tokens": 100
}
```

### Image Generation

```bash
POST /api/v1/hf/text-to-image

{
  "prompt": "A beautiful sunset over mountains",
  "model": "stabilityai/stable-diffusion-3.5-large"
}
```

## Memory & Knowledge Graph

### Get Knowledge Graph

```bash
GET /api/v1/memory/knowledge-graph
```

### List Skills

```bash
GET /api/v1/memory/skills
```

## Performance Monitoring

### Cache Statistics

```bash
GET /api/v1/perf/cache/stats

# Response:
{
  "hits": 1523,
  "misses": 234,
  "hit_rate": 86.7,
  "keys": 145
}
```

### Clear Cache (Admin Only)

```bash
POST /api/v1/perf/cache/clear-stats
Authorization: Bearer ADMIN_TOKEN
```

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Auth (login, register) | 5/minute |
| Query endpoints | 60/minute |
| Default | 100/minute |

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Interactive Documentation

Visit the auto-generated interactive API documentation:

- **Swagger UI**: <http://localhost:8080/docs>
- **ReDoc**: <http://localhost:8080/redoc>
- **OpenAPI JSON**: <http://localhost:8080/openapi.json>

## Client SDKs

Auto-generated client libraries are available:

- **Python**: `sdks/python-client/`
- **TypeScript**: `sdks/typescript-client/`
- **Go**: `sdks/go-client/`

### Python SDK Example

```python
from las_client import LASClient

client = LASClient(base_url="http://localhost:8080")

# Login
client.login("username", "password")

# Query
response = client.query(
    query="What is AI?",
    provider="openai",
    model="gpt-4"
)
print(response)
```

## Support

- **Documentation**: <http://localhost:8080/docs>
- **GitHub**: <https://github.com/your-org/las>
- **Email**: <support@las.local>
