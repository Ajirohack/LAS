# AgenticSeek Feature Matrix & API Documentation

## 1. System Overview

AgenticSeek is an autonomous AI agent system that provides multi-modal interaction capabilities through various specialized agents. The system supports both CLI and web-based interfaces with Docker containerization for easy deployment.

### 1.1 Core Architecture
- **Backend**: FastAPI-based REST API server
- **Frontend**: React-based web interface  
- **Agents**: Modular agent system with specialized capabilities
- **Tools**: Extensible tool framework for code execution, web search, file operations
- **LLM Integration**: Multi-provider support (Ollama, OpenAI, DeepSeek, etc.)

## 2. Feature Matrix

### 2.1 Deployment Modes Comparison

| Feature | Docker Deployment | CLI Deployment | Notes |
|---------|------------------|----------------|--------|
| **Core Features** |
| Multi-Agent System | ✅ | ✅ | All 5 agents available |
| Web Interface | ✅ | ❌ | Requires Docker frontend |
| API Server | ✅ | ✅ | Port 7777 default |
| Real-time Interaction | ✅ | ✅ | WebSocket support planned |
| Session Management | ✅ | ✅ | Configurable save/recovery |
| **Agent Capabilities** |
| Casual Agent | ✅ | ✅ | General conversation |
| Code Agent | ✅ | ✅ | Programming tasks |
| File Agent | ✅ | ✅ | File operations |
| Browser Agent | ✅ | ✅ | Web automation |
| Planner Agent | ✅ | ✅ | Task planning |
| **Tool Integration** |
| Python Interpreter | ✅ | ✅ | Code execution |
| Web Search (SearxNG) | ✅ | ❌ | Requires SearxNG service |
| File System Access | ✅ | ✅ | Configurable work directory |
| Browser Automation | ✅ | ✅ | Selenium-based |
| Multi-language Support | ✅ | ✅ | Python, JavaScript, C++, Go, Java |
| **LLM Providers** |
| Ollama (Local) | ✅ | ✅ | Recommended for privacy |
| OpenAI | ✅ | ✅ | API key required |
| DeepSeek | ✅ | ✅ | API key required |
| Google | ✅ | ✅ | API key required |
| Anthropic | ✅ | ✅ | API key required |
| Together AI | ✅ | ✅ | API key required |
| OpenRouter | ✅ | ✅ | API key required |
| **Infrastructure** |
| Redis Caching | ✅ | ❌ | Docker only |
| Load Balancing | ✅ | ❌ | Docker orchestration |
| Service Discovery | ✅ | ❌ | Docker networking |
| Volume Mounting | ✅ | N/A | Persistent storage |
| **Security Features** |
| Sandboxed Execution | ✅ | ✅ | Tool isolation |
| API Rate Limiting | ✅ | ❌ | Planned feature |
| Authentication | ❌ | ❌ | Not implemented |
| Input Validation | ✅ | ✅ | Pydantic models |
| **Monitoring & Logging** |
| Structured Logging | ✅ | ✅ | File-based logs |
| Health Checks | ✅ | ✅ | `/health` endpoint |
| Performance Metrics | ✅ | ❌ | Basic logging only |
| Error Tracking | ✅ | ✅ | Exception handling |

### 2.2 Agent Capabilities Matrix

| Agent | Primary Function | Tools Available | Use Cases | Special Features |
|-------|------------------|-----------------|-----------|------------------|
| **CasualAgent** | General conversation | web_search | Q&A, chat, information | Natural language processing |
| **CoderAgent** | Programming tasks | python, javascript, c++, go, java, bash | Code generation, debugging, analysis | Multi-language support |
| **FileAgent** | File operations | file_finder, file_operations | File management, search, organization | Directory traversal |
| **BrowserAgent** | Web automation | web_search, browser_control | Web scraping, form filling, navigation | Selenium integration |
| **PlannerAgent** | Task planning | web_search, browser_control | Complex task decomposition | Multi-step planning |

## 3. API Endpoints

### 3.1 REST API Specification

#### Core Endpoints

| Endpoint | Method | Description | Request Body | Response | Auth Required |
|----------|--------|-------------|--------------|----------|---------------|
| `/query` | POST | Process natural language query | `QueryRequest` | `QueryResponse` | ❌ |
| `/health` | GET | Health check endpoint | None | `{"status": "healthy"}` | ❌ |
| `/is_active` | GET | Check if system is active | None | `{"is_active": boolean}` | ❌ |
| `/stop` | GET | Stop current operation | None | `{"status": "stopped"}` | ❌ |
| `/latest_answer` | GET | Get latest agent response | None | `QueryResponse` | ❌ |
| `/screenshot` | GET | Get browser screenshot | None | Image file | ❌ |

#### Data Models

