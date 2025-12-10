"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

interface KnowledgeNode {
  id: string;
  label: string;
  type: "entity" | "concept" | "skill" | "memory";
  connections: number;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface KnowledgeLink {
  source: string;
  target: string;
  strength: number;
}

interface MemoryViewerProps {
  nodes: KnowledgeNode[];
  links: KnowledgeLink[];
  positionsWsUrl?: string;
  persistPositions?: boolean;
  onPositionsChange?: (
    positions: Record<string, { x: number; y: number }>
  ) => void;
}

export function MemoryViewer({
  nodes,
  links,
  positionsWsUrl,
  persistPositions = true,
  onPositionsChange,
}: MemoryViewerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const positionMapRef = useRef<Map<string, { x: number; y: number }>>(
    new Map()
  );
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    svg.attr("width", width).attr("height", height);

    // Clear previous content
    svg.selectAll("*").remove();

    const useServerLayout = !!positionsWsUrl;
    let simulation: d3.Simulation<KnowledgeNode, KnowledgeLink> | null = null;

    if (!useServerLayout) {
      simulation = d3
        .forceSimulation<KnowledgeNode>(nodes)
        .force(
          "link",
          d3
            .forceLink<KnowledgeNode, KnowledgeLink>(links)
            .id((d) => d.id)
            .distance(100)
        )
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(30));
    }

    // Create container group
    const g = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom);

    // Draw links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#52525b")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d) => Math.sqrt(d.strength));

    // Color scale for node types
    const colorScale: Record<string, string> = {
      entity: "#3b82f6", // Electric Blue
      concept: "#a855f7", // Neon Purple
      skill: "#22c55e", // Success Green
      memory: "#f59e0b", // Amber
    };

    if (persistPositions) {
      nodes.forEach((n) => {
        const saved = positionMapRef.current.get(n.id);
        if (saved) {
          n.x = saved.x;
          n.y = saved.y;
        }
      });
    }

    // Draw nodes
    const node = g
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", (d) => 8 + d.connections * 2)
      .attr("fill", (d) => colorScale[d.type] || "#71717a")
      .attr("stroke", "#18181b")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .call(
        d3
          .drag<SVGCircleElement, KnowledgeNode>()
          .on("start", (event, d) => {
            if (simulation && !event.active)
              simulation.alphaTarget(0.3).restart();
            d.fx = d.x ?? event.x;
            d.fy = d.y ?? event.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
            if (persistPositions) {
              positionMapRef.current.set(d.id, { x: event.x, y: event.y });
              onPositionsChange?.(Object.fromEntries(positionMapRef.current));
            }
          })
          .on("end", (event, d) => {
            if (simulation && !event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      )
      .on("click", (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
      });

    // Add labels
    const label = g
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.label)
      .attr("font-size", 10)
      .attr("fill", "#e4e4e7")
      .attr("text-anchor", "middle")
      .attr("dy", -15)
      .style("pointer-events", "none");

    const render = () => {
      link
        .attr("x1", (d) => (d as unknown as { source: KnowledgeNode }).source.x)
        .attr("y1", (d) => (d as unknown as { source: KnowledgeNode }).source.y)
        .attr("x2", (d) => (d as unknown as { target: KnowledgeNode }).target.x)
        .attr(
          "y2",
          (d) => (d as unknown as { target: KnowledgeNode }).target.y
        );

      node
        .attr("cx", (d) => (d as unknown as KnowledgeNode).x!)
        .attr("cy", (d) => (d as unknown as KnowledgeNode).y!);

      label
        .attr("x", (d) => (d as unknown as KnowledgeNode).x!)
        .attr("y", (d) => (d as unknown as KnowledgeNode).y!);

      if (persistPositions) {
        nodes.forEach((n) => {
          if (typeof n.x === "number" && typeof n.y === "number") {
            positionMapRef.current.set(n.id, { x: n.x, y: n.y });
          }
        });
        onPositionsChange?.(Object.fromEntries(positionMapRef.current));
      }
    };

    if (simulation) {
      simulation.on("tick", render);
    }

    if (useServerLayout && positionsWsUrl) {
      try {
        const ws = new WebSocket(positionsWsUrl);
        ws.onopen = () => {
          wsRef.current = ws;
        };
        ws.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            const nextPositions: Record<string, { x: number; y: number }> = {};
            if (Array.isArray(payload.positions)) {
              payload.positions.forEach(
                (p: { id: string; x: number; y: number }) => {
                  nextPositions[p.id] = { x: p.x, y: p.y };
                }
              );
            } else if (
              payload.positions &&
              typeof payload.positions === "object"
            ) {
              Object.keys(payload.positions).forEach((id) => {
                const p = payload.positions[id];
                nextPositions[id] = { x: p.x, y: p.y };
              });
            }

            nodes.forEach((n) => {
              const pos = nextPositions[n.id];
              if (pos) {
                n.x = pos.x;
                n.y = pos.y;
              }
            });
            render();
          } catch {}
        };
        ws.onclose = () => {
          wsRef.current = null;
        };
      } catch {}
    }

    svg.on("click", () => setSelectedNode(null));

    return () => {
      if (simulation) simulation.stop();
      svg.on(".zoom", null);
      svg.on("click", null);
      if (wsRef.current) {
        try {
          wsRef.current.close();
        } catch {}
        wsRef.current = null;
      }
    };
  }, [nodes, links, positionsWsUrl, persistPositions, onPositionsChange]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">Knowledge Graph</h2>
        <p className="text-xs text-foreground-muted mt-1">
          Visualizing {nodes.length} nodes and {links.length} connections
        </p>
      </div>

      {/* Graph */}
      <div className="flex-1 relative">
        <svg ref={svgRef} className="w-full h-full bg-zinc-950/30" />

        {/* Legend */}
        <div className="absolute top-4 right-4 glass-panel p-3 space-y-2">
          <div className="text-xs font-semibold mb-2">Node Types</div>
          {[
            { type: "entity", color: "#3b82f6", label: "Entity" },
            { type: "concept", color: "#a855f7", label: "Concept" },
            { type: "skill", color: "#22c55e", label: "Skill" },
            { type: "memory", color: "#f59e0b", label: "Memory" },
          ].map((item) => (
            <div key={item.type} className="flex items-center gap-2 text-xs">
              <div
                className="w-3 h-3 rounded-full border border-zinc-800"
                style={{ backgroundColor: item.color }}
              />
              <span>{item.label}</span>
            </div>
          ))}
        </div>

        {/* Selected Node Info */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 glass-panel p-4 min-w-64">
            <div className="flex items-center gap-2 mb-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{
                  backgroundColor: {
                    entity: "#3b82f6",
                    concept: "#a855f7",
                    skill: "#22c55e",
                    memory: "#f59e0b",
                  }[selectedNode.type],
                }}
              />
              <div className="text-sm font-semibold">{selectedNode.label}</div>
            </div>
            <div className="text-xs text-foreground-muted space-y-1">
              <div>
                Type:{" "}
                <span className="text-foreground capitalize">
                  {selectedNode.type}
                </span>
              </div>
              <div>
                Connections:{" "}
                <span className="text-foreground">
                  {selectedNode.connections}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 border-t border-border flex items-center justify-between text-xs text-foreground-muted">
        <div>Drag nodes to rearrange • Scroll to zoom</div>
        <div>
          {selectedNode
            ? `Selected: ${selectedNode.label}`
            : "Click a node for details"}
        </div>
      </div>
    </div>
  );
}
