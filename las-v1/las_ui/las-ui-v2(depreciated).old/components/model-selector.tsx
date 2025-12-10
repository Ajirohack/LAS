"use client"

import * as React from "react"
import { Check, ChevronsUpDown, Download } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import { SettingsModal } from "./settings-modal"
import { ModelBrowser } from "./model-browser"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function ModelSelector() {
    const [open, setOpen] = React.useState(false)
    const [showBrowser, setShowBrowser] = React.useState(false)
    const [selectedProvider, setSelectedProvider] = React.useState<string>("")
    const [selectedModel, setSelectedModel] = React.useState<string>("")
    const [models, setModels] = React.useState<{ [key: string]: string[] }>({
        ollama: [],
        openrouter: [],
        gemini: [],
        groq: [],
        "ollama-cloud": [],
    })

    const providers = [
        { value: "ollama", label: "Ollama" },
        { value: "openrouter", label: "OpenRouter" },
        { value: "gemini", label: "Google Gemini" },
        { value: "groq", label: "Groq" },
        { value: "ollama-cloud", label: "Ollama Cloud" },
    ]

    // Load saved selection on mount
    React.useEffect(() => {
        loadSavedSelection()
    }, [])

    // Load models when provider changes
    React.useEffect(() => {
        if (selectedProvider) {
            loadModels(selectedProvider)
        }
    }, [selectedProvider])

    async function loadSavedSelection() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/preferences/model-selection`)
            const data = await response.json()
            if (data.provider && data.model) {
                setSelectedProvider(data.provider)
                setSelectedModel(data.model)
            }
        } catch (error) {
            console.error("Failed to load saved selection:", error)
        }
    }

    async function loadModels(provider: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/models?provider=${provider}`)
            const data = await response.json()
            const modelList = data.models || []
            setModels(prev => ({ ...prev, [provider]: modelList }))
        } catch (error) {
            console.error(`Failed to load ${provider} models:`, error)
        }
    }

    async function handleProviderSelect(provider: string) {
        setSelectedProvider(provider)
        setSelectedModel("")
        setOpen(false)
    }

    async function handleModelSelect(provider: string, model: string) {
        setSelectedProvider(provider)
        setSelectedModel(model)

        // Save selection to backend
        try {
            await fetch(`${API_BASE_URL}/api/preferences/model-selection`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider, model })
            })
        } catch (error) {
            console.error("Failed to save selection:", error)
        }

        setOpen(false)
        setShowBrowser(false)
    }

    const currentModels = selectedProvider ? models[selectedProvider] || [] : []
    const providerLabel = providers.find(p => p.value === selectedProvider)?.label
    const displayText = selectedProvider && providerLabel
        ? (selectedModel ? `${providerLabel}: ${selectedModel}` : providerLabel)
        : "Select Provider"

    return (
        <>
            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-[300px] justify-between"
                    >
                        {displayText}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-[300px] p-0">
                    <Command>
                        <CommandInput placeholder="Search providers..." />
                        <CommandEmpty>No provider found.</CommandEmpty>
                        <CommandGroup>
                            {providers.map((provider) => (
                                <CommandItem
                                    key={provider.value}
                                    value={provider.value}
                                    onSelect={() => handleProviderSelect(provider.value)}
                                >
                                    <Check
                                        className={cn(
                                            "mr-2 h-4 w-4",
                                            selectedProvider === provider.value ? "opacity-100" : "opacity-0"
                                        )}
                                    />
                                    {provider.label}
                                </CommandItem>
                            ))}
                        </CommandGroup>
                    </Command>

                    {selectedProvider && currentModels.length > 0 && (
                        <>
                            <Separator />
                            <Command>
                                <CommandInput placeholder="Search models..." />
                                <CommandEmpty>No model found.</CommandEmpty>
                                <CommandGroup heading="Models">
                                    {currentModels.slice(0, 10).map((model: string) => (
                                        <CommandItem
                                            key={model}
                                            value={model}
                                            onSelect={() => handleModelSelect(selectedProvider, model)}
                                        >
                                            <Check
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    selectedModel === model ? "opacity-100" : "opacity-0"
                                                )}
                                            />
                                            {model}
                                        </CommandItem>
                                    ))}
                                </CommandGroup>
                            </Command>
                        </>
                    )}

                    {selectedProvider === 'ollama' && (
                        <>
                            <Separator />
                            <div className="p-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="w-full"
                                    onClick={() => {
                                        setOpen(false)
                                        setShowBrowser(true)
                                    }}
                                >
                                    <Download className="mr-2 h-4 w-4" />
                                    Manage Models
                                </Button>
                            </div>
                        </>
                    )}

                    <Separator />
                    <SettingsModal />
                </PopoverContent>
            </Popover>

            <Dialog open={showBrowser} onOpenChange={setShowBrowser}>
                <DialogContent className="max-w-3xl max-h-[80vh]">
                    <DialogHeader>
                        <DialogTitle>Manage Ollama Models</DialogTitle>
                    </DialogHeader>
                    <ModelBrowser
                        onSelect={handleModelSelect}
                        currentSelection={{ provider: selectedProvider, model: selectedModel }}
                    />
                </DialogContent>
            </Dialog>
        </>
    )
}
