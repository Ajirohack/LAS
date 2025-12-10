"use client";

import React from 'react';

export function TaskManager() {
    type Task = {
        id: number;
        title: string;
        status: string;
        agent: string;
    };

    // Placeholder data
    const tasks: Task[] = [
        { id: 1, title: "Refactor API Layer", status: "completed", agent: "Coder" },
        { id: 2, title: "Implement Streaming", status: "completed", agent: "Coder" },
        { id: 3, title: "Design Dashboard", status: "in-progress", agent: "Supervisor" },
        { id: 4, title: "Verify System", status: "pending", agent: "Planner" },
    ];

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return 'bg-green-500/15 text-green-600 dark:text-green-400';
            case 'in-progress': return 'bg-blue-500/15 text-blue-600 dark:text-blue-400';
            default: return 'bg-gray-500/15 text-gray-600 dark:text-gray-400';
        }
    };

    return (
        <div className="border rounded-xl bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
                <div>
                    <h3 className="text-2xl font-semibold leading-none tracking-tight">Active Tasks</h3>
                    <p className="text-sm text-muted-foreground mt-2">Monitor agent workflows and progress.</p>
                </div>
                <div className="flex gap-2">
                    <span className="flex h-2 w-2 rounded-full bg-blue-600 animate-pulse"></span>
                    <span className="text-xs text-muted-foreground">Processing</span>
                </div>
            </div>

            <div className="p-6 flex-1 overflow-y-auto">
                <div className="space-y-1">
                    {tasks.map((task: Task) => (
                        <div
                            key={task.id}
                            className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors group"
                        >
                            <div className="flex items-center gap-4">
                                <div className={`w-2 h-2 rounded-full ${task.status === 'completed' ? 'bg-green-500' :
                                    task.status === 'in-progress' ? 'bg-blue-500' : 'bg-gray-300'
                                    }`} />
                                <div>
                                    <p className="font-medium text-sm">{task.title}</p>
                                    <p className="text-xs text-muted-foreground">Assigned to: {task.agent}</p>
                                </div>
                            </div>

                            <div className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                                {task.status}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-4 border-t bg-muted/20">
                <button className="w-full py-2 text-sm font-medium text-primary hover:underline">
                    View All Tasks
                </button>
            </div>
        </div>
    );
}
