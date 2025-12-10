"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Search,
  FileText,
  Cpu,
  Eye,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatRelativeTime } from "@/lib/utils";

export interface ThoughtStep {
  id: string;
  type: "reasoning" | "tool_call" | "observation" | "reflection" | "decision";
  title: string;
  content: string;
  timestamp: Date;
  duration?: number; // in milliseconds
  status: "pending" | "running" | "completed" | "error";
  tool?: {
    name: string;
    input: unknown;
    output?: unknown;
    error?: string;
  };
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
    confidence?: number;
  };
}

interface ThoughtChainProps {
  steps: ThoughtStep[];
  isActive?: boolean;
  onStepClick?: (step: ThoughtStep) => void;
  className?: string;
}

export function ThoughtChain({
  steps,
  isActive = false,
  onStepClick,
  className = "",
}: ThoughtChainProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [showDetails, setShowDetails] = useState(false);

  const toggleStep = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  const getStepIcon = (type: ThoughtStep["type"]) => {
    switch (type) {
      case "reasoning":
        return <Cpu className="w-4 h-4" />;
      case "tool_call":
        return <Zap className="w-4 h-4" />;
      case "observation":
        return <Eye className="w-4 h-4" />;
      case "reflection":
        return <Search className="w-4 h-4" />;
      case "decision":
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getStepColor = (type: ThoughtStep["type"]) => {
    switch (type) {
      case "reasoning":
        return "text-blue-500 bg-blue-50 border-blue-200";
      case "tool_call":
        return "text-purple-500 bg-purple-50 border-purple-200";
      case "observation":
        return "text-green-500 bg-green-50 border-green-200";
      case "reflection":
        return "text-orange-500 bg-orange-50 border-orange-200";
      case "decision":
        return "text-red-500 bg-red-50 border-red-200";
      default:
        return "text-gray-500 bg-gray-50 border-gray-200";
    }
  };

  const getStatusIcon = (status: ThoughtStep["status"]) => {
    switch (status) {
      case "pending":
        return <Clock className="w-3 h-3 text-gray-400 animate-pulse" />;
      case "running":
        return (
          <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        );
      case "completed":
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case "error":
        return <AlertCircle className="w-3 h-3 text-red-500" />;
      default:
        return null;
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const totalDuration = steps.reduce(
    (sum, step) => sum + (step.duration || 0),
    0
  );
  const completedSteps = steps.filter(
    (step) => step.status === "completed"
  ).length;

  return (
    <div className={`bg-card border rounded-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-primary" />
            <h3 className="font-semibold">Thought Process</h3>
          </div>
          {isActive && (
            <Badge variant="secondary" className="text-xs">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse mr-1" />
              Thinking
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span>
            {completedSteps}/{steps.length} steps
          </span>
          {totalDuration > 0 && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDuration(totalDuration)}
            </span>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDetails(!showDetails)}
            className="h-6 px-2">
            {showDetails ? "Hide" : "Show"} Details
          </Button>
        </div>
      </div>

      {/* Steps */}
      <div className="p-4 space-y-3">
        {steps.map((step) => (
          <div
            key={step.id}
            className={`
              border rounded-lg transition-all duration-200
              ${
                expandedSteps.has(step.id)
                  ? "bg-accent/10"
                  : "hover:bg-accent/5"
              }
              ${step.status === "error" ? "border-red-200 bg-red-50/50" : ""}
            `}>
            {/* Step Header */}
            <div
              className="p-3 flex items-center gap-3 cursor-pointer"
              onClick={() => {
                toggleStep(step.id);
                onStepClick?.(step);
              }}>
              {/* Status Icon */}
              <div className="flex-shrink-0">{getStatusIcon(step.status)}</div>

              {/* Step Icon */}
              <div
                className={`flex-shrink-0 p-1.5 rounded border ${getStepColor(
                  step.type
                )}`}>
                {getStepIcon(step.type)}
              </div>

              {/* Step Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-sm">{step.title}</h4>
                  {step.tool && (
                    <Badge variant="outline" className="text-xs">
                      {step.tool.name}
                    </Badge>
                  )}
                </div>

                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="capitalize">
                    {step.type.replace("_", " ")}
                  </span>
                  {step.duration && (
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDuration(step.duration)}
                    </span>
                  )}
                  {step.metadata?.tokens && (
                    <span>{step.metadata.tokens} tokens</span>
                  )}
                </div>
              </div>

              {/* Expand/Collapse Icon */}
              <div className="flex-shrink-0">
                {expandedSteps.has(step.id) ? (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </div>

            {/* Expanded Content */}
            {expandedSteps.has(step.id) && (
              <div className="px-3 pb-3 border-t">
                <div className="pt-3 space-y-3">
                  {/* Content */}
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground mb-1">
                      Content
                    </h5>
                    <p className="text-sm text-foreground whitespace-pre-wrap">
                      {step.content}
                    </p>
                  </div>

                  {/* Tool Details */}
                  {step.tool && (
                    <div className="space-y-2">
                      <h5 className="text-xs font-medium text-muted-foreground">
                        Tool Execution
                      </h5>

                      {step.tool.input && (
                        <div>
                          <h6 className="text-xs text-muted-foreground mb-1">
                            Input:
                          </h6>
                          <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                            {JSON.stringify(step.tool.input, null, 2)}
                          </pre>
                        </div>
                      )}

                      {step.tool.output && (
                        <div>
                          <h6 className="text-xs text-muted-foreground mb-1">
                            Output:
                          </h6>
                          <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
                            {JSON.stringify(step.tool.output, null, 2)}
                          </pre>
                        </div>
                      )}

                      {step.tool.error && (
                        <div>
                          <h6 className="text-xs text-muted-foreground mb-1">
                            Error:
                          </h6>
                          <p className="text-xs text-red-600 bg-red-50 p-2 rounded">
                            {step.tool.error}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Metadata */}
                  {step.metadata && (
                    <div>
                      <h5 className="text-xs font-medium text-muted-foreground mb-2">
                        Metadata
                      </h5>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {step.metadata.model && (
                          <div>
                            <span className="text-muted-foreground">
                              Model:
                            </span>
                            <span className="ml-1">{step.metadata.model}</span>
                          </div>
                        )}
                        {step.metadata.tokens && (
                          <div>
                            <span className="text-muted-foreground">
                              Tokens:
                            </span>
                            <span className="ml-1">{step.metadata.tokens}</span>
                          </div>
                        )}
                        {step.metadata.cost && (
                          <div>
                            <span className="text-muted-foreground">Cost:</span>
                            <span className="ml-1">
                              ${step.metadata.cost.toFixed(4)}
                            </span>
                          </div>
                        )}
                        {step.metadata.confidence && (
                          <div>
                            <span className="text-muted-foreground">
                              Confidence:
                            </span>
                            <span className="ml-1">
                              {(step.metadata.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className="text-xs text-muted-foreground">
                    {formatRelativeTime(step.timestamp)}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {steps.length === 0 && (
          <div className="text-center text-sm text-muted-foreground py-8">
            No thought process available
          </div>
        )}
      </div>
    </div>
  );
}
