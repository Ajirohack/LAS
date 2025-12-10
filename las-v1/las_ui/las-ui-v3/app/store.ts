import { create } from "zustand";
import { persist } from "zustand/middleware";
import { ToastItem } from "@/components/ui/toast-container";
import { Node, Edge } from "reactflow";

export interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
  lastMessage?: string;
}

export interface Workspace {
  id: string;
  name: string;
  color: string;
  isActive: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
  status: "active" | "draft" | "completed";
  lastRun?: Date;
  lastRunDurationMs?: number;
  lastRunStatus?: "success" | "failed";
  createdAt: Date;
  updatedAt: Date;
}

export interface CommandItem {
  id: string;
  title: string;
  subtitle?: string;
  category: "navigation" | "action" | "settings" | "help";
  shortcut?: string;
  icon?: string;
  action: () => void;
}

export interface ProviderConfig {
  name: string;
  enabled: boolean;
  apiKey?: string;
  baseUrl?: string;
  models: string[];
  defaultModel: string;
}

interface AppState {
  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  activePanel: "chat" | "workflow" | "memory" | "settings";
  setActivePanel: (panel: "chat" | "workflow" | "memory" | "settings") => void;

  // Command Bar State
  commandBarOpen: boolean;
  openCommandBar: () => void;
  closeCommandBar: () => void;
  toggleCommandBar: () => void;

  // Session Management
  sessions: ChatSession[];
  currentSessionId: string | null;
  addSession: (session: ChatSession) => void;
  updateSession: (id: string, updates: Partial<ChatSession>) => void;
  deleteSession: (id: string) => void;
  setCurrentSession: (id: string) => void;

  // Workspace Management
  workspaces: Workspace[];
  currentWorkspaceId: string;
  addWorkspace: (workspace: Workspace) => void;
  updateWorkspace: (id: string, updates: Partial<Workspace>) => void;
  deleteWorkspace: (id: string) => void;
  setCurrentWorkspace: (id: string) => void;

  // Workflow Management
  workflows: Workflow[];
  addWorkflow: (workflow: Workflow) => void;
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void;
  deleteWorkflow: (id: string) => void;

  // Inspector Panel State
  inspectorTab: "memory" | "workflow" | "artifacts" | "settings";
  setInspectorTab: (
    tab: "memory" | "workflow" | "artifacts" | "settings"
  ) => void;
  inspectorExpanded: boolean;
  toggleInspector: () => void;

  // Agent State
  selectedProvider: string;
  selectedModel: string;
  setProvider: (provider: string, model: string) => void;
  setSelectedProvider: (provider: string) => void;
  setSelectedModel: (model: string) => void;

  // Settings
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;

  // AI Providers Configuration
  providers: Record<string, ProviderConfig>;
  updateProvider: (provider: string, config: ProviderConfig) => void;

  // Recent Commands
  recentCommands: string[];
  addRecentCommand: (commandId: string) => void;

  // Toast Notifications
  toasts: ToastItem[];
  addToast: (toast: Omit<ToastItem, "id">) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // UI State
      sidebarOpen: true,
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      activePanel: "chat",
      setActivePanel: (panel) => set({ activePanel: panel }),

      // Command Bar State
      commandBarOpen: false,
      openCommandBar: () => set({ commandBarOpen: true }),
      closeCommandBar: () => set({ commandBarOpen: false }),
      toggleCommandBar: () =>
        set((state) => ({ commandBarOpen: !state.commandBarOpen })),

