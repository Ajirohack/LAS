# LAS Core Architecture

## Overview

LAS (Local Agent System) is a sophisticated autonomous agent platform built on **Python FastAPI**. It leverages **LangGraph** for hierarchical multi-agent orchestration and **Qdrant** for semantic memory (RAG).

## System Components

### 1. Core API (`api.py`)

- **Framework**: FastAPI
- **Authentication**: JWT-based auth with role management (`routers/auth.py`).
- **Endpoints**: V1 API structure (`/api/v1/`) covering Query, Memory, Voice, Plugins, and Workflows.

### 2. Agent Orchestration (`agents/hierarchical_graph.py`)

- **Engine**: **LangGraph** (StateGraph).
- **Structure**: Hierarchical Multi-Agent System.
  - **TopSupervisor**: Routes tasks to specialized teams.
  - **Teams**:
    - `ResearchTeam`: Web browsing and information gathering.
    - `CodingTeam`: Code generation and execution.
  - **Workers**:
    - `Planner`: Decomposes complex user requests.
    - `Critic`: Reviews plans and outputs.
    - `AdHocWorker`: Handles general tasks.
- **Flow**: User Query -> Planner -> Critic -> Supervisor -> Team/Worker -> MemoryHook -> Supervisor -> End.

### 3. Memory System (`services/memory_service.py`)

A 3-tier memory architecture:

1. **Episodic (Short-term)**: Session-based conversation history stored in **PostgreSQL**.
2. **Semantic (Long-term)**: Vector-based retrieval using **Qdrant** (`rag_service.py`).
3. **Entity (Facts)**: Structured data about users/projects stored in **PostgreSQL**.
4. **Knowledge Graph**: Graph-based relationship mapping (`agents/memory/knowledge_graph.py`).

### 4. Integration Services

- **LLM Service**: Multi-provider support (Ollama, OpenAI, Anthropic, etc.) via `services/llm_service.py`.
- **MCP Server**: Implements Model Context Protocol to expose LAS tools to external apps (`services/mcp_server.py`).
- **Voice**: Integrated TTS and STT (Whisper) capabilities.

### 5. Infrastructure

- **Containerization**: Docker Compose.
- **Services**:
  - `las-backend`: Python API.
  - `las-frontend`: Next.js UI (located at `../las_ui/las-ui-v2`).
  - `las-postgres`: Relational DB.
  - `las-qdrant`: Vector DB.
  - `las-redis`: Caching (implied for performance).

## Data Flow

1. **Request**: User sends query via REST API or WebSocket.
2. **Auth**: Request is validated via JWT.
3. **Orchestration**: `InteractionService` initializes the LangGraph workflow.
4. **Execution**: Agents execute tools (Browser, File, Code) and query Memory.
5. **Persistence**: Results and interactions are saved to Postgres and Qdrant.
6. **Response**: Final answer is returned to the user.
