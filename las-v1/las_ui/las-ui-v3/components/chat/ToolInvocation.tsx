'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Terminal, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ToolInvocationProps {
    tool: string;
    input: Record<string, unknown>;
    output?: unknown;
    status: 'running' | 'completed' | 'failed';
}

export function ToolInvocation({ tool, input, output, status }: ToolInvocationProps) {
    const [isExpanded, setIsExpanded] = useState(status === 'running');

    return (
        <div className="my-2 rounded-lg border border-border bg-zinc-900/30 overflow-hidden">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center gap-2 p-2 text-xs font-medium hover:bg-zinc-800/50 transition-colors"
            >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}

                <div className="flex items-center gap-2 flex-1">
                    <Terminal className="w-3 h-3 text-accent" />
                    <span className="text-foreground-muted">Used tool:</span>
                    <span className="text-foreground">{tool}</span>
                </div>

                {status === 'running' && <Loader2 className="w-3 h-3 animate-spin text-primary" />}
                {status === 'completed' && <CheckCircle2 className="w-3 h-3 text-success" />}
                {status === 'failed' && <XCircle className="w-3 h-3 text-error" />}
            </button>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="p-3 border-t border-border bg-zinc-950/50 space-y-2">
                            <div>
                                <div className="text-[10px] uppercase tracking-wider text-foreground-muted mb-1">Input</div>
                                <pre className="text-xs font-mono text-zinc-300 bg-zinc-900 p-2 rounded overflow-x-auto">
                                    {JSON.stringify(input, null, 2)}
                                </pre>
                            </div>

                            {output !== undefined && output !== null && (
                                <div>
                                    <div className="text-[10px] uppercase tracking-wider text-foreground-muted mb-1">Output</div>
                                    <pre className="text-xs font-mono text-zinc-300 bg-zinc-900 p-2 rounded overflow-x-auto">
                                        {typeof output === 'string' ? output : JSON.stringify(output, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
