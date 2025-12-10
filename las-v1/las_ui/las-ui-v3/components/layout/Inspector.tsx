"use client";

import { useAppStore } from "@/app/store";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Brain,
  Workflow,
  FileText,
  Settings,
  Search,
  Filter,
  Download,
  Upload,
  Plus,
  Eye,
  EyeOff,
} from "lucide-react";
import { useState } from "react";
import { formatRelativeTime } from "@/lib/utils";

export function Inspector() {
  const { inspectorTab, setInspectorTab, inspectorExpanded, toggleInspector } =
    useAppStore();
  const [searchQuery, setSearchQuery] = useState("");

  if (!inspectorExpanded) {
    return (
      <div className="w-12 glass-panel border-l border-border flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleInspector}
          className="p-2"
          title="Expand Inspector">
          <Eye className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="w-80 glass-panel border-l border-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h3 className="font-semibold">Inspector</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleInspector}
          className="p-1 h-6 w-6"
          title="Collapse Inspector">
          <EyeOff className="w-4 h-4" />
        </Button>
      </div>

      {/* Tabs */}
      <Tabs
        value={inspectorTab}
        onValueChange={(value) =>
          setInspectorTab(
            value as "memory" | "workflow" | "artifacts" | "settings"
          )
        }
        className="flex-1 flex flex-col">
        <TabsList className="w-full justify-start rounded-none border-b border-border p-0 h-10">
          <TabsTrigger
            value="memory"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
            <Brain className="w-4 h-4 mr-2" />
            Memory
          </TabsTrigger>
          <TabsTrigger
            value="workflow"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
            <Workflow className="w-4 h-4 mr-2" />
            Workflow
          </TabsTrigger>
          <TabsTrigger
            value="artifacts"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
            <FileText className="w-4 h-4 mr-2" />
            Artifacts
          </TabsTrigger>
          <TabsTrigger
            value="settings"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Search Bar */}
        <div className="p-3 border-b border-border">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder={`Search ${inspectorTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm bg-background border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Tab Content */}
        <ScrollArea className="flex-1">
          <TabsContent value="memory" className="mt-0 p-4 space-y-4">
            <MemoryTab searchQuery={searchQuery} />
          </TabsContent>

          <TabsContent value="workflow" className="mt-0 p-4 space-y-4">
            <WorkflowTab searchQuery={searchQuery} />
          </TabsContent>

          <TabsContent value="artifacts" className="mt-0 p-4 space-y-4">
            <ArtifactsTab searchQuery={searchQuery} />
          </TabsContent>

          <TabsContent value="settings" className="mt-0 p-4 space-y-4">
            <SettingsTab searchQuery={searchQuery} />
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  );
}

function MemoryTab({ searchQuery }: { searchQuery: string }) {
  const mockMemories = [
    {
      id: "1",
      title: "User Preferences",
      content: "User prefers dark mode and compact layout",
      timestamp: new Date("2024-03-10T10:00:00"),
      tags: ["preferences", "ui"],
    },
    {
      id: "2",
      title: "API Documentation",
      content: "REST API endpoints for user management",
      timestamp: new Date("2024-03-09T14:30:00"),
      tags: ["api", "documentation"],
    },
    {
      id: "3",
      title: "Project Context",
      content: "Current project is a chat interface for AI agents",
      timestamp: new Date("2024-03-08T09:15:00"),
      tags: ["project", "context"],
    },
  ];

  const filteredMemories = mockMemories.filter(
    (memory) =>
      memory.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.tags.some((tag) =>
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      )
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Recent Memories</h4>
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2">
            <Filter className="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2">
            <Plus className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {filteredMemories.map((memory) => (
        <div
          key={memory.id}
          className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer">
          <div className="flex items-start justify-between mb-2">
            <h5 className="text-sm font-medium">{memory.title}</h5>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(memory.timestamp)}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
            {memory.content}
          </p>
          <div className="flex gap-1 flex-wrap">
            {memory.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      ))}

      {filteredMemories.length === 0 && (
        <div className="text-center text-sm text-muted-foreground py-8">
          {`No memories found matching "${searchQuery}"`}
        </div>
      )}
    </div>
  );
}

function WorkflowTab({ searchQuery }: { searchQuery: string }) {
  const { workflows } = useAppStore();

  const filteredWorkflows = workflows.filter((workflow) =>
    workflow.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Recent Workflows</h4>
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2">
            <Plus className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {filteredWorkflows.map((workflow) => (
        <div
          key={workflow.id}
          className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer">
          <div className="flex items-start justify-between mb-2">
            <h5 className="text-sm font-medium">{workflow.name}</h5>
            <Badge
              variant={
                workflow.status === "active"
                  ? "default"
                  : workflow.status === "completed"
                  ? "secondary"
                  : "outline"
              }
              className="text-xs">
              {workflow.status}
            </Badge>
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{workflow.nodes.length} nodes</span>
            <span>
              {workflow.lastRun
                ? formatRelativeTime(new Date(workflow.lastRun))
                : "Never run"}
            </span>
          </div>
        </div>
      ))}

      {filteredWorkflows.length === 0 && (
        <div className="text-center text-sm text-muted-foreground py-8">
          {workflows.length === 0
            ? "No workflows created yet"
            : `No workflows found matching "${searchQuery}"`}
        </div>
      )}
    </div>
  );
}

function ArtifactsTab({ searchQuery }: { searchQuery: string }) {
  const mockArtifacts = [
    {
      id: "1",
      name: "generated-code.js",
      type: "code",
      size: "2.3 KB",
      created: new Date("2024-03-10T10:15:00"),
    },
    {
      id: "2",
      name: "summary-report.md",
      type: "document",
      size: "1.1 KB",
      created: new Date("2024-03-10T09:45:00"),
    },
    {
      id: "3",
      name: "data-analysis.csv",
      type: "data",
      size: "5.7 KB",
      created: new Date("2024-03-10T08:00:00"),
    },
  ];

  const filteredArtifacts = mockArtifacts.filter((artifact) =>
    artifact.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Recent Artifacts</h4>
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" className="h-6 px-2">
            <Download className="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="sm" className="h-6 px-2">
            <Upload className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {filteredArtifacts.map((artifact) => (
        <div
          key={artifact.id}
          className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer">
          <div className="flex items-start justify-between mb-2">
            <h5 className="text-sm font-medium">{artifact.name}</h5>
            <Badge variant="outline" className="text-xs">
              {artifact.type}
            </Badge>
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{artifact.size}</span>
            <span>{formatRelativeTime(artifact.created)}</span>
          </div>
        </div>
      ))}

      {filteredArtifacts.length === 0 && (
        <div className="text-center text-sm text-muted-foreground py-8">
          {`No artifacts found matching "${searchQuery}"`}
        </div>
      )}
    </div>
  );
}

function SettingsTab({ searchQuery }: { searchQuery: string }) {
  const { theme, selectedModel, providers } = useAppStore();

  const settings = [
    {
      id: "1",
      name: "Theme",
      description: `${
        theme.charAt(0).toUpperCase() + theme.slice(1)
      } mode enabled`,
      category: "appearance",
    },
    {
      id: "2",
      name: "Model",
      description: `${selectedModel} selected`,
      category: "ai",
    },
    ...Object.entries(providers).map(([key, config]) => ({
      id: `provider-${key}`,
      name: config.name,
      description: config.enabled ? "Enabled" : "Disabled",
      category: "provider",
    })),
  ];

  const filteredSettings = settings.filter(
    (setting) =>
      setting.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      setting.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Quick Settings</h4>
      </div>

      {filteredSettings.map((setting) => (
        <div
          key={setting.id}
          className="p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors">
          <div className="flex items-center justify-between mb-1">
            <h5 className="text-sm font-medium">{setting.name}</h5>
            <Badge variant="outline" className="text-xs">
              {setting.category}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">{setting.description}</p>
        </div>
      ))}

      {filteredSettings.length === 0 && (
        <div className="text-center text-sm text-muted-foreground py-8">
          No settings found matching &quot;{searchQuery}&quot;
        </div>
      )}
    </div>
  );
}