      // Session Management
      sessions: [],
      currentSessionId: null,
      addSession: (session) =>
        set((state) => ({
          sessions: [session, ...state.sessions],
          currentSessionId: session.id,
        })),
      updateSession: (id, updates) =>
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === id ? { ...session, ...updates } : session
          ),
        })),
      deleteSession: (id) =>
        set((state) => ({
          sessions: state.sessions.filter((session) => session.id !== id),
          currentSessionId:
            state.currentSessionId === id ? null : state.currentSessionId,
        })),
      setCurrentSession: (id) => set({ currentSessionId: id }),

      // Workspace Management
      workspaces: [
        { id: "default", name: "Default", color: "#3b82f6", isActive: true },
      ],
      currentWorkspaceId: "default",
      addWorkspace: (workspace) =>
        set((state) => ({
          workspaces: [
            ...state.workspaces.map((w) => ({ ...w, isActive: false })),
            workspace,
          ],
          currentWorkspaceId: workspace.id,
        })),
      updateWorkspace: (id, updates) =>
        set((state) => ({
          workspaces: state.workspaces.map((workspace) =>
            workspace.id === id ? { ...workspace, ...updates } : workspace
          ),
        })),
      deleteWorkspace: (id) =>
        set((state) => {
          if (state.workspaces.length <= 1) return state;
          const newWorkspaces = state.workspaces.filter((w) => w.id !== id);
          const newCurrentId =
            state.currentWorkspaceId === id
              ? newWorkspaces[0].id
              : state.currentWorkspaceId;
          return {
            workspaces: newWorkspaces.map((w, i) => ({
              ...w,
              isActive: i === 0,
            })),
            currentWorkspaceId: newCurrentId,
          };
        }),
      setCurrentWorkspace: (id) =>
        set((state) => ({
          workspaces: state.workspaces.map((workspace) => ({
            ...workspace,
            isActive: workspace.id === id,
          })),
          currentWorkspaceId: id,
        })),

      // Workflow Management
      workflows: [],
      addWorkflow: (workflow) =>
        set((state) => ({ workflows: [workflow, ...state.workflows] })),
      updateWorkflow: (id, updates) =>
        set((state) => ({
          workflows: state.workflows.map((workflow) =>
            workflow.id === id ? { ...workflow, ...updates } : workflow
          ),
        })),
      deleteWorkflow: (id) =>
        set((state) => ({
          workflows: state.workflows.filter((workflow) => workflow.id !== id),
        })),

      // Inspector Panel State
      inspectorTab: "memory",
      setInspectorTab: (tab) => set({ inspectorTab: tab }),
      inspectorExpanded: true,
      toggleInspector: () =>
        set((state) => ({ inspectorExpanded: !state.inspectorExpanded })),

      // Agent State
      selectedProvider: "openai",
      selectedModel: "gpt-4",
      setProvider: (provider, model) =>
        set({ selectedProvider: provider, selectedModel: model }),
      setSelectedProvider: (provider) => set({ selectedProvider: provider }),
      setSelectedModel: (model) => set({ selectedModel: model }),

      // Theme
      theme: "dark",
      setTheme: (theme) => set({ theme }),

      // AI Providers Configuration
      providers: {
        openai: {
          name: "OpenAI",
          enabled: true,
          models: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
          defaultModel: "gpt-4",
        },
        anthropic: {
          name: "Anthropic",
          enabled: false,
          models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
          defaultModel: "claude-3-sonnet",
        },
      },
      updateProvider: (provider, config) =>
        set((state) => ({
          providers: { ...state.providers, [provider]: config },
        })),

      // Recent Commands
      recentCommands: [],
      addRecentCommand: (commandId) =>
        set((state) => ({
          recentCommands: [
            commandId,
            ...state.recentCommands.filter((id) => id !== commandId),
          ].slice(0, 10),
        })),

      // Toast Notifications
      toasts: [],
      addToast: (toast) =>
        set((state) => ({
          toasts: [
            ...state.toasts,
            { ...toast, id: `toast-${Date.now()}-${Math.random()}` },
          ],
        })),
      removeToast: (id) =>
        set((state) => ({
          toasts: state.toasts.filter((toast) => toast.id !== id),
        })),
      clearToasts: () => set({ toasts: [] }),
    }),
    {
      name: "las-ui-storage",
      partialize: (state) => ({
        theme: state.theme,
        selectedProvider: state.selectedProvider,
        selectedModel: state.selectedModel,
        providers: state.providers,
        sessions: state.sessions,
        workspaces: state.workspaces,
        currentWorkspaceId: state.currentWorkspaceId,
        workflows: state.workflows,
        recentCommands: state.recentCommands,
      }),
    }
  )
);
