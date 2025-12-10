# LAS API Reference & System Analysis

**Generated Date:** 2025-11-25
**Backend Source:** `las_core`
**Target UI:** `las_ui`

---

## 1. API Endpoint Analysis

### A. Authentication (`/api/v1/auth`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| POST | `/register` | `UserCreate` (username, email, password) | `User` (id, email, role) | No | Register new user |
| POST | `/login` | `OAuth2PasswordRequestForm` | `Token` (access, refresh) | No | Login & get JWT |
| POST | `/refresh` | `refresh_token` | `Token` (access) | No | Refresh access token |
| POST | `/logout` | `access_token` | `Message` | Yes | Invalidate token |
| GET | `/me` | - | `User` | Yes | Get current user profile |

### B. Core Query & LLM (`/api/v1/query`, `/api/v1/providers`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| POST | `/query` | `QueryRequest` (query, provider, model) | `QueryResponse` (text, usage) | Yes | Standard LLM query |
| POST | `/query/stream` | `QueryRequest` | `SSE Stream` | Yes | Real-time streaming response |
| GET | `/providers` | - | `List[Provider]` | Yes | List active providers |
| GET | `/providers/{name}/models` | - | `List[Model]` | Yes | List models for provider |

### C. HuggingFace Integration (`/api/v1/hf`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| POST | `/chat` | `HFChatRequest` | `HFResponse` | Yes | Chat with open-source models |
| POST | `/generate` | `HFGenerateRequest` | `HFResponse` | Yes | Text generation |
| POST | `/text-to-image` | `HFImageRequest` | `ImageURL` | Yes | Generate images |
| GET | `/models` | `task`, `limit` | `List[HFModel]` | Yes | Search HF Hub |

### D. Memory & Knowledge (`/api/v1/memory`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| GET | `/knowledge-graph` | - | `GraphData` (nodes, edges) | Yes | Visualize agent memory |
| POST | `/skills` | `SkillCreate` | `Skill` | Yes | Add new capability |
| GET | `/skills` | - | `List[Skill]` | Yes | List learned skills |

### E. Workflows (`/api/v1/workflows`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| GET | `/` | - | `List[Workflow]` | Yes | List user workflows |
| POST | `/` | `WorkflowCreate` | `Workflow` | Yes | Create new workflow |
| POST | `/{id}/execute` | `WorkflowInput` | `WorkflowResult` | Yes | Run a workflow |
| GET | `/{id}/status` | - | `WorkflowStatus` | Yes | Check execution status |

### F. Plugins (`/api/v1/plugins`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| GET | `/installed` | - | `List[Plugin]` | Yes | List active plugins |
| POST | `/install` | `PluginInstall` | `Plugin` | Yes | Install new plugin |
| POST | `/{id}/enable` | - | `Status` | Yes | Enable plugin |

### G. Performance (`/api/v1/perf`)

| Method | Endpoint | Input | Output | Auth Required | Description |
|--------|----------|-------|--------|---------------|-------------|
| GET | `/cache/stats` | - | `CacheStats` | Yes | Redis cache metrics |
| POST | `/cache/clear` | - | `Status` | Admin | Clear system cache |

---

## 2. System Requirements Coverage

### ✅ Core Capabilities

- [x] **Multi-Provider Support:** OpenAI, Anthropic, Gemini, Groq, etc. supported via `/providers`.
- [x] **Real-time Interaction:** Streaming endpoints (`/query/stream`) available.
- [x] **Authentication:** Full JWT flow with RBAC implemented.
- [x] **Memory Persistence:** Knowledge graph endpoints ready for visualization.

### ⚠️ UI Implementation Gaps (To be addressed in Design)

1. **Visualizing "Thinking":** Backend supports streaming, but UI needs a dedicated "Thought Chain" visualizer to parse intermediate steps if the agent provides them.
2. **Workflow Canvas:** Backend has CRUD for workflows, but UI needs a node-based editor (React Flow) to construct the JSON structure `WorkflowCreate` expects.
3. **Memory Graph:** Backend returns nodes/edges; UI needs a force-directed graph renderer (e.g., `react-force-graph` or D3.js).
4. **Plugin Marketplace:** UI needs a discovery interface to browse available plugins before hitting `/install`.

---

## 3. Data Models (TypeScript Interfaces)

```typescript
// Core User
interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user' | 'read-only';
  avatar_url?: string;
}

// LLM Provider
interface Provider {
  id: string;
  name: string; // 'openai', 'anthropic', etc.
  models: string[];
  is_active: boolean;
}

// Chat Message
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  attachments?: Attachment[];
  metadata?: {
    tokens?: number;
    cost?: number;
    provider?: string;
    thinking_time?: number;
  };
}

// Workflow Node
interface WorkflowNode {
  id: string;
  type: 'trigger' | 'action' | 'condition' | 'llm';
  position: { x: number; y: number };
  data: Record<string, any>;
}
```
