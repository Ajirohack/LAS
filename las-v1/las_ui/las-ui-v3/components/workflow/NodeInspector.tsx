"use client";

import { useEffect } from "react";
import { Node } from "reactflow";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

const nodeSchema = z.object({
  label: z.string().min(1, "Label is required"),
  description: z.string().optional(),
  config: z.record(z.string(), z.unknown()).optional(),
});

type NodeFormData = z.infer<typeof nodeSchema>;

interface NodeInspectorProps {
  selectedNode: Node | null;
  onUpdateNode: (id: string, data: Record<string, unknown>) => void;
}

export function NodeInspector({
  selectedNode,
  onUpdateNode,
}: NodeInspectorProps) {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<NodeFormData>({
    resolver: zodResolver(nodeSchema),
    defaultValues: {
      label: "",
      description: "",
      config: {},
    },
  });

  useEffect(() => {
    if (selectedNode) {
      reset({
        label: selectedNode.data.label,
        description: selectedNode.data.description || "",
        config: selectedNode.data.config || {},
      });
    }
  }, [selectedNode, reset]);

  const onSubmit = (data: NodeFormData) => {
    if (selectedNode) {
      onUpdateNode(selectedNode.id, {
        ...selectedNode.data,
        ...data,
      });
    }
  };

  if (!selectedNode) {
    return (
      <Card className="h-full border-l rounded-none border-0">
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-6 text-center">
          <p>Select a node to edit its properties</p>
        </div>
      </Card>
    );
  }

  const nodeType = selectedNode.data.type || "default";

  return (
    <Card className="h-full border-l rounded-none border-0">
      <CardHeader className="p-4 border-b">
        <CardTitle className="text-sm font-medium">Properties</CardTitle>
        <CardDescription className="text-xs">
          Edit {nodeType} node configuration
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="label">Label</Label>
            <Input id="label" {...register("label")} />
            {errors.label && (
              <p className="text-xs text-red-500">{errors.label.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...register("description")}
              className="resize-none h-20"
            />
          </div>

          {/* Dynamic fields based on node type */}
          {nodeType === "action" && (
            <div className="space-y-2">
              <Label>Model</Label>
              <Select
                defaultValue={selectedNode.data.config?.model || "gpt-4"}
                onValueChange={(val: string) => setValue("config.model", val)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3-opus">Claude 3 Opus</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {nodeType === "trigger" && (
            <div className="flex items-center justify-between">
              <Label htmlFor="active">Active</Label>
              <Switch
                id="active"
                checked={watch("config.active") !== false}
                onCheckedChange={(checked: boolean) =>
                  setValue("config.active", checked)
                }
              />
            </div>
          )}

          <div className="pt-4">
            <Button type="submit" className="w-full">
              Save Changes
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
