# LAS UI - Design Concept: "The Live Command Center"

**Philosophy:**
The LAS UI is not just a chat interface; it is a **Command Center** for orchestrating intelligence. It treats the AI not as a passive responder, but as an active agent working in real-time. The interface must reflect this "aliveness" through constant feedback loops, visualizers, and fluid transitions.

---

## 1. Core UX Pillars

1. **"Always Alive" Feedback:**
    * Never show a static spinner. Show *what* the agent is doing (e.g., "Searching web...", "Querying vector DB...", "Generating image...").
    * Use a **"Pulse"** animation in the UI chrome to indicate system heartbeat/latency.

2. **Context is King:**
    * The **Memory Graph** isn't hidden in settings; it's a collapsible panel that lights up when the agent recalls a fact.
    * **Active Tools** are displayed as "Equipped Items" in the agent's status bar.

3. **Fluid Modality:**
    * Seamless switching between **Chat Mode** (text/voice) and **Canvas Mode** (workflows/artifacts).
    * Drag-and-drop anything (images, PDFs, code files) anywhere.

4. **Glassmorphic & Cinematic:**
    * Dark mode default.
    * Translucent panels with background blur (`backdrop-filter: blur(12px)`).
    * Neon accents based on the active provider (e.g., Green for OpenAI, Purple for Anthropic, Orange for Groq).

---

## 2. Layout Strategy: "The Triptych"

The screen is divided into three adaptive columns.

### **Left Panel: Context & Navigation (20%)**

* **Top:** User Profile & Workspace Switcher.
* **Middle:** Session History (grouped by "Today", "Yesterday", "Projects").
* **Bottom:** System Status (CPU/RAM/GPU usage from `/api/v1/perf`).
* **Behavior:** Collapsible to icons-only.

### **Center Stage: The Stream (60%)**

* **The Feed:** A continuous scroll of interaction. Not just bubbles, but "Events".
  * *User Event:* "Analyze this file."
  * *System Event:* "Reading file..." (Progress bar).
  * *Agent Event:* "I found 3 errors." (Code block).
* **Input Deck:** A floating command bar at the bottom.
  * Text input with `/` command support.
  * Voice toggle (Waveform visualizer).
  * Attachment clip.
  * Model selector dropdown.

### **Right Panel: The Inspector (20%)**

* **Tabs:**
    1. **Memory:** Force-directed graph of related concepts.
    2. **Workflow:** Mini-map of the current agent chain.
    3. **Artifacts:** List of generated files/images.
    4. **Settings:** Quick toggles for temperature, system prompt.
* **Behavior:** Context-aware. If the user asks about "Memory", this panel auto-expands.

---

## 3. Visual Language (Design System)

* **Typography:** `Inter` (UI) + `JetBrains Mono` (Code).
* **Colors:**
  * Background: `#09090B` (Zinc 950)
  * Surface: `#18181B` (Zinc 900) with 50% opacity.
  * Primary: `#3B82F6` (Blue 500) -> Gradients.
  * Success: `#10B981` (Emerald 500).
  * Error: `#EF4444` (Red 500).
* **Radius:** `rounded-xl` (12px) for panels, `rounded-full` for buttons.
* **Motion:** `framer-motion` for all state changes. No instant jumps.

---

## 4. Key Interaction Flows

### A. The "Thinking" Flow

1. User submits query.
2. Input bar locks, shows a "Stop" button.
3. A "Thought Stream" accordion appears in the chat.
    * *Step 1:* "Routing to Groq..." (0.2s)
    * *Step 2:* "Retrieving context..." (0.5s)
4. Final response streams in token-by-token.
5. Thought Stream collapses to a summary icon "Thinking (1.2s)".

### B. The Workflow Builder

1. User clicks "Create Workflow".
2. Center Stage transforms into an infinite canvas (React Flow).
3. Right Panel becomes a "Node Library".
4. User drags "Twitter Scraper" node -> "Summarizer" node -> "Email" node.
5. Connecting nodes draws animated bezier curves.

### C. The "Live" Dashboard

1. User pins a "System Monitor" widget to the top right.
2. It subscribes to `ws://api/v1/perf/stream`.
3. Real-time sparklines show Token/sec and Cache Hit Rate.
