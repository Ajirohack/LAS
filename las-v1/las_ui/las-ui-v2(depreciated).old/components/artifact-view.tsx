"use client";

import React from 'react';
import { Code, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface ArtifactViewProps {
    isOpen: boolean;
    onClose: () => void;
    content?: string;
    type?: 'code' | 'text';
    language?: string;
}

export function ArtifactView({ isOpen, onClose, content, type = 'code', language = 'javascript' }: ArtifactViewProps) {
    if (!isOpen) return null;

    return (
        <div className="h-full border-l bg-background flex flex-col w-full max-w-xl shadow-xl transition-all duration-300">
            <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-2">
                    {type === 'code' ? <Code className="h-5 w-5 text-blue-500" /> : <FileText className="h-5 w-5 text-orange-500" />}
                    <h3 className="font-semibold">Artifact Viewer</h3>
                </div>
                <Button variant="ghost" size="icon" onClick={onClose}>
                    <X className="h-4 w-4" />
                </Button>
            </div>

            <div className="flex-1 overflow-hidden">
                <Tabs defaultValue="preview" className="h-full flex flex-col">
                    <div className="px-4 pt-2">
                        <TabsList className="w-full justify-start">
                            <TabsTrigger value="preview">Preview</TabsTrigger>
                            <TabsTrigger value="code">Code</TabsTrigger>
                        </TabsList>
                    </div>

                    <TabsContent value="preview" className="flex-1 p-4 h-full overflow-hidden">
                        <div className="h-full w-full border rounded-md bg-muted/20 flex items-center justify-center text-muted-foreground">
                            Preview not available for this type
                        </div>
                    </TabsContent>

                    <TabsContent value="code" className="flex-1 h-full overflow-hidden">
                        <ScrollArea className="h-full w-full">
                            <pre className="p-4 text-sm font-mono">
                                <code>{content || "// No content available"}</code>
                            </pre>
                        </ScrollArea>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
