"use client";

import { useState } from "react";
import { useAppStore, Workspace } from "@/app/store";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Pencil, Trash2, Check, X, Plus } from "lucide-react";

interface WorkspaceManagerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function WorkspaceManager({
  open,
  onOpenChange,
}: WorkspaceManagerProps) {
  const { workspaces, updateWorkspace, deleteWorkspace, addWorkspace } =
    useAppStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");
  const [newWorkspaceName, setNewWorkspaceName] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const startEditing = (workspace: Workspace) => {
    setEditingId(workspace.id);
    setEditName(workspace.name);
  };

  const saveEdit = () => {
    if (editingId && editName.trim()) {
      updateWorkspace(editingId, { name: editName.trim() });
      setEditingId(null);
      setEditName("");
    }
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName("");
  };

  const handleDelete = (id: string) => {
    if (workspaces.length <= 1) return; // Prevent deleting the last workspace
    deleteWorkspace(id);
  };

  const handleAdd = () => {
    if (newWorkspaceName.trim()) {
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
        name: newWorkspaceName.trim(),
        color: colors[workspaces.length % colors.length],
        isActive: false,
      };
      addWorkspace(newWorkspace);
      setNewWorkspaceName("");
      setIsAdding(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Manage Workspaces</DialogTitle>
          <DialogDescription>
            Create, rename, or delete your workspaces.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <ScrollArea className="h-[300px] pr-4">
            <div className="space-y-3">
              {workspaces.map((workspace) => (
                <div
                  key={workspace.id}
                  className="flex items-center justify-between gap-2 p-2 rounded-lg border bg-card text-card-foreground shadow-sm">
                  {editingId === workspace.id ? (
                    <div className="flex items-center gap-2 flex-1">
                      <Input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="h-8"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === "Enter") saveEdit();
                          if (e.key === "Escape") cancelEdit();
                        }}
                      />
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 text-green-500"
                        onClick={saveEdit}>
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="h-8 w-8 text-red-500"
                        onClick={cancelEdit}>
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div
                          className="w-3 h-3 rounded-full shrink-0"
                          style={{ backgroundColor: workspace.color }}
                        />
                        <span className="font-medium truncate">
                          {workspace.name}
                        </span>
                        {workspace.isActive && (
                          <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                            Active
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-8 w-8"
                          onClick={() => startEditing(workspace)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          disabled={workspaces.length <= 1}
                          onClick={() => handleDelete(workspace.id)}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>

          {isAdding ? (
            <div className="mt-4 flex items-center gap-2 p-2 border rounded-lg border-dashed">
              <Input
                placeholder="Workspace name..."
                value={newWorkspaceName}
                onChange={(e) => setNewWorkspaceName(e.target.value)}
                className="h-9"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAdd();
                  if (e.key === "Escape") setIsAdding(false);
                }}
              />
              <Button size="sm" onClick={handleAdd}>
                Add
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsAdding(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              className="w-full mt-4 border-dashed"
              onClick={() => setIsAdding(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create New Workspace
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
