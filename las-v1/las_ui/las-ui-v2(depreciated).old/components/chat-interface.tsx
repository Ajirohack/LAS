"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useAgentStream } from '@/lib/hooks/use-stream';
import { lasApi } from '@/lib/api';
import { ModelSelector } from './model-selector';
import ReactMarkdown from 'react-markdown';

export function ChatInterface() {
    const [input, setInput] = useState('');
    const [history, setHistory] = useState<{ role: string, content: string }[]>([]);
    const { messages, isConnected } = useAgentStream();
    const scrollRef = useRef<HTMLDivElement>(null);

    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history, messages]);

    // Handle incoming stream messages
    useEffect(() => {
        if (messages.length > 0) {
            const lastMsg = messages[messages.length - 1];
            // Assuming the stream sends structured updates we can display
            // For now, just logging or appending if it's a chat message
            if (lastMsg.type === 'chat') {
                setHistory((prev: { role: string, content: string }[]) => [...prev, { role: 'assistant', content: lastMsg.data.content }]);
            }
        }
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setHistory((prev: { role: string, content: string }[]) => [...prev, { role: 'user', content: userMsg }]);

        try {
            await lasApi.query(userMsg, selectedProvider, selectedModel);
        } catch (error) {
            console.error('Failed to send message:', error);
            setHistory((prev: { role: string, content: string }[]) => [...prev, { role: 'system', content: 'Error sending message.' }]);
        }
    };

    const handleModelChange = (provider: string, model: string) => {
        setSelectedProvider(provider);
        setSelectedModel(model);
    };

    return (
        <div className="flex flex-col h-[600px] w-full max-w-4xl mx-auto border rounded-xl overflow-hidden bg-background shadow-lg">
            {/* Header */}
            <div className="p-4 border-b bg-muted/50 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <h2 className="font-semibold">Agent Chat</h2>
                    <ModelSelector onModelChange={handleModelChange} />
                </div>
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} title={isConnected ? "Connected" : "Disconnected"} />
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {history.map((msg: { role: string, content: string }, idx: number) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg px-4 py-2 ${msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                            }`}>
                            <ReactMarkdown className="text-sm prose dark:prose-invert max-w-none">
                                {msg.content}
                            </ReactMarkdown>
                        </div>
                    </div>
                ))}
                {/* Streamed events visualization could go here */}
                {messages.length > 0 && (
                    <div className="text-xs text-muted-foreground mt-2">
                        Last event: {messages[messages.length - 1].type}
                    </div>
                )}
            </div>

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-4 border-t bg-background">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <button
                        type="submit"
                        disabled={!isConnected}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
}
