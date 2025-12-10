"use client";

import { useState, useMemo } from "react";
import {
  MemoryGraph,
  MemoryNode,
  MemoryLink,
  MemoryGraphData,
} from "@/components/memory/MemoryGraph";
import { NodeDetails } from "@/components/memory/NodeDetails";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Filter,
  Download,
  Upload,
  Plus,
  LayoutGrid,
  List,
  Brain,
  Network,
  Zap,
} from "lucide-react";
import { formatRelativeTime, cn } from "@/lib/utils";

// Mock data for demonstration
const mockNodes: MemoryNode[] = [
  {
    id: "1",
    label: "Artificial Intelligence",
    type: "concept",
    category: "Technology",
    importance: 0.9,
    confidence: 0.95,
    timestamp: new Date("2024-01-15"),
    metadata: {
      description:
        "The simulation of human intelligence in machines that are programmed to think and learn.",
      source: "Wikipedia",
      tags: ["technology", "machine-learning", "future"],
      properties: {
        "First Mentioned": "1956",
        Field: "Computer Science",
        Applications: "Healthcare, Finance, Transportation",
      },
    },
  },
  {
    id: "2",
    label: "Machine Learning",
    type: "concept",
    category: "Technology",
    importance: 0.85,
    confidence: 0.92,
    timestamp: new Date("2024-01-16"),
    metadata: {
      description:
        "A subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
      tags: ["AI", "algorithms", "data-science"],
      properties: {
        Type: "Supervised, Unsupervised, Reinforcement",
        Algorithms: "Neural Networks, Decision Trees, SVM",
      },
    },
  },
  {
    id: "3",
    label: "Neural Networks",
    type: "concept",
    category: "Technology",
    importance: 0.8,
    confidence: 0.88,
    timestamp: new Date("2024-01-17"),
    metadata: {
      description:
        "Computing systems inspired by the biological neural networks that constitute animal brains.",
      tags: ["AI", "deep-learning", "brain-inspired"],
      properties: {
        Layers: "Input, Hidden, Output",
        Training: "Backpropagation",
        Types: "CNN, RNN, Transformer",
      },
    },
  },
  {
    id: "4",
    label: "Deep Learning",
    type: "concept",
    category: "Technology",
    importance: 0.82,
    confidence: 0.9,
    timestamp: new Date("2024-01-18"),
    metadata: {
      description:
        "Part of machine learning based on artificial neural networks with representation learning.",
      tags: ["AI", "neural-networks", "advanced"],
      properties: {
        Architecture: "Multi-layer Neural Networks",
        "Use Cases": "Image Recognition, NLP, Speech",
      },
    },
  },
  {
    id: "5",
    label: "Natural Language Processing",
    type: "concept",
    category: "Technology",
    importance: 0.78,
    confidence: 0.87,
    timestamp: new Date("2024-01-19"),
    metadata: {
      description:
        "A subfield of AI focused on the interaction between computers and humans through natural language.",
      tags: ["AI", "language", "text-processing"],
      properties: {
        Tasks: "Translation, Sentiment Analysis, Chatbots",
        Models: "BERT, GPT, T5",
      },
    },
  },
  {
    id: "6",
    label: "Computer Vision",
    type: "concept",
    category: "Technology",
    importance: 0.75,
    confidence: 0.85,
    timestamp: new Date("2024-01-20"),
    metadata: {
      description:
        "Field of AI that trains computers to interpret and understand the visual world.",
      tags: ["AI", "images", "perception"],
      properties: {
        Applications: "Object Detection, Face Recognition, Medical Imaging",
        Techniques: "CNN, YOLO, R-CNN",
      },
    },
  },
];

const mockLinks: MemoryLink[] = [
  {
    source: "1",
    target: "2",
    type: "related",
    strength: 0.9,
    label: "subset of",
  },
  { source: "2", target: "3", type: "related", strength: 0.85, label: "uses" },
  { source: "3", target: "4", type: "causes", strength: 0.8, label: "enables" },
  {
    source: "1",
    target: "5",
    type: "related",
    strength: 0.75,
    label: "includes",
  },
  {
    source: "1",
    target: "6",
    type: "related",
    strength: 0.7,
    label: "includes",
  },
  {
    source: "4",
    target: "5",
    type: "related",
    strength: 0.65,
    label: "applies to",
  },
  {
    source: "4",
    target: "6",
    type: "related",
    strength: 0.6,
    label: "applies to",
  },
];

interface MemoryPageProps {
  className?: string;
}

