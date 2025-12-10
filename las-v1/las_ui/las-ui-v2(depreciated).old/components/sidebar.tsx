"use client";

import React from 'react';
import { MessageSquare, Plus, GitBranch, LayoutDashboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface SidebarProps {
    className?: string;
    activeView?: string;
    onNavigate?: (view: string) => void;
}

export function Sidebar({ className, activeView = 'chat', onNavigate }: SidebarProps) {
    // Mock history data - in real app this would come from backend/localstorage
    const history = [
        { id: '1', title: 'Project Planning', date: 'Today' },
        { id: '2', title: 'React Component Help', date: 'Yesterday' },
        { id: '3', title: 'Python Script Debugging', date: 'Previous 7 Days' },
    ];

    return (
        <div className={cn("pb-12 w-64 border-r bg-muted/10 hidden md:block", className)}>
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <Button variant="secondary" className="w-full justify-start gap-2">
                        <Plus className="h-4 w-4" />
                        New Chat
                    </Button>
                </div>

                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
                        Views
                    </h2>
                    <div className="space-y-1">
                        <Button
                            variant={activeView === 'chat' ? "secondary" : "ghost"}
                            className="w-full justify-start"
                            onClick={() => onNavigate?.('chat')}
                        >
                            <LayoutDashboard className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                        <Button
                            variant={activeView === 'workflows' ? "secondary" : "ghost"}
                            className="w-full justify-start"
                            onClick={() => onNavigate?.('workflows')}
                        >
                            <GitBranch className="mr-2 h-4 w-4" />
                            Workflows
                        </Button>
                    </div>
                </div>

                <div className="py-2">
                    <h2 className="relative px-7 text-lg font-semibold tracking-tight">
                        History
                    </h2>
                    <ScrollArea className="h-[300px] px-1">
                        <div className="space-y-1 p-2">
                            {history.map((item) => (
                                <Button
                                    key={item.id}
                                    variant="ghost"
                                    className="w-full justify-start font-normal truncate"
                                >
                                    <MessageSquare className="mr-2 h-4 w-4" />
                                    {item.title}
                                </Button>
                            ))}
                        </div>
                    </ScrollArea>
                </div>
            </div>
        </div>
    );
}
