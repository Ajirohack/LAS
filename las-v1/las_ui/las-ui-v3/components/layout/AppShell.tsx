'use client';

import { useAppStore } from '@/app/store';
import { SettingsDialog } from '../settings/SettingsDialog';
import { CommandBar } from './CommandBar';
import { Sidebar } from './Sidebar';
import { Inspector } from './Inspector';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, MessageSquare, Workflow, Brain, Settings, Command } from 'lucide-react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts';

export function AppShell({ children }: { children: React.ReactNode }) {
    const { 
        sidebarOpen, 
        toggleSidebar, 
        activePanel, 
        setActivePanel,
        openCommandBar 
    } = useAppStore();
    const router = useRouter();

    const navItems = [
        { id: 'chat', label: 'Chat', icon: MessageSquare },
        { id: 'workflow', label: 'Workflows', icon: Workflow },
        { id: 'memory', label: 'Memory', icon: Brain },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    const handleNavigation = (panelId: string) => {
        if (panelId === 'settings') return; // Settings opens a dialog, not a page

        const routes: Record<string, string> = {
            chat: '/',
            workflow: '/workflow',
            memory: '/memory',
        };

        setActivePanel(panelId as 'chat' | 'workflow' | 'memory' | 'settings');
        router.push(routes[panelId] || '/');
    };

    useKeyboardShortcuts([
        { combo: { key: '1', meta: true }, handler: () => handleNavigation('chat') },
        { combo: { key: '2', meta: true }, handler: () => handleNavigation('workflow') },
        { combo: { key: '3', meta: true }, handler: () => handleNavigation('memory') },
        { combo: { key: 'k', meta: true }, handler: openCommandBar },
        { combo: { key: 'b', meta: true }, handler: toggleSidebar },
    ]);

    return (
        <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
            {/* Command Bar */}
            <CommandBar />
            
            {/* Sidebar */}
            <AnimatePresence mode="wait">
                {sidebarOpen && (
                    <motion.aside
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 320, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeOut' }}
                        className="glass-panel border-r border-border flex flex-col"
                    >
                        <Sidebar />
                    </motion.aside>
                )}
            </AnimatePresence>

            {/* Main Content */}
            <main className="flex-1 flex flex-col relative min-w-0">
                {/* Top Bar */}
                {!sidebarOpen && (
                    <div className="glass-panel border-b border-border p-4 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={toggleSidebar}
                                className="p-2 hover:bg-zinc-800 rounded-md transition-colors"
                            >
                                <Menu className="w-5 h-5" />
                            </button>
                            
                            {/* Quick Command Bar Access */}
                            <button
                                onClick={openCommandBar}
                                className="flex items-center gap-2 px-3 py-2 hover:bg-zinc-800 rounded-md transition-colors text-sm text-muted-foreground"
                            >
                                <Command className="w-4 h-4" />
                                <span>Search commands...</span>
                                <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
                                  ⌘K
                                </kbd>
                            </button>
                        </div>
                        
                        {/* Status Indicators */}
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                <span>Online</span>
                            </div>
                            <div>GPT-4</div>
                        </div>
                    </div>
                )}

                {/* Content Area */}
                <div className="flex-1 overflow-hidden">
                    {children}
                </div>
            </main>

            {/* Right Inspector Panel */}
            <Inspector />
        </div>
    );
}
