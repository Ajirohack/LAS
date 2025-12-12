# LiteLLM Integration Guide

This document describes the LiteLLM integration in LAS, providing unified access to **100+ LLM providers** through a single, lightweight interface.

## Overview

LiteLLM is integrated as:
1. **LiteLLM Service** (`services/litellm_service.py`) - Core service with unified API
2. **LiteLLM Provider** (`sources/providers/litellm_provider.py`) - Provider factory integration
3. **LiteLLM Router** (`routers/litellm_router.py`) - REST API endpoints
4. **Frontend Component** (`components/settings/LiteLLMSettings.tsx`) - UI for configuration

## Supported Providers

| Provider | Model Format | Features | API Key Required |
|----------|-------------|----------|------------------|
| **Ollama** | `ollama/llama3.2` | Local, Embeddings | No |
| **OpenAI** | `openai/gpt-4o` | Vision, Tools, TTS, STT | Yes |
| **Anthropic** | `anthropic/claude-3-5-sonnet-20241022` | Vision, Tools | Yes |
| **Gemini** | `gemini/gemini-2.0-flash-exp` | Vision, Tools, 1M+ context | Yes |
| **Groq** | `groq/llama-3.3-70b-versatile` | Fast inference, Tools | Yes |
| **OpenRouter** | `openrouter/anthropic/claude-3.5-sonnet` | Multi-provider | Yes |
| **HuggingFace** | `huggingface/meta-llama/Llama-3.2-3B-Instruct` | Many models | Yes |
| **Together AI** | `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo` | Fast, Tools | Yes |
| **DeepSeek** | `deepseek/deepseek-chat` | Code, Reasoning | Yes |
| **Azure OpenAI** | `azure/gpt-4` | Enterprise | Yes |
| **AWS Bedrock** | `bedrock/anthropic.claude-3-sonnet` | Enterprise | Yes |
| **vLLM** | `vllm/model-name` | Self-hosted | No |

## Quick Start

### 1. Install LiteLLM

```bash
pip install litellm>=1.40.0
```

### 2. Configure API Keys

Copy `.env.litellm.example` to `.env` and fill in your API keys:

```bash
# For cloud providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# For local providers (Ollama - no key needed)
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Start the API

```bash
cd las_core
python -m uvicorn api:app --host 0.0.0.0 --port 7777 --reload
```

## API Endpoints

### Chat Completions

**POST** `/api/v1/litellm/chat/completions`

```json
{
  "model": "ollama/llama3.2",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 4096
}
```

**Streaming Response:**
```json
{
  "model": "ollama/llama3.2",
  "messages": [{"role": "user", "content": "Tell me a story"}],
  "stream": true
}
```

### OpenAI-Compatible Proxy

Use LAS as a drop-in OpenAI replacement:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7777/api/v1/litellm/v1",
    api_key="any"  # Not validated locally
)

response = client.chat.completions.create(
    model="ollama/llama3.2",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### List Models

**GET** `/api/v1/litellm/models?provider=ollama`

### List Providers

**GET** `/api/v1/litellm/providers`

### Vision (Image Analysis)

**POST** `/api/v1/litellm/vision`

```json
{
  "prompt": "What's in this image?",
  "image_url": "https://example.com/image.jpg",
  "model": "openai/gpt-4o"
}
```

### Embeddings

**POST** `/api/v1/litellm/embeddings`

```json
{
  "input": "Hello world",
  "model": "text-embedding-3-small",
  "provider": "openai"
}
```

### Cost Estimation

**POST** `/api/v1/litellm/cost/estimate`

```json
{
  "model": "openai/gpt-4o",
  "input_tokens": 1000,
  "output_tokens": 500
}
```

## Python SDK Usage

### Basic Completion

```python
from services.litellm_service import get_litellm_service

svc = get_litellm_service()

# Sync completion
response = svc.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama3.2",
    provider="ollama"
)
print(response.choices[0].message.content)

