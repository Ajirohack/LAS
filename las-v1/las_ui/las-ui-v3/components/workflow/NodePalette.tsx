"use client";

import { DragEvent } from "react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Zap,
  GitBranch,
  CheckCircle,
  MessageSquare,
  Database,
  Globe,
  Code,
  Search,
} from "lucide-react";
import { useState } from "react";

const nodeTypes = [
  {
    category: "Triggers",
    items: [
      {
        type: "trigger",
        label: "User Input",
        icon: MessageSquare,
        description: "Starts flow on user message",
      },
      {
        type: "trigger",
        label: "Webhook",
        icon: Globe,
        description: "Starts flow on external request",
      },
    ],
  },
  {
    category: "Actions",
    items: [
      {
        type: "action",
        label: "LLM Process",
        icon: Zap,
        description: "Process text with AI model",
      },
      {
        type: "action",
        label: "Search",
        icon: Search,
        description: "Search knowledge base or web",
      },
      {
        type: "action",
        label: "Code Execute",
        icon: Code,
        description: "Run Python/JS code",
      },
      {
        type: "action",
        label: "Database",
        icon: Database,
        description: "Query or store data",
      },
    ],
  },
  {
    category: "Logic",
    items: [
      {
        type: "condition",
        label: "If/Else",
        icon: GitBranch,
        description: "Branch based on conditions",
      },
    ],
  },
  {
    category: "Outputs",
    items: [
      {
        type: "output",
        label: "Response",
        icon: MessageSquare,
        description: "Send reply to user",
      },
      {
        type: "output",
        label: "End",
        icon: CheckCircle,
        description: "End workflow execution",
      },
    ],
  },
];

export function NodePalette() {
  const [search, setSearch] = useState("");

  const onDragStart = (event: DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData("application/reactflow/type", nodeType);
    event.dataTransfer.setData("application/reactflow/label", label);
    event.dataTransfer.effectAllowed = "move";
  };

  const filteredNodes = nodeTypes
    .map((category) => ({
      ...category,
      items: category.items.filter(
        (item) =>
          item.label.toLowerCase().includes(search.toLowerCase()) ||
          item.description.toLowerCase().includes(search.toLowerCase())
      ),
    }))
    .filter((category) => category.items.length > 0);

  return (
    <Card className="h-full border-r rounded-none border-0">
      <CardHeader className="p-4 border-b">
        <CardTitle className="text-sm font-medium">Nodes</CardTitle>
        <div className="relative mt-2">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search nodes..."
            className="pl-8 h-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </CardHeader>
      <ScrollArea className="h-[calc(100vh-180px)]">
        <div className="p-4 space-y-6">
          {filteredNodes.map((category) => (
            <div key={category.category}>
              <h3 className="mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {category.category}
              </h3>
              <div className="grid gap-2">
                {category.items.map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center gap-3 p-3 text-sm border rounded-lg cursor-grab hover:bg-accent hover:text-accent-foreground transition-colors active:cursor-grabbing bg-card"
                    draggable
                    onDragStart={(e) => onDragStart(e, item.type, item.label)}>
                    <div className="p-2 bg-primary/10 rounded-md">
                      <item.icon className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <div className="font-medium">{item.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {item.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
}
