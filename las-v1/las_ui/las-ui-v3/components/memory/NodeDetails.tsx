"use client";

import { useState } from "react";
import {
  X,
  Edit3,
  Trash2,
  Tag,
  Calendar,
  Info,
  Link,
  Star,
  Eye,
  EyeOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn, formatRelativeTime } from "@/lib/utils";
import { MemoryNode, MemoryLink } from "./MemoryGraph";

interface NodeDetailsProps {
  node: MemoryNode | null;
  relatedNodes: MemoryNode[];
  relatedLinks: MemoryLink[];
  onClose: () => void;
  onUpdateNode?: (nodeId: string, updates: Partial<MemoryNode>) => void;
  onDeleteNode?: (nodeId: string) => void;
  onAddConnection?: (
    sourceId: string,
    targetId: string,
    linkType: MemoryLink["type"]
  ) => void;
  className?: string;
}

export function NodeDetails({
  node,
  relatedNodes,
  relatedLinks,
  onClose,
  onUpdateNode,
  onDeleteNode,
  onAddConnection,
  className = "",
}: NodeDetailsProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedNode, setEditedNode] = useState<MemoryNode | null>(node);
  const [showAllProperties, setShowAllProperties] = useState(false);
  const [newTag, setNewTag] = useState("");

  // Removed setState inside effect to avoid cascading renders per lint rule

  if (!node) {
    return (
      <div
        className={cn(
          "flex flex-col h-full items-center justify-center text-muted-foreground",
          className
        )}>
        <Info className="w-12 h-12 mb-4 opacity-50" />
        <p className="text-sm">Select a node to view details</p>
      </div>
    );
  }

  const handleSave = () => {
    if (editedNode && onUpdateNode) {
      onUpdateNode(node.id, editedNode);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditedNode(node);
    setIsEditing(false);
  };

  const handleAddTag = () => {
    if (newTag.trim() && editedNode) {
      const updatedNode = {
        ...editedNode,
        metadata: {
          ...editedNode.metadata,
          tags: [...(editedNode.metadata?.tags || []), newTag.trim()],
        },
      };
      setEditedNode(updatedNode);
      setNewTag("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    if (editedNode) {
      const updatedNode = {
        ...editedNode,
        metadata: {
          ...editedNode.metadata,
          tags: (editedNode.metadata?.tags || []).filter(
            (tag) => tag !== tagToRemove
          ),
        },
      };
      setEditedNode(updatedNode);
    }
  };

  const handleDelete = () => {
    if (
      onDeleteNode &&
      window.confirm(`Are you sure you want to delete "${node.label}"?`)
    ) {
      onDeleteNode(node.id);
      onClose();
    }
  };

  const getConnectionTypeLabel = (type: MemoryLink["type"]) => {
    const labels = {
      related: "Related to",
      causes: "Causes",
      "part-of": "Part of",
      similar: "Similar to",
      opposite: "Opposite of",
      temporal: "Connected to",
      semantic: "Semantically related to",
    };
    return labels[type];
  };

  return (
    <div
      className={cn("flex flex-col h-full bg-background border-l", className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
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
            <h3 className="font-semibold">
              {isEditing ? (
                <Input
                  value={editedNode?.label || ""}
                  onChange={(e) =>
                    setEditedNode((prev) =>
                      prev ? { ...prev, label: e.target.value } : null
                    )
                  }
                  className="text-sm font-semibold"
                />
              ) : (
                node.label
              )}
            </h3>
          </div>
          <Badge variant="outline" className="text-xs">
            {node.type}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          {onUpdateNode && (
            <>
              {isEditing ? (
                <>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleSave}
                    className="h-7 px-2">
                    Save
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleCancel}
                    className="h-7 px-2">
                    Cancel
                  </Button>
                </>
              ) : (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsEditing(true)}
                  className="h-7 px-2">
                  <Edit3 className="w-3 h-3" />
                </Button>
              )}
            </>
          )}
          {onDeleteNode && (
            <Button
              size="sm"
              variant="ghost"
              onClick={handleDelete}
              className="h-7 px-2 text-red-600 hover:text-red-700">
              <Trash2 className="w-3 h-3" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="h-7 px-2">
            <X className="w-3 h-3" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-6">
          {/* Basic Info */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold flex items-center gap-2">
              <Info className="w-4 h-4" />
              Basic Information
            </h4>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type:</span>
                <span className="capitalize">{node.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Category:</span>
                <span>{node.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created:</span>
                <span>{formatRelativeTime(node.timestamp)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Importance:</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${node.importance * 100}%` }}
                    />
                  </div>
                  <span>{(node.importance * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Confidence:</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 transition-all"
                      style={{ width: `${node.confidence * 100}%` }}
                    />
                  </div>
                  <span>{(node.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Description */}
          {node.metadata?.description && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold">Description</h4>
              {isEditing ? (
                <Textarea
                  value={editedNode?.metadata?.description || ""}
                  onChange={(e) =>
                    setEditedNode((prev) =>
                      prev
                        ? {
                            ...prev,
                            metadata: {
                              ...prev.metadata,
                              description: e.target.value,
                            },
                          }
                        : null
                    )
                  }
                  className="text-sm"
                  rows={3}
                />
              ) : (
                <p className="text-sm text-muted-foreground">
                  {node.metadata.description}
                </p>
              )}
            </div>
          )}

          {/* Tags */}
          {node.metadata?.tags && node.metadata.tags.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <Tag className="w-4 h-4" />
                Tags
              </h4>
              {isEditing ? (
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <Input
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="Add tag..."
                      className="text-sm"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddTag();
                        }
                      }}
                    />
                    <Button
                      size="sm"
                      onClick={handleAddTag}
                      disabled={!newTag.trim()}>
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {(editedNode?.metadata?.tags || []).map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                        <button
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-1 hover:text-destructive">
                          <X className="w-2 h-2" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex flex-wrap gap-1">
                  {node.metadata.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Connections */}
          {relatedNodes.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <Link className="w-4 h-4" />
                Connections ({relatedNodes.length})
              </h4>
              <div className="space-y-2">
                {relatedNodes.map((relatedNode) => {
                  const link = relatedLinks.find(
                    (l) =>
                      (l.source === node.id && l.target === relatedNode.id) ||
                      (l.target === node.id && l.source === relatedNode.id)
                  );

                  return (
                    <div
                      key={relatedNode.id}
                      className="flex items-center justify-between p-2 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                      onClick={() => onClose()}>
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{
                            backgroundColor: `hsl(${
                              relatedNode.type === "concept"
                                ? 220
                                : relatedNode.type === "entity"
                                ? 140
                                : relatedNode.type === "relation"
                                ? 35
                                : relatedNode.type === "event"
                                ? 0
                                : relatedNode.type === "document"
                                ? 270
                                : 180
                            }, 70%, 50%)`,
                          }}
                        />
                        <span className="text-sm font-medium">
                          {relatedNode.label}
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {relatedNode.type}
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {link && getConnectionTypeLabel(link.type)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Properties */}
          {node.metadata?.properties &&
            Object.keys(node.metadata.properties).length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold">Properties</h4>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setShowAllProperties(!showAllProperties)}
                    className="h-6 px-2">
                    {showAllProperties ? (
                      <>
                        <EyeOff className="w-3 h-3 mr-1" /> Hide
                      </>
                    ) : (
                      <>
                        <Eye className="w-3 h-3 mr-1" /> Show All
                      </>
                    )}
                  </Button>
                </div>
                <div className="space-y-2 text-sm">
                  {Object.entries(node.metadata.properties)
                    .slice(0, showAllProperties ? undefined : 3)
                    .map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground capitalize">
                          {key.replace(/([A-Z])/g, " $1").trim()}:
                        </span>
                        <span className="font-mono text-xs bg-muted px-2 py-1 rounded">
                          {typeof value === "object"
                            ? JSON.stringify(value)
                            : String(value)}
                        </span>
                      </div>
                    ))}
                </div>
                {!showAllProperties &&
                  Object.keys(node.metadata.properties).length > 3 && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setShowAllProperties(true)}
                      className="w-full h-7">
                      Show {Object.keys(node.metadata.properties).length - 3}{" "}
                      more
                    </Button>
                  )}
              </div>
            )}
        </div>
      </ScrollArea>
    </div>
  );
}
