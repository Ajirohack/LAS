# LAS UI - Wireframes & Component Architecture

## 1. Main Layout (Shell)

```
+-----------------------------------------------------------------------+
|  [L] Logo  |  [C]  Global Command Bar (Cmd+K)       |  [R] User/Notif |
+-----------------------------------------------------------------------+
|          |                                             |              |
| [NAV]    |                                             |  [INSPECTOR] |
|          |                                             |              |
| - Chat   |             [CENTER STAGE]                  |  - Memory    |
| - Flows  |                                             |  - Config    |
| - Agents |             (Dynamic View)                  |  - Artifacts |
| - Memory |                                             |              |
|          |                                             |              |
|          |                                             |              |
| [Status] |                                             |              |
+-----------------------------------------------------------------------+
```

### Components

* **`AppShell`**: The main grid container. Handles responsive collapsing of sidebars.
* **`GlobalCommandBar`**: A modal search that can trigger actions ("New Chat", "Switch Model", "Search Memory").
* **`NavRail`**: Vertical icon bar with tooltips. Expands on hover.

---

## 2. Chat Interface (Center Stage)

```
+-----------------------------------------------------------------------+
|  [Header: Current Model (GPT-4) | Temp: 0.7 | Tokens: 4k]     [Settings]|
+-----------------------------------------------------------------------+
|                                                                       |
|  [System Message: You are a helpful assistant...]                     |
|                                                                       |
|  [User]: Analyze this data.csv                                        |
|                                                                       |
|  [Agent]:                                                             |
|    > [Thinking] Searching knowledge graph... (Done)                   |
|    > [Tool] Executing Python analysis...                              |
|      +------------------------------------------+                     |
|      |  import pandas as pd                     |                     |
|      |  df = pd.read_csv('data.csv')            |                     |
|      +------------------------------------------+                     |
|                                                                       |
|    Here is the summary of your data...                                |
|    [Chart Component Rendered Here]                                    |
|                                                                       |
+-----------------------------------------------------------------------+
|  [Input Deck]                                                         |
|  [ (+) ] [ Type a message...                                ] [ (^) ] |
|  [ Model: GPT-4 ] [ Voice ] [ Web Search: On ]                        |
+-----------------------------------------------------------------------+
```

### Components

* **`MessageList`**: Virtualized scroll container.
* **`MessageBubble`**: Polymorphic component (User/Agent/System).
* **`ThoughtChain`**: Collapsible accordion for internal agent steps.
* **`CodeBlock`**: Syntax highlighted code with "Copy" and "Run" buttons.
* **`InputDeck`**: Complex form with file upload, voice recording, and text area.

---

## 3. Workflow Builder (Center Stage - Mode 2)

```
+-----------------------------------------------------------------------+
|  [Back]  Workflow: Daily News Digest              [Run] [Save] [Deploy]|
+-----------------------------------------------------------------------+
| [Nodes]  |                                                            |
|          |           (Canvas - React Flow)                            |
| - Trigger|                                                            |
| - LLM    |    [Timer] ----> [Web Scraper]                             |
| - Code   |                       |                                    |
| - Email  |                       v                                    |
|          |                 [Summarizer LLM]                           |
|          |                       |                                    |
|          |                       v                                    |
|          |                 [Email Sender]                             |
|          |                                                            |
+-----------------------------------------------------------------------+
```

### Components

* **`WorkflowCanvas`**: Wrapper around React Flow.
* **`NodePalette`**: Draggable list of available node types.
* **`NodeInspector`**: Properties panel for the selected node (appears in Right Panel).

---

## 4. Memory Visualizer (Right Panel / Full Screen)

```
+-----------------------------------------------------------------------+
|  Search Memory...                                          [Filter]   |
+-----------------------------------------------------------------------+
|                                                                       |
|          (O) Python                                                   |
|           |                                                           |
|  (O) LAS -+---- (O) API                                               |
|           |                                                           |
|          (O) Architecture                                             |
|                                                                       |
+-----------------------------------------------------------------------+
|  Selected Node: LAS API                                               |
|  Content: The Local Agent System API v1...                            |
+-----------------------------------------------------------------------+
```

### Components

* **`ForceGraph`**: Interactive 2D/3D graph visualizer.
* **`NodeDetails`**: Card showing the raw text/embedding data of a memory fragment.

---

## 5. Implementation Architecture

### Directory Structure (`src/`)

```
components/
  ├── ui/               # Shadcn/Radix primitives (Button, Input, Dialog)
  ├── layout/           # Shell, Sidebar, Header
  ├── chat/             # MessageBubble, InputDeck, ThoughtChain
  ├── workflow/         # CustomNodes, Canvas, Palette
  ├── visualization/    # MemoryGraph, Charts, CodeBlock
  └── providers/        # ThemeProvider, AuthProvider, QueryProvider
lib/
  ├── api.ts            # Typed Axios client
  ├── store.ts          # Zustand global state (user, settings)
  ├── hooks.ts          # Custom React hooks
  └── utils.ts          # Helpers
app/
  ├── page.tsx          # Main Chat
  ├── workflows/        # Workflow Builder
  ├── memory/           # Memory Graph
  └── settings/         # Config
```
