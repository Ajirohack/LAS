# LAS v1 – Fix Plans and Implementation Guide

This guide enumerates the blocking defects and incomplete integrations identified in the project review, with detailed implementation plans, proposed code changes, and validation steps.

## 1) Wire `InteractionService` into API Query Route

- Problem: `interaction_service` is `None` in `las_core/routers/query.py:47–49`. No wiring exists in `api.py`.
- Impact: `POST /api/v1/query` returns 500 and cannot process queries.
- Plan:
  - Initialize the `InteractionService` at app startup and pass it to the query router via its `set_interaction_service`.
  - Ensure initialization does not run heavy I/O on import.
- Proposed Changes:
  - In `las_core/api.py`, after creating `app` and routers:
    ```python
    # las_core/api.py (near router includes)
    from services.interaction_service import get_interaction_service
    from routers import query as query_router
    query_router.set_interaction_service(get_interaction_service())
    ```
- Validation:
  - Start API, POST `/api/v1/query` with `{"query":"hello"}` and confirm 200 with `answer` populated.

## 2) Define or Remove `is_running_in_docker()` in `api.py`

- Problem: `las_core/api.py:176–184` references `is_running_in_docker()` which is undefined.
- Impact: Script entrypoint path crashes on run.
- Plan:
  - Add a helper function mirroring `las_core/services/interaction_service.py:88–96`.
- Proposed Changes:
  ```python
  # las_core/api.py (top-level or near __main__)
  def is_running_in_docker():
      import os
      if os.path.exists('/.dockerenv'):
          return True
      try:
          with open('/proc/1/cgroup','r') as f:
              return 'docker' in f.read()
      except:
          return False
  ```
- Validation:
  - Run `python las_core/api.py` both on host and inside container; confirm it prints the appropriate message and starts.

## 3) Fix Async Misuse in `WebSurferAgent.run`

- Problem: `ToolService.execute_command` is async (`las_core/services/tool_service.py:80–96`), but `las_core/agents/workers/web_surfer.py:23–35` calls it synchronously.
- Impact: Returns coroutine objects; graph produces incorrect results.
- Plan:
  - Make `web_surfer_node` and `WebSurferAgent.run` async and `await` command execution.
  - If LangGraph requires sync node, wrap with `anyio.from_thread.run` or use `graph.ainvoke`.
- Proposed Changes:
  ```python
  # las_core/agents/workers/web_surfer.py
  class WebSurferAgent:
      async def run(self, state):
          messages = state["messages"]
          last_message = messages[-1].content
          if "search" in last_message.lower():
              result = await self.tool_service.execute_command("web_search", query=last_message, num_results=3)
              from langchain_core.messages import HumanMessage
              return {"messages":[HumanMessage(content=f"Search Results: {result}")]}
          # ... similarly for browse_website

  async def web_surfer_node(state):
      agent = WebSurferAgent()
      return await agent.run(state)
  ```
- Validation:
  - Add a test query with “search” and verify results are strings, not coroutine repr.
  - Run the graph via `ainvoke` to respect async nodes.

## 4) Repair Truncated Method in `BrowserExtension`

- Problem: `las_core/extensions/browser_extension.py:155–157` is truncated (decorator string incomplete) and missing `get_navigable` implementation.
- Impact: Import of extension fails; tool registration incomplete.
- Plan:
  - Complete the decorator and implement `get_navigable` to return navigable links from `Browser.get_navigable()`.
- Proposed Changes:
  ```python
  # las_core/extensions/browser_extension.py (append the method)
  @command(description="Returns a list of all navigable links on the current page.")
  def get_navigable(self) -> list[str]:
      return self.browser.get_navigable()
  ```
- Validation:
  - Restart `ToolService` and confirm command appears in `get_available_commands()`.

## 5) Fix `SearchExtension` Import Mismatch

- Problem: `las_core/extensions/search_extension.py:1–12` imports `sources.tools.web_search.WebSearchTool` which does not exist; actual tool is `searxSearch` (and `webSearch.py`).
- Impact: Extension load fails; web_search command unregistered.
- Plan:
  - Replace with instantiation of `searxSearch` from `sources.tools.searxSearch` or implement `WebSearchTool` wrapper matching expected API.
- Proposed Changes:
  ```python
  from sources.tools.searxSearch import searxSearch
  class SearchExtension:
      def __init__(self):
          self.tool = searxSearch()
          self.commands = {"web_search": self.web_search}
      def web_search(self, query: str, num_results: int = 5):
          return self.tool.execute([query])
  ```
- Validation:
  - Ensure `SEARXNG_BASE_URL` is set; call `ToolService.execute_command("web_search", query="..." )` and receive results.

