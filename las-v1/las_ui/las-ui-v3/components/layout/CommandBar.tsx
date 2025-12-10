"use client";

import { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  MessageSquare,
  Workflow,
  Brain,
  Settings,
  Search,
  Plus,
  FileText,
  Zap,
  HelpCircle,
  History,
  Palette,
} from "lucide-react";

import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandShortcut,
  CommandSeparator,
} from "@/components/ui/command";
import { useAppStore } from "@/app/store";

interface CommandItemDef {
  id: string;
  title: string;
  subtitle?: string;
  category: "navigation" | "action" | "settings" | "help" | "recent";
  shortcut?: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
}

export function CommandBar() {
  const {
    commandBarOpen,
    closeCommandBar,
    toggleCommandBar,
    sessions,
    addRecentCommand,
    setActivePanel,
    setTheme,
    theme,
  } = useAppStore();

  const router = useRouter();

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        toggleCommandBar();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [toggleCommandBar]);

  // Command definitions
  const commands: CommandItemDef[] = useMemo(
    () => [
      // Navigation commands
      {
        id: "nav-chat",
        title: "Go to Chat",
        subtitle: "Open chat interface",
        category: "navigation",
        shortcut: "⌘1",
        icon: MessageSquare,
        action: () => {
          setActivePanel("chat");
          router.push("/");
          closeCommandBar();
        },
      },
      {
        id: "nav-workflow",
        title: "Go to Workflows",
        subtitle: "Open workflow builder",
        category: "navigation",
        shortcut: "⌘2",
        icon: Workflow,
        action: () => {
          setActivePanel("workflow");
          router.push("/workflow");
          closeCommandBar();
        },
      },
      {
        id: "nav-memory",
        title: "Go to Memory",
        subtitle: "Open memory viewer",
        category: "navigation",
        shortcut: "⌘3",
        icon: Brain,
        action: () => {
          setActivePanel("memory");
          router.push("/memory");
          closeCommandBar();
        },
      },
      {
        id: "nav-settings",
        title: "Open Settings",
        subtitle: "Configure application",
        category: "navigation",
        shortcut: "⌘,",
        icon: Settings,
        action: () => {
          setActivePanel("settings");
          closeCommandBar();
        },
      },

      // Action commands
      {
        id: "action-new-chat",
        title: "New Chat",
        subtitle: "Start a new conversation",
        category: "action",
        shortcut: "⌘N",
        icon: Plus,
        action: () => {
          // Create new chat session logic here
          closeCommandBar();
        },
      },
      {
        id: "action-search-memory",
        title: "Search Memory",
        subtitle: "Search through saved memories",
        category: "action",
        shortcut: "⌘K",
        icon: Search,
        action: () => {
          setActivePanel("memory");
          router.push("/memory");
          closeCommandBar();
        },
      },
      {
        id: "action-clear-chat",
        title: "Clear Current Chat",
        subtitle: "Remove all messages",
        category: "action",
        icon: FileText,
        action: () => {
          // Clear chat logic here
          closeCommandBar();
        },
      },

      // Settings commands
      {
        id: "settings-theme",
        title: "Toggle Theme",
        subtitle: `Switch to ${theme === "dark" ? "light" : "dark"} mode`,
        category: "settings",
        shortcut: "⌘T",
        icon: Palette,
        action: () => {
          setTheme(theme === "dark" ? "light" : "dark");
          closeCommandBar();
        },
      },
      {
        id: "settings-providers",
        title: "Configure Providers",
        subtitle: "Manage AI provider settings",
        category: "settings",
        icon: Zap,
        action: () => {
          setActivePanel("settings");
          closeCommandBar();
        },
      },

      // Help commands
      {
        id: "help-shortcuts",
        title: "Keyboard Shortcuts",
        subtitle: "View all available shortcuts",
        category: "help",
        shortcut: "?",
        icon: HelpCircle,
        action: () => {
          // Show shortcuts help
          closeCommandBar();
        },
      },
    ],
    [router, setActivePanel, closeCommandBar, theme, setTheme]
  );

  // Add recent sessions to commands
  const sessionCommands: CommandItemDef[] = useMemo(
    () =>
      sessions.slice(0, 5).map((session) => ({
        id: `session-${session.id}`,
        title: session.title,
        subtitle: session.lastMessage || "No messages",
        category: "recent" as const,
        icon: History,
        action: () => {
          // Load session logic here
          addRecentCommand(`session-${session.id}`);
          closeCommandBar();
        },
      })),
    [sessions, addRecentCommand, closeCommandBar]
  );

  const handleSelect = (command: CommandItemDef) => {
    addRecentCommand(command.id);
    command.action();
  };

  // Group commands
  const groups = useMemo(() => {
    return {
      recent: sessionCommands,
      navigation: commands.filter((c) => c.category === "navigation"),
      action: commands.filter((c) => c.category === "action"),
      settings: commands.filter((c) => c.category === "settings"),
      help: commands.filter((c) => c.category === "help"),
    };
  }, [commands, sessionCommands]);

  return (
    <CommandDialog open={commandBarOpen} onOpenChange={closeCommandBar}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {groups.recent.length > 0 && (
          <>
            <CommandGroup heading="Recent">
              {groups.recent.map((command) => (
                <CommandItem
                  key={command.id}
                  value={`${command.title} ${command.subtitle}`}
                  onSelect={() => handleSelect(command)}>
                  <command.icon className="mr-2 h-4 w-4" />
                  <span>{command.title}</span>
                  {command.shortcut && (
                    <CommandShortcut>{command.shortcut}</CommandShortcut>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        <CommandGroup heading="Navigation">
          {groups.navigation.map((command) => (
            <CommandItem
              key={command.id}
              value={`${command.title} ${command.subtitle}`}
              onSelect={() => handleSelect(command)}>
              <command.icon className="mr-2 h-4 w-4" />
              <span>{command.title}</span>
              {command.shortcut && (
                <CommandShortcut>{command.shortcut}</CommandShortcut>
              )}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          {groups.action.map((command) => (
            <CommandItem
              key={command.id}
              value={`${command.title} ${command.subtitle}`}
              onSelect={() => handleSelect(command)}>
              <command.icon className="mr-2 h-4 w-4" />
              <span>{command.title}</span>
              {command.shortcut && (
                <CommandShortcut>{command.shortcut}</CommandShortcut>
              )}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Settings">
          {groups.settings.map((command) => (
            <CommandItem
              key={command.id}
              value={`${command.title} ${command.subtitle}`}
              onSelect={() => handleSelect(command)}>
              <command.icon className="mr-2 h-4 w-4" />
              <span>{command.title}</span>
              {command.shortcut && (
                <CommandShortcut>{command.shortcut}</CommandShortcut>
              )}
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Help">
          {groups.help.map((command) => (
            <CommandItem
              key={command.id}
              value={`${command.title} ${command.subtitle}`}
              onSelect={() => handleSelect(command)}>
              <command.icon className="mr-2 h-4 w-4" />
              <span>{command.title}</span>
              {command.shortcut && (
                <CommandShortcut>{command.shortcut}</CommandShortcut>
              )}
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
