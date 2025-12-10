"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { ZoomBehavior, ZoomTransform } from "d3";
import {
  Brain,
  Circle,
  Square,
  Triangle,
  Diamond,
  Hexagon,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface MemoryNode {
  id: string;
  label: string;
  type: "concept" | "entity" | "relation" | "event" | "document" | "task";
  category: string;
  importance: number; // 0-1
  confidence: number; // 0-1
  timestamp: Date;
  metadata?: {
    description?: string;
    source?: string;
    tags?: string[];
    properties?: Record<string, unknown>;
  };
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface MemoryLink {
  source: string | MemoryNode;
  target: string | MemoryNode;
  type:
    | "related"
    | "causes"
    | "part-of"
    | "similar"
    | "opposite"
    | "temporal"
    | "semantic";
  strength: number; // 0-1
  label?: string;
  metadata?: {
    confidence?: number;
    evidence?: string[];
    timestamp?: Date;
  };
}

export interface MemoryGraphData {
  nodes: MemoryNode[];
  links: MemoryLink[];
}

interface MemoryGraphProps {
  data: MemoryGraphData;
  width?: number;
  height?: number;
  className?: string;
  onNodeClick?: (node: MemoryNode) => void;
  onNodeHover?: (node: MemoryNode | null) => void;
  onLinkClick?: (link: MemoryLink) => void;
  selectedNodeId?: string;
  showLabels?: boolean;
  showLegend?: boolean;
  enableZoom?: boolean;
  enablePan?: boolean;
  nodeSize?: number;
  linkDistance?: number;
  chargeStrength?: number;
}

export function MemoryGraph({
  data,
  width = 800,
  height = 600,
  className = "",
  onNodeClick,
  onNodeHover,
  onLinkClick,
  selectedNodeId,
  showLabels = true,
  showLegend = true,
  enableZoom = true,
  enablePan = true,
  nodeSize = 20,
  linkDistance = 100,
  chargeStrength = -300,
}: MemoryGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<MemoryNode | null>(null);
  const [transform, setTransform] = useState<ZoomTransform>(d3.zoomIdentity);
  const simulationRef = useRef<d3.Simulation<MemoryNode, MemoryLink> | null>(
    null
  );

  // Get node icon based on type
  const getNodeIcon = (type: MemoryNode["type"]) => {
    switch (type) {
      case "concept":
        return Brain;
      case "entity":
        return Circle;
      case "relation":
        return Diamond;
      case "event":
        return Triangle;
      case "document":
        return Square;
      case "task":
        return Hexagon;
      default:
        return Circle;
    }
  };

  // Get node color based on type and importance
  const getNodeColor = (type: MemoryNode["type"], importance: number) => {
    const baseColors = {
      concept: "#3b82f6", // blue
      entity: "#10b981", // green
      relation: "#f59e0b", // amber
      event: "#ef4444", // red
      document: "#8b5cf6", // purple
      task: "#06b6d4", // cyan
    };

    const baseColor = baseColors[type] || "#6b7280";

    // Adjust color based on importance (opacity)
    const opacity = 0.4 + importance * 0.6;
    return d3.color(baseColor)?.copy({ opacity }).toString() || baseColor;
  };

  // Get link color based on type
  const getLinkColor = (type: MemoryLink["type"]) => {
    const colors = {
      related: "#6b7280",
      causes: "#ef4444",
      "part-of": "#10b981",
      similar: "#3b82f6",
      opposite: "#f59e0b",
      temporal: "#8b5cf6",
      semantic: "#06b6d4",
    };
    return colors[type] || "#6b7280";
  };

  // Initialize and run simulation
  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    const g = svg.select<SVGGElement>("g");

    // Clear previous simulation
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    // Set up zoom behavior
    const zoom: ZoomBehavior<SVGSVGElement, unknown> = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 10])
      .on("zoom", (event) => {
        setTransform(event.transform);
      });

    if (enableZoom) {
      svg.call(zoom);
    }

    // Create simulation
    const simulation = d3
      .forceSimulation<MemoryNode>(data.nodes)
      .force(
        "link",
        d3
          .forceLink<MemoryNode, MemoryLink>(data.links)
          .id((d) => d.id)
          .distance(linkDistance)
          .strength((d) => d.strength || 0.5)
      )
      .force("charge", d3.forceManyBody().strength(chargeStrength))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(nodeSize + 5))
      .alphaDecay(0.05)
      .alphaMin(0.1);

    simulationRef.current = simulation;

    // Create links
    const link = g
      .selectAll(".link")
      .data(data.links)
      .join("line")
      .attr("class", "link")
      .attr("stroke", (d) => getLinkColor(d.type))
      .attr("stroke-width", (d) => d.strength * 3 + 1)
      .attr("stroke-opacity", (d) => d.strength * 0.7 + 0.3)
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        event.stopPropagation();
        onLinkClick?.(d);
      });

    // Create nodes
    const node = g
      .selectAll(".node")
      .data(data.nodes)
      .join("g")
      .attr("class", "node")
      .style("cursor", "pointer");

    if (enablePan) {
      node.call(
        d3
          .drag<SVGGElement, MemoryNode>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x ?? event.x;
            d.fy = d.y ?? event.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );
    }

    // Add node circles
    node
      .append("circle")
      .attr("r", (d) => nodeSize + d.importance * 10)
      .attr("fill", (d) => getNodeColor(d.type, d.importance))
      .attr("stroke", (d) => (selectedNodeId === d.id ? "#f59e0b" : "white"))
      .attr("stroke-width", (d) => (selectedNodeId === d.id ? 3 : 1))
      .attr("stroke-opacity", (d) => (selectedNodeId === d.id ? 1 : 0.8));

    // Removed icon text (unused variable and ineffective rendering)

    // Add labels
    if (showLabels) {
      node
        .append("text")
        .attr("class", "label")
        .attr("text-anchor", "middle")
        .attr("dy", nodeSize + 20)
        .attr("font-size", "12px")
        .attr("fill", "#374151")
        .text((d) =>
          d.label.length > 15 ? d.label.substring(0, 15) + "..." : d.label
        );
    }

    // Add hover effects
    node
      .on("mouseenter", (_, d) => {
        setHoveredNode(d);
        onNodeHover?.(d);

        // Highlight connected nodes
        const connectedNodeIds = new Set<string>();
        data.links.forEach((link) => {
          if (
            typeof link.source === "string" &&
            typeof link.target === "string"
          ) {
            if (link.source === d.id) connectedNodeIds.add(link.target);
            if (link.target === d.id) connectedNodeIds.add(link.source);
          }
        });

        node
          .selectAll("circle")
          .attr("opacity", (nodeData) =>
            nodeData.id === d.id || connectedNodeIds.has(nodeData.id) ? 1 : 0.3
          );

        link.attr("opacity", (linkData) => {
          const sourceId =
            typeof linkData.source === "string"
              ? linkData.source
              : linkData.source.id;
          const targetId =
            typeof linkData.target === "string"
              ? linkData.target
              : linkData.target.id;
          return sourceId === d.id || targetId === d.id ? 1 : 0.1;
        });
      })
      .on("mouseleave", () => {
        setHoveredNode(null);
        onNodeHover?.(null);

        // Reset opacity
        node.selectAll("circle").attr("opacity", 1);
        link.attr("opacity", (linkData) => linkData.strength * 0.7 + 0.3);
      })
      .on("click", (event, d) => {
        event.stopPropagation();
        onNodeClick?.(d);
      });

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as MemoryNode).x!)
        .attr("y1", (d) => (d.source as MemoryNode).y!)
        .attr("x2", (d) => (d.target as MemoryNode).x!)
        .attr("y2", (d) => (d.target as MemoryNode).y!);

      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    // Cleanup
    return () => {
      simulation.stop();
      svg.on(".zoom", null);
    };
  }, [
    data,
    width,
    height,
    nodeSize,
    linkDistance,
    chargeStrength,
    showLabels,
    selectedNodeId,
    onNodeClick,
    onNodeHover,
    onLinkClick,
    enableZoom,
    enablePan,
  ]);

  return (
    <div className={cn("relative bg-background", className)} ref={containerRef}>
      <svg ref={svgRef} width={width} height={height} className="w-full h-full">
        <g transform={transform.toString()} />
      </svg>

      {/* Legend */}
      {showLegend && (
        <div className="absolute top-4 right-4 bg-background/90 backdrop-blur-sm rounded-lg border p-3 space-y-2">
          <h4 className="text-sm font-semibold">Node Types</h4>
          <div className="space-y-1 text-xs">
            {["concept", "entity", "relation", "event", "document", "task"].map(
              (type) => {
                const Icon = getNodeIcon(type as MemoryNode["type"]);
                return (
                  <div key={type} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{
                        backgroundColor: getNodeColor(
                          type as MemoryNode["type"],
                          0.8
                        ),
                      }}
                    />
                    <Icon className="w-3 h-3" />
                    <span className="capitalize">{type}</span>
                  </div>
                );
              }
            )}
          </div>
        </div>
      )}

      {/* Node Info */}
      {hoveredNode && (
        <div className="absolute bottom-4 left-4 bg-background/90 backdrop-blur-sm rounded-lg border p-3 max-w-xs">
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-4 h-4 rounded-full"
              style={{
                backgroundColor: getNodeColor(
                  hoveredNode.type,
                  hoveredNode.importance
                ),
              }}
            />
            <h4 className="font-semibold text-sm">{hoveredNode.label}</h4>
            <Badge variant="outline" className="text-xs">
              {hoveredNode.type}
            </Badge>
          </div>
          {hoveredNode.metadata?.description && (
            <p className="text-xs text-muted-foreground mb-2">
              {hoveredNode.metadata.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>
              Importance: {(hoveredNode.importance * 100).toFixed(0)}%
            </span>
            <span>
              Confidence: {(hoveredNode.confidence * 100).toFixed(0)}%
            </span>
          </div>
          {hoveredNode.metadata?.tags &&
            hoveredNode.metadata.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {hoveredNode.metadata.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
        </div>
      )}
    </div>
  );
}