## 6) Align Rate Limiting Paths to v1

- Problem: `las_core/middleware/security_middleware.py:48–56` enforces strict limits on `/api/auth/...`, while current routes are under `/api/v1/auth/...`.
- Impact: Sensitive rate limits do not apply to v1 endpoints.
- Plan:
  - Change patterns to `/api/v1/auth/login`, `/api/v1/auth/register`, `/api/v1/auth/refresh`.
- Proposed Changes:
  ```python
  strict_limits = {
      "/api/v1/auth/login": {"limit": 5, "window": 60},
      "/api/v1/auth/register": {"limit": 3, "window": 3600},
      "/api/v1/auth/refresh": {"limit": 10, "window": 60},
  }
  ```
- Validation:
  - Hit the endpoints rapidly and confirm 429 responses per configured windows.

## 7) Unify Database Strategy

- Problem: Auth models use SQLite (`las_core/database/models.py:13–117`), while memory service is async Postgres (`las_core/services/db/postgres.py:8–12`).
- Impact: Operational complexity and inconsistent persistence; complicates deployment.
- Plan:
  - Choose Postgres as primary. Port auth models to async SQLAlchemy, and migrate to Postgres DSN from `Settings`.
  - Provide migration scripts (Alembic) and one-time data migration from SQLite if needed.
- Proposed Changes (directional):
  - Replace `create_engine` with `create_async_engine` and `AsyncSessionLocal`.
  - Update all DB interactions in `routers/auth.py` and `services/auth_service.py` to async sessions.
- Validation:
  - Run migrations; execute register/login flows; verify memory services operate on same Postgres.

## 8) Refactor Planner/Coder Workers to Use `LLMService`

- Problem: `PlannerAgent` and `CoderAgent` instantiate `ChatOllama` directly (`las_core/agents/workers/planner.py:6–14`, `las_core/agents/workers/coder.py:5–17`).
- Impact: Hard-codes model/provider; ignores provider abstraction and preferences.
- Plan:
  - Inject `llm = get_llm_service().get_langchain_llm()` and remove direct `ChatOllama` references.
- Proposed Changes:
  ```python
  from services.llm_service import get_llm_service
  class PlannerAgent:
      def __init__(self):
          self.llm = get_llm_service().get_langchain_llm()
  ```
  (Similarly for `CoderAgent`.)
- Validation:
  - Switch provider/model via preferences; verify Planner/Coder reflect the change.

## 9) Implement Workflow Execution Engine

- Problem: `POST /api/v1/workflows/{id}/execute` returns a placeholder message (`las_core/routers/workflows.py:142–161`).
- Impact: No actual workflow execution available.
- Plan:
  - Implement directed graph traversal from nodes/edges; define supported node types (`agent`, `tool`, `decision`, `start`, `end`).
  - Maintain a mutable `state` dict; pass outputs between nodes.
  - Reuse existing agents via `LLMService` and tools via `ToolService`; decisions resolved via LLM or explicit rules.
- Proposed Pseudocode:
  ```python
  def execute_workflow(workflow, inputs):
      state = {"inputs": inputs, "messages": []}
      current = find_start(workflow)
      while current.type != "end":
          if current.type == "agent":
              result = run_agent(current.data, state)
              state.update(result)
          elif current.type == "tool":
              result = await tool_service.execute_command(current.data["command"], **current.data.get("args", {}))
              state[current.id] = result
          elif current.type == "decision":
              current = choose_next_edge(current, state)
              continue
          current = follow_default_edge(current)
      return state
  ```
- Validation:
  - Create a simple workflow (search → analyze → end) and verify outputs flow through.

## 10) API Health & Startup Robustness

- Problem: Startup may attempt heavy I/O; missing readiness checks.
- Plan:
  - Ensure browser is optional at startup (graceful fallback when headless fails).
  - Provide `/health` that checks provider connectivity and DB/Qdrant availability.
- Proposed Changes:
  - Extend `/health` to probe provider (`llm_service.get_available_models()`), DB (`SELECT 1`), and Qdrant `collections`.
- Validation:
  - Observe 200 OK with component statuses; degrade gracefully when services are offline.

## Verification Checklist

- End-to-end query returns valid answer and blocks.
- Async tool commands execute and return strings, not coroutine repr.
- Browser and search extensions import without errors; commands registered.
- Rate limiting applies to v1 auth endpoints; 429 observed under load.
- Unified Postgres used across auth and memory services; migrations applied.
- Planner/Coder respect provider/model selection via preferences.
- Workflows execute and mutate state predictably; simple test passes.

