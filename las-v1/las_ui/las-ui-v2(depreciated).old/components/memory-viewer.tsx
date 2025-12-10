"use client";

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import { lasApi } from '@/lib/api';
import { useTheme } from 'next-themes';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

type MemoryType = 'episodic' | 'semantic' | 'entity' | 'graph';

export function MemoryViewer() {
    const [activeTab, setActiveTab] = useState<MemoryType>('graph');
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [loading, setLoading] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const { theme } = useTheme();

    useEffect(() => {
        if (activeTab === 'graph') {
            loadGraphData();
        }
    }, [activeTab]);

    const loadGraphData = async () => {
        setLoading(true);
        try {
            const data = await lasApi.getKnowledgeGraph();
            setGraphData(data);
        } catch (error) {
            console.error("Failed to load knowledge graph:", error);
        } finally {
            setLoading(false);
        }
    };

    // Placeholder data for other tabs
    const memories = {
        episodic: [
            { id: 1, content: "User asked to refactor the codebase.", timestamp: "2 mins ago" },
            { id: 2, content: "Analyzed AgenticSeek architecture.", timestamp: "1 hour ago" },
        ],
        semantic: [
            { id: 1, content: "LAS Architecture Overview", relevance: 0.95 },
            { id: 2, content: "React Component Patterns", relevance: 0.88 },
        ],
        entity: [
            { id: 1, name: "User", attributes: { role: "Admin", preference: "Dark Mode" } },
            { id: 2, name: "Project", attributes: { name: "LAS", status: "In Progress" } },
        ]
    };

    return (
        <div className="border rounded-xl bg-card text-card-foreground shadow-sm h-full flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
                <div>
                    <h3 className="text-2xl font-semibold leading-none tracking-tight">Memory System</h3>
                    <p className="text-sm text-muted-foreground mt-2">Inspect agent&apos;s internal state and knowledge.</p>
                </div>
                <button
                    onClick={loadGraphData}
                    className="text-xs bg-secondary text-secondary-foreground px-3 py-1 rounded-md hover:bg-secondary/80"
                >
                    Refresh
                </button>
            </div>

            <div className="flex border-b">
                {(['graph', 'episodic', 'semantic', 'entity'] as MemoryType[]).map((type) => (
                    <button
                        key={type}
                        onClick={() => setActiveTab(type)}
                        className={`flex-1 px-4 py-3 text-sm font-medium transition-colors hover:bg-muted/50 ${activeTab === type
                            ? 'border-b-2 border-primary text-primary'
                            : 'text-muted-foreground'
                            }`}
                    >
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                ))}
            </div>

            <div className="flex-1 overflow-hidden relative" ref={containerRef}>
                {activeTab === 'graph' ? (
                    <div className="h-full w-full">
                        {loading && (
                            <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
                                <span className="animate-pulse">Loading Graph...</span>
                            </div>
                        )}
                        {containerRef.current && (
                            <ForceGraph2D
                                width={containerRef.current.clientWidth}
                                height={containerRef.current.clientHeight}
                                graphData={graphData}
                                nodeLabel="label"
                                nodeColor={(node: any) => {
                                    if (node.type === 'skill') return '#3b82f6'; // blue
                                    if (node.type === 'reflection') return '#ef4444'; // red
                                    if (node.type === 'task') return '#10b981'; // green
                                    return '#6b7280'; // gray
                                }}
                                nodeRelSize={6}
                                linkDirectionalParticles={2}
                                linkDirectionalParticleSpeed={0.005}
                                backgroundColor={theme === 'dark' ? '#020817' : '#ffffff'}
                                linkColor={() => theme === 'dark' ? '#374151' : '#e5e7eb'}
                            />
                        )}
                    </div>
                ) : (
                    <div className="p-6 overflow-y-auto h-full">
                        <div className="space-y-4">
                            {activeTab === 'episodic' && memories.episodic.map((m: { id: number, content: string, timestamp: string }) => (
                                <div key={m.id} className="p-4 rounded-lg border bg-muted/20">
                                    <p className="text-sm">{m.content}</p>
                                    <p className="text-xs text-muted-foreground mt-2">{m.timestamp}</p>
                                </div>
                            ))}

                            {activeTab === 'semantic' && memories.semantic.map((m: { id: number, content: string, relevance: number }) => (
                                <div key={m.id} className="p-4 rounded-lg border bg-muted/20 flex justify-between items-center">
                                    <span className="text-sm font-medium">{m.content}</span>
                                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                                        {(m.relevance * 100).toFixed(0)}% Match
                                    </span>
                                </div>
                            ))}

                            {activeTab === 'entity' && memories.entity.map((m: { id: number, name: string, attributes: Record<string, string | undefined> }) => (
                                <div key={m.id} className="p-4 rounded-lg border bg-muted/20">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                                            {m.name[0]}
                                        </div>
                                        <span className="font-medium">{m.name}</span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                        {Object.entries(m.attributes).map(([k, v]: [string, string | undefined]) => (
                                            <div key={k} className="bg-background p-2 rounded border">
                                                <span className="text-muted-foreground">{k}:</span> {v}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
