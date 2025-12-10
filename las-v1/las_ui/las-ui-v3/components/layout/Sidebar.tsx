"use client";

import { useState } from "react";
import { useAppStore, ChatSession, Workspace } from "@/app/store";
import { useRouter } from "next/navigation";
import { formatRelativeTime } from "@/lib/utils";
import {
  MessageSquare,
  Workflow,
  Brain,
  Settings,
  ChevronDown,
  Plus,
  MoreVertical,
  Search,
  Circle,
  Pencil,
  Check,
  X,
  LayoutGrid,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { WorkspaceManager } from "./WorkspaceManager";

export function Sidebar() {
  const {
    sessions,
    currentSessionId,
    setCurrentSession,
    addSession,
    deleteSession,
    updateSession,
    workspaces,
    currentWorkspaceId,
    setCurrentWorkspace,
    addWorkspace,
    activePanel,
    setActivePanel,
  } = useAppStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [showWorkspaceMenu, setShowWorkspaceMenu] = useState(false);
  const [showWorkspaceManager, setShowWorkspaceManager] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editSessionTitle, setEditSessionTitle] = useState("");
  const router = useRouter();

  const currentWorkspace =
    workspaces.find((w) => w.id === currentWorkspaceId) || workspaces[0];

  const startEditingSession = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditSessionTitle(session.title);
  };

  const saveSessionTitle = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    if (editingSessionId && editSessionTitle.trim()) {
      updateSession(editingSessionId, { title: editSessionTitle.trim() });
      setEditingSessionId(null);
      setEditSessionTitle("");
    }
  };

  const cancelSessionEdit = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    setEditingSessionId(null);
    setEditSessionTitle("");
  };

  // Group sessions by date
  const groupedSessions = sessions.reduce((groups, session) => {
    const now = new Date();
    const sessionDate = new Date(session.timestamp);
    const diffDays = Math.floor(
      (now.getTime() - sessionDate.getTime()) / (1000 * 60 * 60 * 24)
    );

    let group: string;
    if (diffDays === 0) {
      group = "Today";
    } else if (diffDays === 1) {
      group = "Yesterday";
    } else if (diffDays < 7) {
      group = "This Week";
    } else if (diffDays < 30) {
      group = "This Month";
    } else {
      group = "Older";
    }

    if (!groups[group]) groups[group] = [];
    groups[group].push(session);
    return groups;
  }, {} as Record<string, ChatSession[]>);

  const navItems = [
    { id: "chat", label: "Chat", icon: MessageSquare, shortcut: "⌘1" },
    { id: "workflow", label: "Workflows", icon: Workflow, shortcut: "⌘2" },
    { id: "memory", label: "Memory", icon: Brain, shortcut: "⌘3" },
  ];

  const handleNavigation = (panelId: string) => {
    const routes: Record<string, string> = {
      chat: "/",
      workflow: "/workflow",
      memory: "/memory",
    };

    setActivePanel(panelId as "chat" | "workflow" | "memory" | "settings");
    router.push(routes[panelId] || "/");
  };

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: "New Chat",
      timestamp: new Date(),
      messageCount: 0,
    };
    addSession(newSession);
    setCurrentSession(newSession.id);
  };

  const createNewWorkspace = () => {
    const colors = [
      "#3b82f6",
      "#10b981",
      "#f59e0b",
      "#ef4444",
      "#8b5cf6",
      "#ec4899",
    ];
    const newWorkspace: Workspace = {
      id: Date.now().toString(),
      name: `Workspace ${workspaces.length + 1}`,
      color: colors[workspaces.length % colors.length],
      isActive: false,
    };
    addWorkspace(newWorkspace);
  };

  const filteredSessions = sessions.filter(
    (session) =>
      session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.lastMessage?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-full flex-col glass-panel border-r border-border">
      {/* Header with Workspace Switcher */}
      <div className="p-4 border-b border-border">
        <DropdownMenu
          open={showWorkspaceMenu}
          onOpenChange={setShowWorkspaceMenu}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-between p-2 h-auto">
              <div className="flex items-center gap-2">
                <Circle
                  className="w-3 h-3"
                  style={{ color: currentWorkspace.color }}
                  fill="currentColor"
                />
                <span className="font-medium">{currentWorkspace.name}</span>
              </div>
              <ChevronDown className="w-4 h-4 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="start">
            <div className="px-2 py-1.5 text-sm font-semibold">Workspaces</div>
            <DropdownMenuSeparator />
            {workspaces.map((workspace) => (
              <DropdownMenuItem
                key={workspace.id}
                onClick={() => setCurrentWorkspace(workspace.id)}
                className="flex items-center gap-2">
                <Circle
                  className="w-3 h-3"
                  style={{ color: workspace.color }}
                  fill={workspace.isActive ? "currentColor" : "none"}
                />
                <span>{workspace.name}</span>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => setShowWorkspaceManager(true)}>
              <LayoutGrid className="w-4 h-4 mr-2" />
              Manage Workspaces
            </DropdownMenuItem>
            <DropdownMenuItem onClick={createNewWorkspace}>
              <Plus className="w-4 h-4 mr-2" />
              New Workspace
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <WorkspaceManager
          open={showWorkspaceManager}
          onOpenChange={setShowWorkspaceManager}
        />
      </div>

      {/* Search Bar */}
      <div className="p-4 border-b border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-b border-border">
        <Button
          onClick={createNewSession}
          className="w-full justify-start"
          variant="outline">
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Navigation */}
      <div className="p-4 border-b border-border">
        <nav className="space-y-1">
          {navItems.map((item) => (
            <Button
              key={item.id}
              onClick={() => handleNavigation(item.id)}
              variant={activePanel === item.id ? "default" : "ghost"}
              className="w-full justify-start">
              <item.icon className="w-4 h-4 mr-3" />
              <span className="flex-1">{item.label}</span>
              <span className="text-xs opacity-50">{item.shortcut}</span>
            </Button>
          ))}
        </nav>
      </div>

      {/* Session History */}
      <div className="flex-1 overflow-hidden">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-muted-foreground">
              Recent
            </h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={createNewSession}
              className="h-6 px-2">
              <Plus className="w-3 h-3" />
            </Button>
          </div>

          <ScrollArea className="h-[300px]">
            <div className="space-y-2">
              {Object.entries(groupedSessions).map(([group, groupSessions]) => {
                const filteredGroupSessions = searchQuery
                  ? filteredSessions.filter((s) => groupSessions.includes(s))
                  : groupSessions;

                if (filteredGroupSessions.length === 0) return null;

                return (
                  <div key={group} className="space-y-1">
                    <div className="px-2 py-1 text-xs font-medium text-muted-foreground">
                      {group}
                    </div>
                    {filteredGroupSessions.map((session) => (
                      <div
                        key={session.id}
                        className={`
                          group flex items-center justify-between p-2 rounded-md cursor-pointer
                          hover:bg-accent hover:text-accent-foreground transition-colors
                          ${
                            currentSessionId === session.id
                              ? "bg-accent text-accent-foreground"
                              : ""
                          }
                        `}
                        onClick={() => setCurrentSession(session.id)}>
                        {editingSessionId === session.id ? (
                          <div
                            className="flex items-center gap-1 flex-1 min-w-0"
                            onClick={(e) => e.stopPropagation()}>
                            <Input
                              value={editSessionTitle}
                              onChange={(e) =>
                                setEditSessionTitle(e.target.value)
                              }
                              className="h-7 text-xs px-2"
                              autoFocus
                              onKeyDown={(e) => {
                                if (e.key === "Enter") saveSessionTitle();
                                if (e.key === "Escape") cancelSessionEdit();
                              }}
                            />
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={saveSessionTitle}>
                              <Check className="h-3 w-3 text-green-500" />
                            </Button>
                            <Button
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              onClick={cancelSessionEdit}>
                              <X className="h-3 w-3 text-red-500" />
                            </Button>
                          </div>
                        ) : (
                          <>
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium truncate">
                                {session.title}
                              </div>
                              {session.lastMessage && (
                                <div className="text-xs text-muted-foreground truncate">
                                  {session.lastMessage}
                                </div>
                              )}
                              <div className="text-xs text-muted-foreground">
                                {formatRelativeTime(
                                  new Date(session.timestamp)
                                )}
                              </div>
                            </div>

                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                                  onClick={(e) => e.stopPropagation()}>
                                  <MoreVertical className="w-3 h-3" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                  onClick={() => setCurrentSession(session.id)}>
                                  <MessageSquare className="w-4 h-4 mr-2" />
                                  Open
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={(e) =>
                                    startEditingSession(session, e)
                                  }>
                                  <Pencil className="w-4 h-4 mr-2" />
                                  Rename
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  onClick={() => deleteSession(session.id)}
                                  className="text-destructive">
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}

              {filteredSessions.length === 0 && searchQuery && (
                <div className="text-center text-sm text-muted-foreground py-4">
                  No sessions found matching &quot;{searchQuery}&quot;
                </div>
              )}

              {sessions.length === 0 && !searchQuery && (
                <div className="text-center text-sm text-muted-foreground py-4">
                  No recent sessions
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* User Profile & Settings */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3 mb-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium">User</div>
            <div className="text-xs text-muted-foreground">
              user@example.com
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start"
          onClick={() => {
            setActivePanel("settings");
            // This would open settings dialog instead of navigation
          }}>
          <Settings className="w-4 h-4 mr-2" />
          Settings
        </Button>

        <div className="mt-3 pt-3 border-t border-border">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Status</span>
            <div className="flex items-center gap-1">
              <Circle className="w-2 h-2 fill-green-500 text-green-500" />
              <span>Online</span>
            </div>
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
            <span>Model</span>
            <span>GPT-4</span>
          </div>
        </div>
      </div>
    </div>
  );
}
