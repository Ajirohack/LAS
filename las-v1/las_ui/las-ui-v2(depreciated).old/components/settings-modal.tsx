"use client";

import React, { useState } from 'react';
import { Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function SettingsModal() {
    const [open, setOpen] = useState(false);
    const [openRouterKey, setOpenRouterKey] = useState("");
    const [geminiKey, setGeminiKey] = useState("");
    const [groqKey, setGroqKey] = useState("");
    const [ollamaCloudKey, setOllamaCloudKey] = useState("");

    const handleSave = () => {
        // In a real app, you'd save these to a secure storage or backend
        // For now, we'll just log them or save to localStorage
        if (openRouterKey) localStorage.setItem("OPENROUTER_API_KEY", openRouterKey);
        if (geminiKey) localStorage.setItem("GOOGLE_API_KEY", geminiKey);
        if (groqKey) localStorage.setItem("GROQ_API_KEY", groqKey);
        if (ollamaCloudKey) localStorage.setItem("OLLAMA_CLOUD_API_KEY", ollamaCloudKey);

        setOpen(false);
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Settings</DialogTitle>
                    <DialogDescription>
                        Configure your API keys for external providers.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="openrouter" className="text-right">
                            OpenRouter
                        </Label>
                        <Input
                            id="openrouter"
                            type="password"
                            value={openRouterKey}
                            onChange={(e) => setOpenRouterKey(e.target.value)}
                            className="col-span-3"
                            placeholder="sk-or-..."
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="gemini" className="text-right">
                            Gemini
                        </Label>
                        <Input
                            id="gemini"
                            type="password"
                            value={geminiKey}
                            onChange={(e) => setGeminiKey(e.target.value)}
                            className="col-span-3"
                            placeholder="AIza..."
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="groq" className="text-right">
                            Groq
                        </Label>
                        <Input
                            id="groq"
                            type="password"
                            value={groqKey}
                            onChange={(e) => setGroqKey(e.target.value)}
                            className="col-span-3"
                            placeholder="gsk_..."
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="ollama-cloud" className="text-right">
                            Ollama Cloud
                        </Label>
                        <Input
                            id="ollama-cloud"
                            type="password"
                            value={ollamaCloudKey}
                            onChange={(e) => setOllamaCloudKey(e.target.value)}
                            className="col-span-3"
                            placeholder="Ollama Cloud Key..."
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button type="submit" onClick={handleSave}>Save changes</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
