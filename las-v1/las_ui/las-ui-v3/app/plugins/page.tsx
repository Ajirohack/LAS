"use client";

import { PluginStore } from "@/components/plugins/PluginStore";
import { Separator } from "@/components/ui/separator";

export default function PluginsPage() {
    return (
        <div className="flex h-screen flex-col bg-background">
            <div className="flex-1 space-y-4 p-8 pt-6">
                <div className="flex items-center justify-between space-y-2">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Plugin Marketplace</h2>
                        <p className="text-muted-foreground">
                            Discover and install extensions to enhance your agent&apos;s capabilities.
                        </p>
                    </div>
                </div>
                <Separator />
                <PluginStore />
            </div>
        </div>
    );
}