export default function MemoryPage({ className = "" }: MemoryPageProps) {
  const [selectedNode, setSelectedNode] = useState<MemoryNode | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"graph" | "list">("graph");
  const [showImportance, setShowImportance] = useState(true);
  const [showConfidence, setShowConfidence] = useState(true);

  // Filter nodes based on search and category
  const filteredNodes = useMemo(() => {
    return mockNodes.filter((node) => {
      const matchesSearch =
        node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.metadata?.description
          ?.toLowerCase()
          .includes(searchQuery.toLowerCase()) ||
        node.metadata?.tags?.some((tag) =>
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        );

      const matchesCategory =
        selectedCategory === "all" || node.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  // Filter links based on filtered nodes
  const filteredLinks = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return mockLinks.filter((link) => {
      const sourceId =
        typeof link.source === "string" ? link.source : link.source.id;
      const targetId =
        typeof link.target === "string" ? link.target : link.target.id;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
  }, [filteredNodes]);

  const graphData: MemoryGraphData = {
    nodes: filteredNodes,
    links: filteredLinks,
  };

  const categories = useMemo(() => {
    const cats = Array.from(new Set(mockNodes.map((n) => n.category)));
    return ["all", ...cats];
  }, []);

  const handleNodeClick = (node: MemoryNode) => {
    setSelectedNode(node);
  };

  const handleNodeUpdate = (nodeId: string, updates: Partial<MemoryNode>) => {
    // In a real app, this would update the backend
    console.log("Updating node:", nodeId, updates);
  };

  const handleNodeDelete = (nodeId: string) => {
    // In a real app, this would delete from the backend
    console.log("Deleting node:", nodeId);
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null);
    }
  };

  const getRelatedNodes = (nodeId: string) => {
    const relatedIds = new Set<string>();
    mockLinks.forEach((link) => {
      const sourceId =
        typeof link.source === "string" ? link.source : link.source.id;
      const targetId =
        typeof link.target === "string" ? link.target : link.target.id;

      if (sourceId === nodeId) relatedIds.add(targetId);
      if (targetId === nodeId) relatedIds.add(sourceId);
    });

    return mockNodes.filter((n) => relatedIds.has(n.id));
  };

  const getRelatedLinks = (nodeId: string) => {
    return mockLinks.filter((link) => {
      const sourceId =
        typeof link.source === "string" ? link.source : link.source.id;
      const targetId =
        typeof link.target === "string" ? link.target : link.target.id;
      return sourceId === nodeId || targetId === nodeId;
    });
  };

  return (
    <div className={cn("flex h-full bg-background", className)}>
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center gap-3">
              <Brain className="w-5 h-5 text-primary" />
              <h1 className="text-xl font-semibold">Memory Graph</h1>
              <Badge variant="secondary" className="text-xs">
                {filteredNodes.length} nodes, {filteredLinks.length} connections
              </Badge>
            </div>

            <div className="flex items-center gap-2">
              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search nodes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 text-sm border rounded-md bg-background">
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === "all" ? "All Categories" : category}
                  </option>
                ))}
              </select>

              {/* View Toggle */}
              <div className="flex border rounded-md overflow-hidden">
                <Button
                  size="sm"
                  variant={viewMode === "graph" ? "default" : "ghost"}
                  onClick={() => setViewMode("graph")}
                  className="rounded-none">
                  <Network className="w-4 h-4" />
                </Button>
                <Button
                  size="sm"
                  variant={viewMode === "list" ? "default" : "ghost"}
                  onClick={() => setViewMode("list")}
                  className="rounded-none">
                  <LayoutGrid className="w-4 h-4" />
                </Button>
              </div>

              {/* Actions */}
              <Button size="sm" variant="outline">
                <Upload className="w-4 h-4 mr-1" />
                Import
              </Button>
              <Button size="sm" variant="outline">
                <Download className="w-4 h-4 mr-1" />
                Export
              </Button>
              <Button size="sm">
                <Plus className="w-4 h-4 mr-1" />
                Add Node
              </Button>
            </div>
          </div>

          {/* Visualization Controls */}
          <div className="px-4 pb-3 flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-muted-foreground">Show:</label>
              <label className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={showImportance}
                  onChange={(e) => setShowImportance(e.target.checked)}
                  className="rounded"
                />
                Importance
              </label>
              <label className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={showConfidence}
                  onChange={(e) => setShowConfidence(e.target.checked)}
                  className="rounded"
                />
                Confidence
              </label>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 relative">
          {viewMode === "graph" ? (
            <MemoryGraph
              data={graphData}
              width={1200}
              height={800}
              onNodeClick={handleNodeClick}
              selectedNodeId={selectedNode?.id}
              showLabels={true}
              showLegend={true}
            />
          ) : (
            <ScrollArea className="h-full">
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredNodes.map((node) => (
                    <Card
                      key={node.id}
                      className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => handleNodeClick(node)}>
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor: `hsl(${
                                node.type === "concept"
                                  ? 220
                                  : node.type === "entity"
                                  ? 140
                                  : node.type === "relation"
                                  ? 35
                                  : node.type === "event"
                                  ? 0
                                  : node.type === "document"
                                  ? 270
                                  : 180
                              }, 70%, 50%)`,
                            }}
                          />
                          <h3 className="font-medium">{node.label}</h3>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {node.type}
                        </Badge>
                      </div>
                      {node.metadata?.description && (
                        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                          {node.metadata.description}
                        </p>
                      )}
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{formatRelativeTime(node.timestamp)}</span>
                        <div className="flex items-center gap-2">
                          <span>
                            Importance: {(node.importance * 100).toFixed(0)}%
                          </span>
                          <span>
                            Confidence: {(node.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </ScrollArea>
          )}
        </div>
      </div>

      {/* Node Details Sidebar */}
      {selectedNode && (
        <div className="w-96 border-l bg-background">
          <NodeDetails
            node={selectedNode}
            relatedNodes={getRelatedNodes(selectedNode.id)}
            relatedLinks={getRelatedLinks(selectedNode.id)}
            onClose={() => setSelectedNode(null)}
            onUpdateNode={handleNodeUpdate}
            onDeleteNode={handleNodeDelete}
          />
        </div>
      )}
    </div>
  );
}
