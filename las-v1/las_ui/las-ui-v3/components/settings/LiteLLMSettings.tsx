"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertCircle, Check, ChevronRight, Cloud, Cpu, Settings2, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface Provider {
    id: string;
    name: string;
    configured: boolean;
    features: string[];
    key_env?: string;
    base_url?: string;
}

interface Model {
    id: string;
    provider: string;
    context_length: number;
    features: string[];
    litellm_model: string;
}

interface LiteLLMSettingsProps {
    className?: string;
    onSettingsChange?: (settings: LiteLLMSettings) => void;
}

interface LiteLLMSettings {
    provider: string;
    model: string;
    temperature: number;
    maxTokens: number;
    ollamaBaseUrl: string;
}

export function LiteLLMSettings({ className, onSettingsChange }: LiteLLMSettingsProps) {
    const [providers, setProviders] = useState<Provider[]>([]);
    const [models, setModels] = useState<Model[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Settings state
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("llama3.2");
    const [temperature, setTemperature] = useState(0.7);
    const [maxTokens, setMaxTokens] = useState(4096);
    const [ollamaBaseUrl, setOllamaBaseUrl] = useState("http://localhost:11434");
    const [streamingEnabled, setStreamingEnabled] = useState(true);

    // Fetch providers and models on mount
    useEffect(() => {
        fetchData();
    }, []);

    // Update models when provider changes
    useEffect(() => {
        fetchModels(selectedProvider);
    }, [selectedProvider]);

    // Notify parent of settings changes
    useEffect(() => {
        if (onSettingsChange) {
            onSettingsChange({
                provider: selectedProvider,
                model: selectedModel,
                temperature,
                maxTokens,
                ollamaBaseUrl,
            });
        }
    }, [selectedProvider, selectedModel, temperature, maxTokens, ollamaBaseUrl, onSettingsChange]);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Fetch providers
            const providersRes = await fetch("/api/v1/litellm/providers");
            if (providersRes.ok) {
                const data = await providersRes.json();
                setProviders(data);
            }

            // Fetch all models
            const modelsRes = await fetch("/api/v1/litellm/models");
            if (modelsRes.ok) {
                const data = await modelsRes.json();
                setModels(data);
            }

            setError(null);
        } catch (err) {
            setError("Failed to connect to LiteLLM service");
            console.error("LiteLLM fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchModels = async (provider: string) => {
        try {
            const res = await fetch(`/api/v1/litellm/models?provider=${provider}`);
            if (res.ok) {
                const data = await res.json();
                setModels(data);
                if (data.length > 0) {
                    setSelectedModel(data[0].id);
                }
            }
        } catch (err) {
            console.error("Failed to fetch models:", err);
        }
    };

    const handleSaveSettings = async () => {
        try {
            const res = await fetch("/api/v1/litellm/config/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    default_provider: selectedProvider,
                    default_model: `${selectedProvider}/${selectedModel}`,
                    ollama_base_url: ollamaBaseUrl,
                    temperature,
                    max_tokens: maxTokens,
                }),
            });

            if (res.ok) {
                // Show success feedback
                console.log("Settings saved successfully");
            }
        } catch (err) {
            console.error("Failed to save settings:", err);
        }
    };

    const getProviderIcon = (providerId: string) => {
        const localProviders = ["ollama", "vllm", "llamafile"];
        if (localProviders.includes(providerId)) {
            return <Cpu className="w-4 h-4" />;
        }
        return <Cloud className="w-4 h-4" />;
    };

    const filteredModels = models.filter(m => m.provider === selectedProvider);

    if (loading) {
        return (
            <Card className={cn("w-full", className)}>
                <CardContent className="p-6">
                    <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className={cn("w-full", className)}>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Settings2 className="w-5 h-5" />
                            LiteLLM Settings
                        </CardTitle>
                        <CardDescription>
                            Configure your AI model provider and settings
                        </CardDescription>
                    </div>
                    <Badge variant="outline" className="text-xs">
                        100+ Providers
                    </Badge>
                </div>
            </CardHeader>

            <CardContent>
                <Tabs defaultValue="provider" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="provider">Provider</TabsTrigger>
                        <TabsTrigger value="model">Model</TabsTrigger>
                        <TabsTrigger value="advanced">Advanced</TabsTrigger>
                    </TabsList>

                    {/* Provider Selection */}
                    <TabsContent value="provider" className="space-y-4 mt-4">
                        <div className="grid gap-4">
                            <Label>Select Provider</Label>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                {providers.map((provider) => (
                                    <button
                                        key={provider.id}
                                        onClick={() => setSelectedProvider(provider.id)}
                                        className={cn(
                                            "flex items-center gap-2 p-3 rounded-lg border transition-all",
                                            "hover:border-primary/50 hover:bg-accent",
                                            selectedProvider === provider.id
                                                ? "border-primary bg-primary/5"
                                                : "border-border"
                                        )}
                                    >
                                        {getProviderIcon(provider.id)}
                                        <div className="flex-1 text-left">
                                            <div className="font-medium text-sm">{provider.name}</div>
                                            <div className="text-xs text-muted-foreground">
                                                {provider.configured ? (
                                                    <span className="flex items-center gap-1 text-green-500">
                                                        <Check className="w-3 h-3" /> Ready
                                                    </span>
                                                ) : provider.id === "ollama" ? (
                                                    <span className="text-muted-foreground">Local</span>
                                                ) : (
                                                    <span className="flex items-center gap-1 text-amber-500">
                                                        <AlertCircle className="w-3 h-3" /> No API Key
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        {selectedProvider === provider.id && (
                                            <ChevronRight className="w-4 h-4 text-primary" />
                                        )}
                                    </button>
                                ))}
                            </div>

                            {selectedProvider === "ollama" && (
                                <div className="space-y-2 p-4 rounded-lg bg-accent/50">
                                    <Label htmlFor="ollamaUrl">Ollama Base URL</Label>
                                    <Input
                                        id="ollamaUrl"
                                        value={ollamaBaseUrl}
                                        onChange={(e) => setOllamaBaseUrl(e.target.value)}
                                        placeholder="http://localhost:11434"
                                    />
                                    <p className="text-xs text-muted-foreground">
                                        Default: http://localhost:11434
                                    </p>
                                </div>
                            )}
                        </div>
                    </TabsContent>

                    {/* Model Selection */}
                    <TabsContent value="model" className="space-y-4 mt-4">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label>Select Model</Label>
                                <Select value={selectedModel} onValueChange={setSelectedModel}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select a model" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <ScrollArea className="h-[200px]">
                                            {filteredModels.map((model) => (
                                                <SelectItem key={model.id} value={model.id}>
                                                    <div className="flex items-center gap-2">
                                                        <span>{model.id}</span>
                                                        <span className="text-xs text-muted-foreground">
                                                            {(model.context_length / 1000).toFixed(0)}K
                                                        </span>
                                                    </div>
                                                </SelectItem>
                                            ))}
                                        </ScrollArea>
                                    </SelectContent>
                                </Select>
                            </div>

                            {filteredModels.length > 0 && (
                                <div className="p-4 rounded-lg bg-accent/50 space-y-2">
                                    <div className="text-sm font-medium">Model Info</div>
                                    <div className="flex flex-wrap gap-1">
                                        {filteredModels
                                            .find((m) => m.id === selectedModel)
                                            ?.features.map((feature) => (
                                                <Badge key={feature} variant="secondary" className="text-xs">
                                                    {feature}
                                                </Badge>
                                            ))}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        LiteLLM Model: {selectedProvider}/{selectedModel}
                                    </div>
                                </div>
                            )}
                        </div>
                    </TabsContent>

                    {/* Advanced Settings */}
                    <TabsContent value="advanced" className="space-y-6 mt-4">
                        <div className="space-y-4">
                            {/* Temperature */}
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label>Temperature</Label>
                                    <span className="text-sm text-muted-foreground">{temperature}</span>
                                </div>
                                <Slider
                                    value={[temperature]}
                                    onValueChange={([val]) => setTemperature(val)}
                                    min={0}
                                    max={2}
                                    step={0.1}
                                    className="w-full"
                                />
                                <p className="text-xs text-muted-foreground">
                                    Lower = more focused, Higher = more creative
                                </p>
                            </div>

                            {/* Max Tokens */}
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label>Max Tokens</Label>
                                    <span className="text-sm text-muted-foreground">{maxTokens}</span>
                                </div>
                                <Slider
                                    value={[maxTokens]}
                                    onValueChange={([val]) => setMaxTokens(val)}
                                    min={256}
                                    max={32768}
                                    step={256}
                                    className="w-full"
                                />
                            </div>

                            {/* Streaming Toggle */}
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label>Streaming Responses</Label>
                                    <p className="text-xs text-muted-foreground">
                                        Stream tokens as they are generated
                                    </p>
                                </div>
                                <Switch
                                    checked={streamingEnabled}
                                    onCheckedChange={setStreamingEnabled}
                                />
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>

                {/* Save Button */}
                <div className="flex justify-end mt-6 pt-4 border-t">
                    <Button onClick={handleSaveSettings} className="gap-2">
                        <Zap className="w-4 h-4" />
                        Save Settings
                    </Button>
                </div>

                {error && (
                    <div className="mt-4 p-3 rounded-lg bg-destructive/10 text-destructive text-sm flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

export default LiteLLMSettings;
