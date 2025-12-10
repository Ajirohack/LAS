"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Download, Trash2, Search, Check, Server } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface OllamaModel {
    name: string
    model: string
    size: number
    digest: string
    modified_at: string
    details?: any
}

interface LibraryModel {
    name: string
    description: string
    tags: string[]
}

interface DownloadProgress {
    status: string
    completed: number
    total: number
    percent?: number
}

export function ModelBrowser({
    onSelect,
    currentSelection
}: {
    onSelect: (provider: string, model: string) => void
    currentSelection?: { provider: string, model: string }
}) {
    // The following lines are added based on the provided Code Edit, assuming they are new declarations.
    // Note: 'providers', 'selectedProvider', 'models', 'selectedModel' are not defined in the original context.
    // This insertion might lead to compilation errors if these variables are not defined elsewhere.
    // For the purpose of faithfully applying the change as instructed, they are inserted.
    // const currentModels = selectedProvider ? models[selectedProvider] || [] : []
    // const displayText = selectedProvider && selectedModel
    //     ? `${providers.find((p: { value: string; label: string }) => p.value === selectedProvider)?.label}: ${selectedModel}`
    //     : "Select Model"

    const [localModels, setLocalModels] = useState<OllamaModel[]>([])
    const [libraryModels, setLibraryModels] = useState<LibraryModel[]>([])
    const [searchQuery, setSearchQuery] = useState("")
    const [downloading, setDownloading] = useState<Map<string, DownloadProgress>>(new Map())
    const [loading, setLoading] = useState(true)
    const { toast } = useToast()

    useEffect(() => {
        loadLocalModels()
        loadLibraryModels()
    }, [])

    async function loadLocalModels() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ollama/models/local`)
            const data = await response.json()
            setLocalModels(data.models || [])
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load local models",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    async function loadLibraryModels() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ollama/models/library`)
            const data = await response.json()
            setLibraryModels(data.models || [])
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load library models",
                variant: "destructive"
            })
        }
    }

    async function handleDownload(modelName: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/ollama/models/pull`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: modelName })
            })

            if (!response.ok) throw new Error('Failed to start download')

            const reader = response.body?.getReader()
            const decoder = new TextDecoder()

            while (reader) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)
                const lines = chunk.split('\n')

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6))

                        if (data.status === 'done') {
                            setDownloading(prev => {
                                const newMap = new Map(prev)
                                newMap.delete(modelName)
                                return newMap
                            })
                            toast({
                                title: "Success",
                                description: `Model ${modelName} downloaded successfully`
                            })
                            loadLocalModels()
                        } else if (data.status === 'error') {
                            setDownloading(prev => {
                                const newMap = new Map(prev)
                                newMap.delete(modelName)
                                return newMap
                            })
                            toast({
                                title: "Error",
                                description: data.message,
                                variant: "destructive"
                            })
                        } else {
                            setDownloading(prev => new Map(prev).set(modelName, data))
                        }
                    }
                }
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to download model",
                variant: "destructive"
            })
        }
    }

    async function handleDelete(modelName: string) {
        if (!confirm(`Are you sure you want to delete ${modelName}?`)) return

        try {
            const response = await fetch(`${API_BASE_URL}/api/ollama/models/${modelName}`, {
                method: 'DELETE'
            })

            if (!response.ok) throw new Error('Failed to delete model')

            toast({
                title: "Success",
                description: `Model ${modelName} deleted`
            })
            loadLocalModels()
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete model",
                variant: "destructive"
            })
        }
    }

    const filteredLocalModels = localModels.filter(m =>
        m.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    const filteredLibraryModels = libraryModels.filter(m =>
        m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.description.toLowerCase().includes(searchQuery.toLowerCase())
    )

    function formatSize(bytes: number): string {
        const gb = bytes / (1024 ** 3)
        return `${gb.toFixed(2)} GB`
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search models..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="flex-1"
                />
            </div>

            <Tabs defaultValue="local" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="local">
                        Downloaded ({filteredLocalModels.length})
                    </TabsTrigger>
                    <TabsTrigger value="library">
                        Ollama Library ({filteredLibraryModels.length})
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="local" className="space-y-4">
                    <ScrollArea className="h-[400px]">
                        <div className="grid gap-4">
                            {filteredLocalModels.map((model) => {
                                const isSelected = currentSelection?.provider === 'ollama' &&
                                    currentSelection?.model === model.name

                                return (
                                    <Card key={model.name} className={isSelected ? "border-primary" : ""}>
                                        <CardHeader>
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <CardTitle className="flex items-center gap-2">
                                                        {model.name}
                                                        {isSelected && <Check className="h-4 w-4 text-primary" />}
                                                    </CardTitle>
                                                    <CardDescription>
                                                        {formatSize(model.size)} • Modified {new Date(model.modified_at).toLocaleDateString()}
                                                    </CardDescription>
                                                </div>
                                            </div>
                                        </CardHeader>
                                        <CardFooter className="flex gap-2">
                                            <Button
                                                size="sm"
                                                variant={isSelected ? "default" : "outline"}
                                                onClick={() => onSelect('ollama', model.name)}
                                                className="flex-1"
                                            >
                                                {isSelected ? "Selected" : "Select"}
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="destructive"
                                                onClick={() => handleDelete(model.name)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </CardFooter>
                                    </Card>
                                )
                            })}
                        </div>
                    </ScrollArea>
                </TabsContent>

                <TabsContent value="library" className="space-y-4">
                    <ScrollArea className="h-[400px]">
                        <div className="grid gap-4">
                            {filteredLibraryModels.map((model) => {
                                const isDownloading = downloading.has(model.name)
                                const progress = downloading.get(model.name)
                                const isInstalled = localModels.some(m => m.name.startsWith(model.name))

                                return (
                                    <Card key={model.name}>
                                        <CardHeader>
                                            <CardTitle>{model.name}</CardTitle>
                                            <CardDescription>{model.description}</CardDescription>
                                            <div className="flex gap-1 flex-wrap mt-2">
                                                {model.tags.map(tag => (
                                                    <Badge key={tag} variant="secondary" className="text-xs">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </CardHeader>
                                        <CardFooter>
                                            {isDownloading ? (
                                                <div className="w-full space-y-2">
                                                    <div className="flex justify-between text-sm text-muted-foreground">
                                                        <span>{progress?.status}</span>
                                                        <span>{progress?.percent?.toFixed(1)}%</span>
                                                    </div>
                                                    <Progress value={progress?.percent || 0} />
                                                </div>
                                            ) : (
                                                <Button
                                                    size="sm"
                                                    onClick={() => handleDownload(model.name)}
                                                    disabled={isInstalled}
                                                    className="flex-1"
                                                >
                                                    {isInstalled ? (
                                                        <>
                                                            <Check className="mr-2 h-4 w-4" />
                                                            Installed
                                                        </>
                                                    ) : (
                                                        <>
                                                            <Download className="mr-2 h-4 w-4" />
                                                            Download
                                                        </>
                                                    )}
                                                </Button>
                                            )}
                                        </CardFooter>
                                    </Card>
                                )
                            })}
                        </div>
                    </ScrollArea>
                </TabsContent>
            </Tabs>
        </div>
    )
}
