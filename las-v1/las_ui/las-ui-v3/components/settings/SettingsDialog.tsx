import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

import { useAppStore } from "@/app/store";
import {
  Settings,
  User,
  Palette,
  Bell,
  Keyboard,
  Database,
  Shield,
  Zap,
} from "lucide-react";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface SettingsSection {
  general: {
    appName: string;
    language: string;
    timezone: string;
    dateFormat: string;
    timeFormat: string;
    startOnBoot: boolean;
    minimizeToTray: boolean;
    checkUpdates: boolean;
  };
  appearance: {
    theme: "light" | "dark" | "system";
    fontSize: "small" | "medium" | "large";
    fontFamily: string;
    accentColor: string;
    sidebarWidth: number;
    chatWidth: number;
    compactMode: boolean;
    animations: boolean;
    transparency: boolean;
    glassEffect: boolean;
  };
  notifications: {
    enableNotifications: boolean;
    soundEnabled: boolean;
    desktopNotifications: boolean;
    emailNotifications: boolean;
    messagePreview: boolean;
    notificationSound: string;
    notificationVolume: number;
    quietHours: {
      enabled: boolean;
      start: string;
      end: string;
    };
  };
  shortcuts: {
    toggleSidebar: string;
    openCommandBar: string;
    newChat: string;
    sendMessage: string;
    toggleInspector: string;
    toggleFullscreen: string;
    zoomIn: string;
    zoomOut: string;
    resetZoom: string;
  };
  ai: {
    defaultProvider: string;
    defaultModel: string;
    maxTokens: number;
    temperature: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
    timeout: number;
    retryAttempts: number;
    enableStreaming: boolean;
    enableMemory: boolean;
    memoryLimit: number;
  };
  memory: {
    enableMemory: boolean;
    maxNodes: number;
    autoSave: boolean;
    saveInterval: number;
    compressionThreshold: number;
    enableSearch: boolean;
    searchLimit: number;
  };
  privacy: {
    enableTelemetry: boolean;
    shareUsageData: boolean;
    storeMessagesLocally: boolean;
    encryptLocalData: boolean;
    autoDeleteMessages: boolean;
    messageRetentionDays: number;
    enableAnalytics: boolean;
  };
  advanced: {
    enableDebugMode: boolean;
    logLevel: "error" | "warn" | "info" | "debug";
    enableExperimental: boolean;
    customCSS: string;
    customJS: string;
    apiEndpoint: string;
    websocketUrl: string;
    maxConcurrentRequests: number;
    requestTimeout: number;
    cacheEnabled: boolean;
    cacheSize: number;
  };
}

