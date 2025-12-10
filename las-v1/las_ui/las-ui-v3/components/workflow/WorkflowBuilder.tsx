"use client";

import { useCallback, useState, useRef } from "react";
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  NodeTypes,
  OnConnect,
} from "reactflow";
import type { ReactFlowInstance } from "reactflow";
import "reactflow/dist/style.css";
import { Save, Play, Loader2 } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "@/components/ui/input";
import { NodePalette } from "./NodePalette";
import { NodeInspector } from "./NodeInspector";
import { toast } from "sonner";
import { useAppStore } from "@/app/store";
import { Badge } from "@/components/ui/badge";

// Custom node component
type NodeData = { label: string; type: string };
type EdgeData = { label?: string };

function CustomNode({ data }: { data: NodeData }) {
  const typeColors: Record<string, string> = {
    trigger: "border-accent bg-accent/10",
    action: "border-primary bg-primary/10",
    condition: "border-warning bg-warning/10",
    output: "border-success bg-success/10",
  };

  return (
    <div
      className={`px-4 py-3 rounded-lg border-2 ${
        typeColors[data.type] || "border-border bg-zinc-900/50"
      } min-w-32 bg-card`}>
      <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">
        {data.type}
      </div>
      <div className="text-sm font-medium">{data.label}</div>
    </div>
  );
}

const nodeTypes: NodeTypes = {
  custom: CustomNode,
  trigger: CustomNode,
  action: CustomNode,
  condition: CustomNode,
  output: CustomNode,
};

const initialNodes: Node<NodeData>[] = [
  {
    id: "1",
    type: "trigger",
    position: { x: 100, y: 100 },
    data: { label: "User Input", type: "trigger" },
  },
];

const initialEdges: Edge<EdgeData>[] = [];

export function WorkflowBuilder() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, onNodesChange] =
    useNodesState<NodeData>(initialNodes);
  const [edges, setEdges, onEdgesChange] =
    useEdgesState<EdgeData>(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const { addWorkflow, updateWorkflow } = useAppStore();
  const [savedWorkflowId, setSavedWorkflowId] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState<string>("Untitled Workflow");

  const onConnect: OnConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current || !reactFlowInstance) return;

      const type = event.dataTransfer.getData("application/reactflow/type");
      const label = event.dataTransfer.getData("application/reactflow/label");

      if (typeof type === "undefined" || !type) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node<NodeData> = {
        id: `${Date.now()}`,
        type: type,
        position,
        data: { label: label, type: type },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  const handleUpdateNode = useCallback(
    (id: string, data: Partial<NodeData>) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === id) {
            return {
              ...node,
              data: {
                ...node.data,
                ...data,
              },
            };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  const saveWorkflow = async () => {
    setIsSaving(true);
    try {
      const id = `wf-${Date.now()}`;
      const workflow = {
        id,
        name: workflowName.trim() || "Untitled Workflow",
        nodes,
        edges,
        status: "draft" as const,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      addWorkflow(workflow);
      setSavedWorkflowId(id);
      console.log("Saving workflow:", workflow);
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast.success("Workflow saved successfully");
    } catch (error) {
      toast.error("Failed to save workflow");
    } finally {
      setIsSaving(false);
    }
  };

  const runWorkflow = async () => {
    setIsRunning(true);
    try {
      console.log("Running workflow with", nodes.length, "nodes");
      const start = performance.now();
      // Simulate execution
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const duration = performance.now() - start;
      if (savedWorkflowId) {
        updateWorkflow(savedWorkflowId, {
          lastRun: new Date(),
          status: "active",
          lastRunDurationMs: Math.round(duration),
          lastRunStatus: "success",
        });
      }
      toast.success("Workflow execution started");
    } catch (error) {
      toast.error("Failed to start workflow");
    } finally {
      setIsRunning(false);
    }
  };

  const selectedNode: Node<NodeData> | null =
    nodes.find((n) => n.id === selectedNodeId) || null;

  return (
    <div className="flex h-full w-full bg-background">
      {/* Sidebar Palette */}
      <div className="w-64 border-r flex-shrink-0 bg-card z-10">
        <NodePalette />
        <div className="border-t p-3">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium">Recent Workflows</h4>
            <Badge variant="outline" className="text-xs">
              {useAppStore.getState().workflows.length}
            </Badge>
          </div>
          <div className="space-y-2">
            {useAppStore
              .getState()
              .workflows.slice(0, 6)
              .map((wf) => (
                <div
                  key={wf.id}
                  className="p-2 rounded border hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs font-medium line-clamp-1">
                        {wf.name}
                      </div>
                      <div className="text-[10px] text-muted-foreground">
                        {wf.nodes.length} nodes • {wf.status}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 px-2"
                      onClick={() => {
                        setNodes(wf.nodes as Node<NodeData>[]);
                        setEdges(wf.edges as Edge<EdgeData>[]);
                        setSavedWorkflowId(wf.id);
                        setWorkflowName(wf.name);
                      }}>
                      Load
                    </Button>
                  </div>
                </div>
              ))}
            {useAppStore.getState().workflows.length === 0 && (
              <div className="text-xs text-muted-foreground">
                No saved workflows
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Canvas */}
      <div className="flex-1 relative h-full" ref={reactFlowWrapper}>
        <div className="absolute top-4 right-4 z-10 flex gap-2">
          <Input
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            placeholder="Workflow name"
            className="w-48"
          />
          <Button
            size="sm"
            variant="outline"
            onClick={saveWorkflow}
            disabled={isSaving}>
            {isSaving ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save
          </Button>
          <Button size="sm" onClick={runWorkflow} disabled={isRunning}>
            {isRunning ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            Run
          </Button>
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView>
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      {/* Right Inspector */}
      <div className="w-80 border-l flex-shrink-0 bg-card z-10">
        <NodeInspector
          selectedNode={selectedNode}
          onUpdateNode={handleUpdateNode}
        />
      </div>
    </div>
  );
}
