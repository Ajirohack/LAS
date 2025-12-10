import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Globe,
  Brain,
  Zap,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  Edit3,
  Save,
  RefreshCw
} from 'lucide-react';
import { useStore } from '@/lib/store';

export interface AIProvider {
  id: string;
  name: string;
  type: 'openai' | 'anthropic' | 'google' | 'openrouter' | 'custom';
  apiKey: string;
  baseUrl?: string;
  models: ModelConfig[];
  enabled: boolean;
  isDefault: boolean;
  config: {
    maxTokens?: number;
    temperature?: number;
    topP?: number;
    frequencyPenalty?: number;
    presencePenalty?: number;
    timeout?: number;
    retryAttempts?: number;
  };
}

export interface ModelConfig {
  id: string;
  name: string;
  contextLength: number;
  maxTokens: number;
  pricing?: {
    input: number;
    output: number;
  };
  capabilities: string[];
  enabled: boolean;
}

const ProviderConfig: React.FC = () => {
  const { providers, setProviders } = useStore();
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [showApiKey, setShowApiKey] = useState<{ [key: string]: boolean }>({});
  const [isEditing, setIsEditing] = useState<{ [key: string]: boolean }>({});
  const [testResults, setTestResults] = useState<{ [key: string]: { success: boolean; message: string } }>({});
  const [newProvider, setNewProvider] = useState<Partial<AIProvider> | null>(null);

  const providerTypes = [
    { value: 'openai', label: 'OpenAI', icon: Brain, color: 'text-green-600' },
    { value: 'anthropic', label: 'Anthropic', icon: Zap, color: 'text-orange-600' },
    { value: 'google', label: 'Google AI', icon: Globe, color: 'text-blue-600' },
    { value: 'openrouter', label: 'OpenRouter', icon: RefreshCw, color: 'text-purple-600' },
    { value: 'custom', label: 'Custom', icon: Settings, color: 'text-gray-600' }
  ];

  const defaultModels: { [key: string]: ModelConfig[] } = {
    openai: [
      { id: 'gpt-4', name: 'GPT-4', contextLength: 8192, maxTokens: 8192, capabilities: ['text', 'code', 'reasoning'], enabled: true },
      { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', contextLength: 128000, maxTokens: 4096, capabilities: ['text', 'code', 'reasoning', 'vision'], enabled: true },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', contextLength: 16385, maxTokens: 4096, capabilities: ['text', 'code'], enabled: true }
    ],
    anthropic: [
      { id: 'claude-3-opus', name: 'Claude 3 Opus', contextLength: 200000, maxTokens: 4096, capabilities: ['text', 'code', 'reasoning'], enabled: true },
      { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', contextLength: 200000, maxTokens: 4096, capabilities: ['text', 'code', 'reasoning'], enabled: true },
      { id: 'claude-3-haiku', name: 'Claude 3 Haiku', contextLength: 200000, maxTokens: 4096, capabilities: ['text', 'code'], enabled: true }
    ],
    google: [
      { id: 'gemini-pro', name: 'Gemini Pro', contextLength: 30720, maxTokens: 2048, capabilities: ['text', 'code', 'vision'], enabled: true },
      { id: 'gemini-pro-vision', name: 'Gemini Pro Vision', contextLength: 16384, maxTokens: 2048, capabilities: ['text', 'vision'], enabled: true }
    ]
  };

  const handleAddProvider = () => {
    setNewProvider({
      id: '',
      name: '',
      type: 'openai',
      apiKey: '',
      baseUrl: '',
      models: [],
      enabled: true,
      isDefault: false,
      config: {
        maxTokens: 4096,
        temperature: 0.7,
        topP: 1,
        frequencyPenalty: 0,
        presencePenalty: 0,
        timeout: 30000,
        retryAttempts: 3
      }
    });
  };

  const handleSaveNewProvider = () => {
    if (!newProvider?.name || !newProvider.apiKey) return;

    const provider: AIProvider = {
      id: `provider-${Date.now()}`,
      name: newProvider.name,
      type: newProvider.type || 'openai',
      apiKey: newProvider.apiKey,
      baseUrl: newProvider.baseUrl,
      models: newProvider.models?.length ? newProvider.models : (defaultModels[newProvider.type || 'openai'] || []),
      enabled: newProvider.enabled ?? true,
      isDefault: newProvider.isDefault ?? false,
      config: newProvider.config || {}
    };

    setProviders([...providers, provider]);
    setNewProvider(null);
  };

  const handleUpdateProvider = (providerId: string, updates: Partial<AIProvider>) => {
    setProviders(providers.map(p => p.id === providerId ? { ...p, ...updates } : p));
  };

  const handleDeleteProvider = (providerId: string) => {
    if (window.confirm('Are you sure you want to delete this provider?')) {
      setProviders(providers.filter(p => p.id !== providerId));
      if (selectedProvider === providerId) {
        setSelectedProvider(null);
      }
    }
  };

  const handleTestProvider = async (providerId: string) => {
    const provider = providers.find(p => p.id === providerId);
    if (!provider) return;

    setTestResults({ ...testResults, [providerId]: { success: false, message: 'Testing...' } });

    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In a real implementation, you would test the actual API here
      const isValid = provider.apiKey.length > 10;
      
      setTestResults({
        ...testResults,
        [providerId]: {
          success: isValid,
          message: isValid ? 'Connection successful' : 'Invalid API key'
        }
      });
    } catch {
      setTestResults({
        ...testResults,
        [providerId]: {
          success: false,
          message: 'Connection failed'
        }
      });
    }
  };

  const toggleApiKeyVisibility = (providerId: string) => {
    setShowApiKey({ ...showApiKey, [providerId]: !showApiKey[providerId] });
  };

  const toggleEditMode = (providerId: string) => {
    setIsEditing({ ...isEditing, [providerId]: !isEditing[providerId] });
  };

  const toggleModelEnabled = (providerId: string, modelId: string) => {
    setProviders(providers.map(provider => {
      if (provider.id === providerId) {
        return {
          ...provider,
          models: provider.models.map(model =>
            model.id === modelId ? { ...model, enabled: !model.enabled } : model
          )
        };
      }
      return provider;
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Providers</h2>
          <p className="text-muted-foreground">Manage your AI service providers and API configurations</p>
        </div>
        <Button onClick={handleAddProvider} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Provider
        </Button>
      </div>

      {newProvider && (
        <Card className="border-primary">
          <CardHeader>
            <CardTitle>Add New Provider</CardTitle>
            <CardDescription>Configure a new AI service provider</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="provider-name">Provider Name</Label>
                <Input
                  id="provider-name"
                  value={newProvider.name || ''}
                  onChange={(e) => setNewProvider({ ...newProvider, name: e.target.value })}
                  placeholder="My OpenAI Provider"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="provider-type">Provider Type</Label>
                <Select
                  value={newProvider.type || 'openai'}
                  onValueChange={(value: AIProvider['type']) => setNewProvider({ ...newProvider, type: value })}
                >
                  <SelectTrigger id="provider-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {providerTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        <div className="flex items-center gap-2">
                          <type.icon className={`h-4 w-4 ${type.color}`} />
                          {type.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-key">API Key</Label>
              <Input
                id="api-key"
                type="password"
                value={newProvider.apiKey || ''}
                onChange={(e) => setNewProvider({ ...newProvider, apiKey: e.target.value })}
                placeholder="sk-..."
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="base-url">Base URL (Optional)</Label>
              <Input
                id="base-url"
                value={newProvider.baseUrl || ''}
                onChange={(e) => setNewProvider({ ...newProvider, baseUrl: e.target.value })}
                placeholder="https://api.openai.com/v1"
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="enabled"
                  checked={newProvider.enabled ?? true}
                  onCheckedChange={(checked) => setNewProvider({ ...newProvider, enabled: checked })}
                />
                <Label htmlFor="enabled">Enabled</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="default"
                  checked={newProvider.isDefault ?? false}
                  onCheckedChange={(checked) => setNewProvider({ ...newProvider, isDefault: checked })}
                />
                <Label htmlFor="default">Set as Default</Label>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSaveNewProvider}>
                <Save className="h-4 w-4 mr-2" />
                Save Provider
              </Button>
              <Button variant="outline" onClick={() => setNewProvider(null)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={selectedProvider || 'overview'} onValueChange={setSelectedProvider}>
        <TabsList className="grid grid-cols-4 lg:grid-cols-8">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          {providers.map(provider => (
            <TabsTrigger key={provider.id} value={provider.id} className="relative">
              {provider.name}
              {provider.enabled && (
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-500" />
              )}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {providers.map(provider => {
              const providerType = providerTypes.find(t => t.value === provider.type);
              const testResult = testResults[provider.id];
              
              return (
                <Card key={provider.id} className={provider.isDefault ? 'border-primary' : ''}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <div className="flex items-center gap-2">
                      {providerType && (
                        <providerType.icon className={`h-5 w-5 ${providerType.color}`} />
                      )}
                      <CardTitle className="text-sm font-medium">
                        {provider.name}
                      </CardTitle>
                      {provider.isDefault && (
                        <Badge variant="outline" className="text-xs">Default</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {testResult && (
                        <div className="flex items-center">
                          {testResult.success ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      )}
                      <Switch
                        checked={provider.enabled}
                        onCheckedChange={(checked) => handleUpdateProvider(provider.id, { enabled: checked })}
                      />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Type</span>
                        <span>{providerType?.label}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Models</span>
                        <span>{provider.models.filter(m => m.enabled).length}/{provider.models.length}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">API Key</span>
                        <Badge variant={provider.apiKey ? "outline" : "destructive"}>
                          {provider.apiKey ? "Configured" : "Missing"}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestProvider(provider.id)}
                        disabled={!provider.apiKey || testResults[provider.id]?.message === 'Testing...'}
                      >
                        {testResults[provider.id]?.message === 'Testing...' ? (
                          <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                        ) : null}
                        Test
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleEditMode(provider.id)}
                      >
                        <Edit3 className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteProvider(provider.id)}
                      >
                        <Trash2 className="h-3 w-3 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {providers.map(provider => (
          <TabsContent key={provider.id} value={provider.id} className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{provider.name} Configuration</CardTitle>
                <CardDescription>Manage settings for {provider.name}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Basic Configuration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Basic Configuration</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-name`}>Provider Name</Label>
                      <Input
                        id={`${provider.id}-name`}
                        value={provider.name}
                        onChange={(e) => handleUpdateProvider(provider.id, { name: e.target.value })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-type`}>Provider Type</Label>
                      <Input
                        id={`${provider.id}-type`}
                        value={provider.type}
                        disabled
                        className="bg-muted"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={`${provider.id}-api-key`}>API Key</Label>
                    <div className="flex gap-2">
                      <Input
                        id={`${provider.id}-api-key`}
                        type={showApiKey[provider.id] ? "text" : "password"}
                        value={provider.apiKey}
                        onChange={(e) => handleUpdateProvider(provider.id, { apiKey: e.target.value })}
                        disabled={!isEditing[provider.id]}
                        placeholder="sk-..."
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={() => toggleApiKeyVisibility(provider.id)}
                      >
                        {showApiKey[provider.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  {provider.type === 'custom' && (
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-base-url`}>Base URL</Label>
                      <Input
                        id={`${provider.id}-base-url`}
                        value={provider.baseUrl || ''}
                        onChange={(e) => handleUpdateProvider(provider.id, { baseUrl: e.target.value })}
                        disabled={!isEditing[provider.id]}
                        placeholder="https://api.example.com/v1"
                      />
                    </div>
                  )}
                </div>

                {/* Advanced Configuration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Advanced Configuration</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-max-tokens`}>Max Tokens</Label>
                      <Input
                        id={`${provider.id}-max-tokens`}
                        type="number"
                        value={provider.config.maxTokens || 4096}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, maxTokens: parseInt(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-temperature`}>Temperature</Label>
                      <Input
                        id={`${provider.id}-temperature`}
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        value={provider.config.temperature || 0.7}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, temperature: parseFloat(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-top-p`}>Top P</Label>
                      <Input
                        id={`${provider.id}-top-p`}
                        type="number"
                        step="0.1"
                        min="0"
                        max="1"
                        value={provider.config.topP || 1}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, topP: parseFloat(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-frequency-penalty`}>Frequency Penalty</Label>
                      <Input
                        id={`${provider.id}-frequency-penalty`}
                        type="number"
                        step="0.1"
                        min="-2"
                        max="2"
                        value={provider.config.frequencyPenalty || 0}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, frequencyPenalty: parseFloat(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-presence-penalty`}>Presence Penalty</Label>
                      <Input
                        id={`${provider.id}-presence-penalty`}
                        type="number"
                        step="0.1"
                        min="-2"
                        max="2"
                        value={provider.config.presencePenalty || 0}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, presencePenalty: parseFloat(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-timeout`}>Timeout (ms)</Label>
                      <Input
                        id={`${provider.id}-timeout`}
                        type="number"
                        value={provider.config.timeout || 30000}
                        onChange={(e) => handleUpdateProvider(provider.id, { 
                          config: { ...provider.config, timeout: parseInt(e.target.value) }
                        })}
                        disabled={!isEditing[provider.id]}
                      />
                    </div>
                  </div>
                </div>

                {/* Model Configuration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Available Models</h3>
                  <div className="space-y-2">
                    {provider.models.map(model => (
                      <Card key={model.id} className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <Switch
                              checked={model.enabled}
                              onCheckedChange={() => toggleModelEnabled(provider.id, model.id)}
                            />
                            <div>
                              <h4 className="font-medium">{model.name}</h4>
                              <p className="text-sm text-muted-foreground">{model.id}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <div className="text-right">
                              <div className="text-muted-foreground">Context</div>
                              <div>{(model.contextLength / 1000).toFixed(0)}k</div>
                            </div>
                            <div className="text-right">
                              <div className="text-muted-foreground">Max Tokens</div>
                              <div>{(model.maxTokens / 1000).toFixed(0)}k</div>
                            </div>
                            <div>
                              {model.capabilities.map(cap => (
                                <Badge key={cap} variant="secondary" className="mr-1 text-xs">
                                  {cap}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button onClick={() => handleTestProvider(provider.id)} disabled={!provider.apiKey}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Test Connection
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => toggleEditMode(provider.id)}
                  >
                    {isEditing[provider.id] ? (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    ) : (
                      <>
                        <Edit3 className="h-4 w-4 mr-2" />
                        Edit Configuration
                      </>
                    )}
                  </Button>
                  {testResults[provider.id] && (
                    <Alert className={testResults[provider.id].success ? 'border-green-500' : 'border-red-500'}>
                      <AlertDescription className="flex items-center gap-2">
                        {testResults[provider.id].success ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        )}
                        {testResults[provider.id].message}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default ProviderConfig;