const SettingsDialog: React.FC<SettingsDialogProps> = ({
  open,
  onOpenChange,
}) => {
  const { theme, setTheme, selectedProvider, selectedModel, setProvider } =
    useAppStore();

  const [settings, setSettings] = useState<SettingsSection>({
    general: {
      appName: "LAS - Local Agent System",
      language: "en",
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      dateFormat: "MM/DD/YYYY",
      timeFormat: "12h",
      startOnBoot: false,
      minimizeToTray: true,
      checkUpdates: true,
    },
    appearance: {
      theme: theme,
      fontSize: "medium",
      fontFamily: "Inter",
      accentColor: "#3b82f6",
      sidebarWidth: 280,
      chatWidth: 800,
      compactMode: false,
      animations: true,
      transparency: true,
      glassEffect: true,
    },
    notifications: {
      enableNotifications: true,
      soundEnabled: true,
      desktopNotifications: true,
      emailNotifications: false,
      messagePreview: true,
      notificationSound: "default",
      notificationVolume: 0.5,
      quietHours: {
        enabled: false,
        start: "22:00",
        end: "08:00",
      },
    },
    shortcuts: {
      toggleSidebar: "Cmd+\\",
      openCommandBar: "Cmd+K",
      newChat: "Cmd+N",
      sendMessage: "Enter",
      toggleInspector: "Cmd+I",
      toggleFullscreen: "F11",
      zoomIn: "Cmd+Plus",
      zoomOut: "Cmd+-",
      resetZoom: "Cmd+0",
    },
    ai: {
      defaultProvider: selectedProvider,
      defaultModel: selectedModel,
      maxTokens: 4096,
      temperature: 0.7,
      topP: 1,
      frequencyPenalty: 0,
      presencePenalty: 0,
      timeout: 30000,
      retryAttempts: 3,
      enableStreaming: true,
      enableMemory: true,
      memoryLimit: 1000,
    },
    memory: {
      enableMemory: true,
      maxNodes: 1000,
      autoSave: true,
      saveInterval: 30000,
      compressionThreshold: 100,
      enableSearch: true,
      searchLimit: 50,
    },
    privacy: {
      enableTelemetry: false,
      shareUsageData: false,
      storeMessagesLocally: true,
      encryptLocalData: true,
      autoDeleteMessages: false,
      messageRetentionDays: 30,
      enableAnalytics: false,
    },
    advanced: {
      enableDebugMode: false,
      logLevel: "warn",
      enableExperimental: false,
      customCSS: "",
      customJS: "",
      apiEndpoint: "https://api.openai.com/v1",
      websocketUrl: "ws://localhost:8080",
      maxConcurrentRequests: 5,
      requestTimeout: 30000,
      cacheEnabled: true,
      cacheSize: 100,
    },
  });

  useEffect(() => {
    setSettings((prev) => ({
      ...prev,
      appearance: { ...prev.appearance, theme },
      ai: {
        ...prev.ai,
        defaultProvider: selectedProvider,
        defaultModel: selectedModel,
      },
    }));
  }, [theme, selectedProvider, selectedModel]);

  const updateSetting = <K extends keyof SettingsSection>(
    section: K,
    updates: Partial<SettingsSection[K]>
  ) => {
    setSettings((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...updates },
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Settings
          </DialogTitle>
          <DialogDescription>
            Configure your LAS experience across all modules
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          <Tabs defaultValue="general" className="h-full">
            <TabsList className="grid grid-cols-4 lg:grid-cols-8">
              <TabsTrigger value="general" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                General
              </TabsTrigger>
              <TabsTrigger
                value="appearance"
                className="flex items-center gap-2">
                <Palette className="h-4 w-4" />
                Appearance
              </TabsTrigger>
              <TabsTrigger
                value="notifications"
                className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                Notifications
              </TabsTrigger>
              <TabsTrigger
                value="shortcuts"
                className="flex items-center gap-2">
                <Keyboard className="h-4 w-4" />
                Shortcuts
              </TabsTrigger>
              <TabsTrigger value="ai" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                AI
              </TabsTrigger>
              <TabsTrigger value="memory" className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                Memory
              </TabsTrigger>
              <TabsTrigger value="privacy" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Privacy
              </TabsTrigger>
              <TabsTrigger value="advanced" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Advanced
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {/* General Settings */}
              <TabsContent value="general" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Application Settings</CardTitle>
                    <CardDescription>
                      Configure basic application behavior
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="app-name">Application Name</Label>
                        <Input
                          id="app-name"
                          value={settings.general.appName}
                          onChange={(e) =>
                            updateSetting("general", {
                              appName: e.target.value,
                            })
                          }
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="language">Language</Label>
                        <Select
                          value={settings.general.language}
                          onValueChange={(value) =>
                            updateSetting("general", { language: value })
                          }>
                          <SelectTrigger id="language">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="en">English</SelectItem>
                            <SelectItem value="es">Spanish</SelectItem>
                            <SelectItem value="fr">French</SelectItem>
                            <SelectItem value="de">German</SelectItem>
                            <SelectItem value="zh">Chinese</SelectItem>
                            <SelectItem value="ja">Japanese</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="date-format">Date Format</Label>
                        <Select
                          value={settings.general.dateFormat}
                          onValueChange={(value) =>
                            updateSetting("general", { dateFormat: value })
                          }>
                          <SelectTrigger id="date-format">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="MM/DD/YYYY">
                              MM/DD/YYYY
                            </SelectItem>
                            <SelectItem value="DD/MM/YYYY">
                              DD/MM/YYYY
                            </SelectItem>
                            <SelectItem value="YYYY-MM-DD">
                              YYYY-MM-DD
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="time-format">Time Format</Label>
                        <Select
                          value={settings.general.timeFormat}
                          onValueChange={(value) =>
                            updateSetting("general", { timeFormat: value })
                          }>
                          <SelectTrigger id="time-format">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="12h">12 Hour</SelectItem>
                            <SelectItem value="24h">24 Hour</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="start-on-boot"
                          checked={settings.general.startOnBoot}
                          onCheckedChange={(checked) =>
                            updateSetting("general", { startOnBoot: checked })
                          }
                        />
                        <Label htmlFor="start-on-boot">
                          Start on system boot
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="minimize-to-tray"
                          checked={settings.general.minimizeToTray}
                          onCheckedChange={(checked) =>
                            updateSetting("general", {
                              minimizeToTray: checked,
                            })
                          }
                        />
                        <Label htmlFor="minimize-to-tray">
                          Minimize to system tray
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="check-updates"
                          checked={settings.general.checkUpdates}
                          onCheckedChange={(checked) =>
                            updateSetting("general", { checkUpdates: checked })
                          }
                        />
                        <Label htmlFor="check-updates">
                          Check for updates automatically
                        </Label>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SettingsDialog;