**QueryRequest**
```json
{
  "query": "string",           // Required: User's natural language query
  "tts_enabled": boolean       // Optional: Enable text-to-speech (default: true)
}
```

**QueryResponse**
```json
{
  "done": "string",            // "true" or "false"
  "answer": "string",          // Agent's response text
  "reasoning": "string",       // Agent's reasoning process
  "agent_name": "string",      // Name of executing agent
  "success": "string",         // "true" or "false"
  "blocks": {},                // Execution blocks and results
  "status": "string",          // Current status message
  "uid": "string"              // Unique request identifier
}
```

### 3.2 Error Responses

| HTTP Status | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | System busy processing another query |
| 500 | Internal Server Error | Server-side error |

## 4. Tool Interfaces

### 4.1 Code Execution Tools

#### Python Interpreter
- **Tag**: `python`
- **Description**: Execute Python code blocks
- **Capabilities**: Full Python runtime with standard library
- **Security**: Sandboxed execution environment
- **Error Handling**: Exception capture and feedback

#### JavaScript Interpreter  
- **Tag**: `javascript`
- **Description**: Execute JavaScript/Node.js code
- **Capabilities**: Node.js runtime environment
- **Security**: Process isolation

#### Multi-Language Support
- **C++**: `cpp` tag with compiler integration
- **Go**: `go` tag with Go toolchain
- **Java**: `java` tag with JVM execution
- **Bash**: `bash` tag for shell scripting

### 4.2 Web Search Tool

#### SearxSearch Integration
- **Tag**: `web_search`
- **Description**: Privacy-focused web search via SearxNG
- **Configuration**: `SEARXNG_BASE_URL` environment variable
- **Features**: Link validation, paywall detection, content filtering
- **Results Format**: Title, snippet, URL extraction

### 4.3 File System Tools

#### FileFinder
- **Tag**: `file_finder`
- **Description**: Search and locate files in workspace
- **Capabilities**: Pattern matching, directory traversal
- **Security**: Confined to `WORK_DIR` directory

#### File Operations
- **Tag**: `file_operations`
- **Description**: Read, write, and manipulate files
- **Capabilities**: Text processing, file creation, content modification
- **Security**: Workspace directory restrictions

### 4.4 Browser Automation

#### Browser Control
- **Integration**: Selenium WebDriver
- **Capabilities**: Page navigation, form filling, screenshot capture
- **Features**: Stealth mode, anti-detection, multi-language support
- **Configuration**: Headless mode, stealth mode settings

## 5. Configuration Options

### 5.1 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SEARXNG_BASE_URL` | SearxNG instance URL | `http://searxng:8080` | Docker only |
| `REDIS_BASE_URL` | Redis connection URL | `redis://redis:6379/0` | Docker only |
| `WORK_DIR` | Workspace directory path | `/Users/username/Documents/workspace_with_my_files` | ✅ |
| `OLLAMA_PORT` | Ollama service port | `11434` | ❌ |
| `LM_STUDIO_PORT` | LM Studio service port | `1234` | ❌ |
| `BACKEND_PORT` | API server port | `7777` | ❌ |
| `OPENAI_API_KEY` | OpenAI API access key | None | For OpenAI |
| `DEEPSEEK_API_KEY` | DeepSeek API access key | None | For DeepSeek |
| `OPENROUTER_API_KEY` | OpenRouter API access key | None | For OpenRouter |
| `TOGETHER_API_KEY` | Together AI API access key | None | For Together |
| `GOOGLE_API_KEY` | Google AI API access key | None | For Google |
| `ANTHROPIC_API_KEY` | Anthropic API access key | None | For Anthropic |

### 5.2 Configuration File (config.ini)

```ini
[MAIN]
is_local = True                    # Use local LLM provider
provider_name = ollama            # LLM provider name
provider_model = deepseek-r1:14b  # Model identifier
provider_server_address = 127.0.0.1:11434  # Provider server
agent_name = Jarvis                # Default agent name
recover_last_session = False       # Auto-recover sessions
save_session = False              # Save conversation history
speak = False                     # Enable text-to-speech
listen = False                    # Enable speech-to-text
jarvis_personality = False        # Use Jarvis personality
languages = en                    # UI languages (space-separated)

[BROWSER]
headless_browser = True           # Run browser in headless mode
stealth_mode = False              # Enable anti-detection measures
```

## 6. OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: AgenticSeek API
  description: Autonomous AI Agent System API
  version: 0.1.0
  contact:
    name: AgenticSeek Team
    url: https://github.com/AgenticSeek
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:7777
    description: Local development server
  - url: http://localhost:3000/api
    description: Docker deployment

