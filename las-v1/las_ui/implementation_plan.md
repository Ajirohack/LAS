# Phase 2 Implementation Plan - UI Enhancement & Feature Completion

## Goal Description

Complete the LAS UI implementation by building all missing components specified in the design documentation, enhancing existing features, and ensuring full feature parity with the documented wireframes and UX specifications.

## Current State Analysis

### ✅ Completed Components

- API Handler (`app/api/chat/route.ts`)
- Basic AppShell with sidebar navigation
- ChatInterface with streaming support
- WorkflowBuilder with React Flow
- Authentication (Login/Register pages)
- Basic state management (Zustand store)
- WebSocket streaming hook

### ⚠️ Partial/Needs Enhancement

- **AppShell**: Missing Inspector panel content, Global Command Bar
- **ChatInterface**: Missing ThoughtChain visualization, enhanced InputDeck
- **Memory Page**: Basic structure exists but needs full implementation
- **Settings**: Dialog exists but needs robust configuration UI

### ❌ Missing Components

1. Sidebar session history and workspace switcher
2. Global Command Bar (Cmd+K)
3. ThoughtChain/Tool invocation visualizer for chat
4. Enhanced InputDeck with file upload, voice, slash commands
5. Memory Graph visualizer (ForceGraph)
6. Inspector panel with context-aware tabs
7. Settings configuration UI
8. Message virtualization for performance
9. Artifacts/generated files panel

---

## User Review Required

> [!IMPORTANT]
> This plan implements all features from the design documentation. Some components (Memory Graph, Voice Input) may require additional backend endpoints that should be verified before implementation.

> [!WARNING]
> The Memory Graph visualizer will use D3.js for force-directed graphs, which can be performance-intensive. Consider implementing with lazy loading and optimization strategies.

---

## Proposed Changes

### Phase 2.1: Enhanced Navigation & Shell

#### [MODIFY] [AppShell.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/layout/AppShell.tsx)

- Add Global Command Bar (Cmd+K) modal
- Enhance sidebar with session history
- Add workspace switcher
- Implement keyboard shortcut hints

#### [NEW] [Sidebar.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/layout/Sidebar.tsx)

- Session history grouped by date ("Today", "Yesterday", "Projects")
- User profile section with avatar
- Workspace switcher dropdown
- System status indicators

#### [NEW] [Inspector.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/layout/Inspector.tsx)

- Tabbed interface (Memory, Workflow, Artifacts, Settings)
- Context-aware content switching
- Auto-expand behavior based on user actions

#### [NEW] [CommandBar.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/layout/CommandBar.tsx)

- Fuzzy search functionality
- Quick actions ("New Chat", "Switch Model", "Search Memory")
- Keyboard navigation
- Recent commands history

---

### Phase 2.2: Enhanced Chat Experience

#### [MODIFY] [ChatInterface.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/chat/ChatInterface.tsx)

- Add ThoughtChain visualization for agent reasoning
- Integrate enhanced PromptInput with advanced features
- Add message virtualization for performance
- Implement "Stop Generating" button

#### [NEW] [ThoughtChain.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/chat/ThoughtChain.tsx)

- Collapsible accordion showing agent steps
- Step timing visualization
- Tool execution progress indicators
- Summary collapse mode

#### [ENHANCE] [PromptInput.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/ui/prompt-input.tsx)