# Async completion
response = await svc.achat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o",
    provider="openai"
)
```

### Streaming

```python
response = svc.chat_completion(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="llama3.2",
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

### Function Calling / Tool Use

```python
from services.litellm_service import ToolDefinition

# Define tools
tools = [
    ToolDefinition(
        name="get_weather",
        description="Get current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    )
]

# Tool handlers
def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 72°F"

# Chat with automatic tool execution
result = svc.chat_with_tools(
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_handlers={"get_weather": get_weather},
    model="gpt-4o",
    provider="openai"
)

print(result["response"])
# Output: "The weather in Tokyo is currently sunny with a temperature of 72°F."
```

### Vision

```python
response = svc.vision_completion(
    prompt="Describe this image in detail",
    image_url="https://example.com/cat.jpg",
    model="gpt-4o",
    provider="openai"
)
```

### Embeddings

```python
response = svc.create_embedding(
    input=["Hello world", "Goodbye world"],
    model="text-embedding-3-small",
    provider="openai"
)

embeddings = [item.embedding for item in response.data]
```

## Provider Factory Integration

Use LiteLLM through the existing provider system:

```python
from sources.provider_factory import ProviderFactory

# Create LiteLLM provider
provider = ProviderFactory.create(
    provider_name="litellm",
    model="openai/gpt-4o"  # Provider prefix in model name
)

# Use like any other provider
response = provider.chat_completion([
    {"role": "user", "content": "Hello!"}
])

# Or with Ollama
provider = ProviderFactory.create(
    provider_name="litellm",
    model="ollama/llama3.2"
)
```

## Model Name Formats

LiteLLM uses `provider/model` format:

| Provider | Format | Example |
|----------|--------|---------|
| OpenAI | `openai/model` | `openai/gpt-4o` |
| Anthropic | `anthropic/model` | `anthropic/claude-3-5-sonnet-20241022` |
| Gemini | `gemini/model` | `gemini/gemini-1.5-pro` |
| Ollama | `ollama/model` | `ollama/llama3.2` |
| Groq | `groq/model` | `groq/llama-3.3-70b-versatile` |
| OpenRouter | `openrouter/org/model` | `openrouter/anthropic/claude-3.5-sonnet` |
| HuggingFace | `huggingface/org/model` | `huggingface/meta-llama/Llama-3.2-3B-Instruct` |
| Together | `together_ai/org/model` | `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo` |

## Configuration

### Service Configuration

```python
from services.litellm_service import LiteLLMConfig, LiteLLMService

config = LiteLLMConfig(
    default_provider="ollama",
    default_model="llama3.2",
    temperature=0.7,
    max_tokens=4096,
    ollama_base_url="http://localhost:11434",
    enable_caching=True,
    enable_cost_tracking=True
)

svc = LiteLLMService()
svc.config = config
svc._setup_litellm()
```

### Runtime Updates

```python
svc.update_config(
    default_provider="openai",
    default_model="gpt-4o",
    temperature=0.5
)
```

## Error Handling

LiteLLM provides standardized error handling:

```python
from litellm.exceptions import (
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ServiceUnavailableError
)

try:
    response = svc.chat_completion(messages=messages)
except RateLimitError:
    # Handle rate limiting
    pass
except AuthenticationError:
    # Handle auth errors (invalid API key)
    pass
except InvalidRequestError:
    # Handle bad requests
    pass
except ServiceUnavailableError:
    # Handle provider outages
    pass
```

## LangChain Integration

The LiteLLM provider works with LangChain:

```python
from sources.provider_factory import ProviderFactory

provider = ProviderFactory.create("litellm", model="openai/gpt-4o")
llm = provider.get_langchain_llm()

# Use with LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("Tell me about {topic}")
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(topic="AI")
```

## Monitoring & Observability

LiteLLM supports various observability integrations:

```python
import litellm

# LangFuse
litellm.success_callback = ["langfuse"]

# Helicone
litellm.success_callback = ["helicone"]

# Custom callbacks
def log_success(response):
    print(f"Model: {response.model}, Tokens: {response.usage}")

litellm.success_callback = [log_success]
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         LAS API                              │
│                     (FastAPI + Routers)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LiteLLM Router                            │
│              /api/v1/litellm/*                               │
│   • /chat/completions  • /models  • /providers               │
│   • /embeddings        • /vision  • /v1/* (OpenAI proxy)     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LiteLLM Service                            │
│         (Singleton - Unified LLM Interface)                  │
│   • chat_completion()  • create_embedding()                  │
│   • vision_completion() • chat_with_tools()                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LiteLLM SDK                               │
│         (litellm.completion, litellm.acompletion)            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐
        │ Ollama  │     │ OpenAI  │     │ Gemini  │
        │ (Local) │     │ (Cloud) │     │ (Cloud) │
        └─────────┘     └─────────┘     └─────────┘
              │               │               │
              ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐
        │ Groq    │     │Anthropic│     │OpenRouter│
        │ (Cloud) │     │ (Cloud) │     │ (Gateway)│
        └─────────┘     └─────────┘     └─────────┘
```

## Related Files

- `services/litellm_service.py` - Core LiteLLM service
- `sources/providers/litellm_provider.py` - Provider factory integration
- `routers/litellm_router.py` - REST API endpoints
- `components/settings/LiteLLMSettings.tsx` - Frontend settings UI
- `.env.litellm.example` - Environment configuration template

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [Supported Providers](https://docs.litellm.ai/docs/providers)
- [LiteLLM Proxy](https://docs.litellm.ai/docs/simple_proxy)