paths:
  /health:
    get:
      summary: Health check endpoint
      description: Check if the API server is running and healthy
      operationId: healthCheck
      responses:
        '200':
          description: Server is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  version:
                    type: string
                    example: "0.1.0"

  /is_active:
    get:
      summary: Check system activity
      description: Check if the agent system is currently processing
      operationId: isActive
      responses:
        '200':
          description: System status retrieved
          content:
            application/json:
              schema:
                type: object
                properties:
                  is_active:
                    type: boolean
                    description: Whether the system is currently active

  /query:
    post:
      summary: Process natural language query
      description: Send a query to the agent system for processing
      operationId: processQuery
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          description: Query processed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResponse'
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '429':
          description: Too many requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /stop:
    get:
      summary: Stop current operation
      description: Request the current agent to stop processing
      operationId: stopOperation
      responses:
        '200':
          description: Operation stopped
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "stopped"

  /latest_answer:
    get:
      summary: Get latest response
      description: Retrieve the most recent agent response
      operationId: getLatestAnswer
      responses:
        '200':
          description: Latest answer retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResponse'
        '404':
          description: No answer available
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /screenshot:
    get:
      summary: Get browser screenshot
      description: Retrieve the latest browser screenshot
      operationId: getScreenshot
      responses:
        '200':
          description: Screenshot available
          content:
            image/png:
              schema:
                type: string
                format: binary
        '404':
          description: No screenshot available
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    QueryRequest:
      type: object
      required:
        - query
      properties:
        query:
          type: string
          description: The natural language query to process
          example: "What is the weather like today?"
        tts_enabled:
          type: boolean
          description: Enable text-to-speech for the response
          default: true
          example: true

    QueryResponse:
      type: object
      properties:
        done:
          type: string
          description: Whether the query processing is complete
          enum: ["true", "false"]
        answer:
          type: string
          description: The agent's response text
          example: "The weather today is sunny with a temperature of 72°F."
        reasoning:
          type: string
          description: The agent's reasoning process
          example: "I searched for current weather information and found..."
        agent_name:
          type: string
          description: Name of the agent that processed the query
          example: "Jarvis"
        success:
          type: string
          description: Whether the operation was successful
          enum: ["true", "false"]
        blocks:
          type: object
          description: Execution blocks and their results
          additionalProperties: true
        status:
          type: string
          description: Current status message
          example: "Ready"
        uid:
          type: string
          description: Unique identifier for this response
          example: "550e8400-e29b-41d4-a716-446655440000"

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
          description: Error message
          example: "No screenshot available"
        status_code:
          type: integer
          description: HTTP status code
          example: 404

tags:
  - name: System
    description: System health and status endpoints
  - name: Agents
    description: Agent interaction and query processing
  - name: Utilities
    description: Utility endpoints for screenshots and control
```

## 7. Validation Requirements

### 7.1 Input Validation

#### QueryRequest Validation
- `query`: Required, non-empty string, max length 10000 characters
- `tts_enabled`: Optional boolean, defaults to true

#### Request Rate Limiting
- Maximum 1 concurrent query per session
- Request timeout: 300 seconds default
- Payload size limit: 1MB

### 7.2 Response Validation

#### QueryResponse Validation
- All fields required in response
- `done`: Must be "true" or "false"
- `success`: Must be "true" or "false"
- `uid`: Must be valid UUID format
- `blocks`: Valid JSON object structure

### 7.3 Error Handling

#### Client Errors (4xx)
- 400: Invalid request format, missing required fields
- 404: Resource not found, invalid endpoint
- 429: Rate limit exceeded, system busy

#### Server Errors (5xx)
- 500: Internal server error, agent failure
- 502: Upstream service unavailable (LLM provider)
- 503: Service temporarily unavailable

## 8. Security Considerations

### 8.1 Code Execution Security
- Sandboxed execution environments
- Process isolation for interpreters
- File system access restrictions
- Network access controls

### 8.2 API Security
- No authentication currently implemented
- Rate limiting recommended for production
- Input sanitization for all endpoints
- CORS configuration for cross-origin requests

### 8.3 Data Protection
- Local processing preference for sensitive data
- API key management via environment variables
- Session data encryption for persistence
- Audit logging for security events

## 9. Performance Characteristics

### 9.1 Response Times
- Health check: < 100ms
- Query processing: 5-60 seconds (depends on complexity)
- Screenshot retrieval: < 1 second
- Concurrent request limit: 1 per session

### 9.2 Resource Requirements
- Memory: 2-8GB depending on LLM model
- CPU: 2-4 cores recommended
- Storage: 1GB for base system + workspace
- Network: Required for web search and cloud LLMs

### 9.3 Scalability Notes
- Single-instance design (no horizontal scaling)
- Redis caching for improved performance
- Docker orchestration for service management
- LLM provider load balancing considerations

This documentation provides a comprehensive overview of the AgenticSeek system's capabilities, API specifications, and deployment options. The feature matrix highlights the differences between Docker and CLI deployments, while the OpenAPI specification enables easy integration with other systems.