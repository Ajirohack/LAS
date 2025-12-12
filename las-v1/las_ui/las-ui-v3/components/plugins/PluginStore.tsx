"use client";

import { useEffect, useState } from "react";
import { lasApi } from "@/app/api-client";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, Check, Box } from "lucide-react";
import { toast } from "sonner";

export interface Plugin {
    name: string;
    version: string;
    author: string;
    description: string;
    loaded: boolean;
    enabled: boolean;
    category?: string;
}

export function PluginStore() {
    const [plugins, setPlugins] = useState<Plugin[]>([]);
    const [loading, setLoading] = useState(true);

    // Initial Mock Data (fallback)
    const mockPlugins: Plugin[] = [
        {
            name: "web_surfer",
            version: "1.0.0",
            author: "LAS Team",
            description: "Autonomous web browsing and data extraction agent.",
            loaded: true,
            enabled: true,
            category: "Worker",
        },
        {
            name: "code_interpreter",
            version: "0.5.0",
            author: "LAS Team",
            description: "Execute Python code safely in a sandboxed environment.",
            loaded: true,
            enabled: true,
            category: "Tool",
        },
        {
            name: "vision_service",
            version: "1.2.0",
            author: "LAS Team",
            description: "Analyze images and videos using multimodal LLMs.",
            loaded: false,
            enabled: false,
            category: "Service",
        },
        {
            name: "telegram_connector",
            version: "0.1.0",
            author: "Community",
            description: "Connect your agent to Telegram for messaging.",
            loaded: false,
            enabled: false,
            category: "Integration",
        },
    ];

    useEffect(() => {
        const fetchPlugins = async () => {
            try {
                setLoading(true);
                // Real API fetch
                const data = await lasApi.listPlugins();
                // Merge with mock data or just use API data. For safety let's use API data if available.
                // If API returns empty and we want to show something, we could fallback, but ideally API is source of truth.
                // Let's assume API works.
                setPlugins(data && data.length > 0 ? data : mockPlugins);

            } catch (error) {
                console.error("Failed to fetch plugins", error);
                toast.error("Failed to fetch plugins from marketplace.");
                setPlugins(mockPlugins); // Fallback
            } finally {
                setLoading(false);
            }
        };

        fetchPlugins();
    }, []);

    const handleInstall = async (pluginName: string) => {
        try {
            toast.info(`Installing ${pluginName}...`);
            await lasApi.loadPlugin(pluginName);

            // Optimistic update
            setPlugins(prev => prev.map(p =>
                p.name === pluginName ? { ...p, loaded: true, enabled: true } : p
            ));

            toast.success(`${pluginName} installed successfully!`);
        } catch (error) {
            console.error(error);
            toast.error(`Failed to install ${pluginName}`);
        }
    };

    if (loading) {
        return <div className="p-10 text-center">Loading Marketplace...</div>;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {plugins.map((plugin) => (
                <Card key={plugin.name} className="flex flex-col">
                    <CardHeader>
                        <div className="flex justify-between items-start">
                            <div className="flex items-center gap-2">
                                <Box className="w-5 h-5 text-primary" />
                                <CardTitle className="text-lg">{plugin.name}</CardTitle>
                            </div>
                            <Badge variant={plugin.loaded ? "default" : "outline"}>
                                {plugin.loaded ? "Installed" : "Available"}
                            </Badge>
                        </div>
                        <CardDescription className="line-clamp-2 mt-2">
                            {plugin.description}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1">
                        <div className="text-xs text-muted-foreground flex gap-4">
                            <span>v{plugin.version}</span>
                            <span>by {plugin.author}</span>
                            {plugin.category && <span>{plugin.category}</span>}
                        </div>
                    </CardContent>
                    <CardFooter>
                        {plugin.loaded ? (
                            <Button variant="secondary" className="w-full" disabled>
                                <Check className="w-4 h-4 mr-2" /> Installed
                            </Button>
                        ) : (
                            <Button className="w-full" onClick={() => handleInstall(plugin.name)}>
                                <Download className="w-4 h-4 mr-2" /> Install
                            </Button>
                        )}
                    </CardFooter>
                </Card>
            ))}
        </div>
    );
}