- File upload via drag-and-drop
- Image preview for attachments
- Voice recording button with waveform
- Slash command autocomplete (/, @, #)
- Model selector dropdown inline

#### [NEW] [MessageVirtualizer.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/chat/MessageVirtualizer.tsx)

- Use `@tanstack/react-virtual` for efficient rendering
- Handle 1000+ messages without lag
- Scroll-to-bottom behavior
- Auto-scroll on new messages

---

### Phase 2.3: Memory & Knowledge Graph

#### [MODIFY] [memory/page.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/app/memory/page.tsx)

- Implement full Memory Visualizer layout
- Search and filter controls
- Node selection and detail view

#### [NEW] [MemoryGraph.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/memory/MemoryGraph.tsx)

- Force-directed graph using D3.js
- Interactive node dragging and zooming
- Cluster detection and coloring
- Search highlighting
- Export to PNG/SVG

#### [NEW] [NodeDetails.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/memory/NodeDetails.tsx)

- Display selected node information
- Show embeddings metadata
- Related nodes visualization
- Edit/delete node actions

---

### Phase 2.4: Settings & Configuration

#### [ENHANCE] [SettingsDialog.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/settings/SettingsDialog.tsx)

- Comprehensive settings UI with tabs:
  - **AI Providers**: Configure API keys, base URLs
  - **Models**: Select default models per provider
  - **General**: Theme, language, notifications
  - **Tools**: Enable/disable integrations
  - **Advanced**: Temperature, top-p, system prompts

#### [NEW] [ProviderConfig.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/settings/ProviderConfig.tsx)

- Provider cards with enable/disable toggles
- API key input with validation
- Model selection dropdowns
- Test connection button

---

### Phase 2.5: Workflow Enhancements

#### [MODIFY] [WorkflowBuilder.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/workflow/WorkflowBuilder.tsx)

- Implement save workflow to backend
- Implement run workflow execution
- Add node palette (draggable sidebar)
- Node property inspector in right panel

#### [NEW] [NodePalette.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/workflow/NodePalette.tsx)

- Categorized node types (Trigger, Action, Condition, Output)
- Drag-and-drop to canvas
- Search/filter nodes

#### [NEW] [NodeInspector.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/workflow/NodeInspector.tsx)

- Edit selected node properties
- Dynamic form based on node type
- Validation and error display

---

### Phase 2.6: Polish & Optimization

#### [NEW] [lib/utils.ts](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/lib/utils.ts)

- Create if doesn't exist, add utility functions:
  - Token counting
  - File size formatting
  - Date/time formatting
  - Debounce/throttle helpers

#### [NEW] [hooks/use-virtual-scroll.ts](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/hooks/use-virtual-scroll.ts)

- Custom hook for message virtualization
- Auto-scroll management
- Performance optimization

#### [NEW] [components/ui/toast.tsx](file:///Volumes/Project Disk/Project Built/Z/Agent Projects🔄/LAS/gemini_build/las_ui/las-ui-v3/components/ui/toast.tsx)

- Install Sonner toast component (if not already)
- Configure global toast provider
- Add toast notifications for actions

---

## Dependencies to Install

```bash
# Virtualization
npm install @tanstack/react-virtual

# D3 for graphs
npm install d3 @types/d3

# Command Bar
npm install cmdk

# Form validation
npm install react-hook-form zod @hookform/resolvers

# File upload
npm install react-dropzone

# Voice recording (optional)
npm install recordrtc
```

---

## Implementation Priority

### High Priority (Phase 2.1-2.2)

1. ✅ Enhanced AppShell with Command Bar
2. ✅ Sidebar with session history
3. ✅ ThoughtChain visualization
4. ✅ Enhanced PromptInput

### Medium Priority (Phase 2.3-2.4)

5. ✅ Memory Graph visualizer
6. ✅ Settings UI enhancement
7. ✅ Inspector panel tabs

### Low Priority (Phase 2.5-2.6)

8. ✅ Workflow save/run backend integration
9. ✅ Message virtualization
10. ✅ Performance optimizations

---

## Verification Plan

### Automated Tests

- Unit tests for utility functions
- Integration tests for Command Bar
- E2E tests for chat workflow

### Manual Verification

1. **Navigation**: Test all keyboard shortcuts (Cmd+K, Cmd+1-3, Cmd+B)
2. **Chat**: Send 100+ messages and verify scrolling performance
3. **Memory**: Load knowledge graph and test node interactions
4. **Settings**: Update provider configs and verify persistence
5. **Workflows**: Create, save, and run a multi-node workflow
6. **Responsive**: Test on mobile, tablet, desktop viewports

---

## Success Criteria

- ✅ All wireframe components implemented
- ✅ Keyboard shortcuts functional
- ✅ Command Bar with fuzzy search
- ✅ Chat handles 1000+ messages smoothly
- ✅ Memory graph renders and is interactive
- ✅ Settings persisted to localStorage/backend
- ✅ Workflows can be saved and executed
- ✅ No TypeScript errors
- ✅ Responsive design on all breakpoints
