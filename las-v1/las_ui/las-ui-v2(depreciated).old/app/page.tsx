"use client";

import React, { useState } from 'react';
import { ChatInterface } from '@/components/chat-interface';
import { TaskManager } from '@/components/task-manager';
import { MemoryViewer } from '@/components/memory-viewer';
import { Sidebar } from '@/components/sidebar';
import { ArtifactView } from '@/components/artifact-view';
import { WorkflowBuilder } from '@/components/workflow-builder';

export default function Home() {
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [artifactContent, setArtifactContent] = useState('// Example code\nconsole.log("Hello World");');
  const [activeView, setActiveView] = useState('chat');

  return (
    <main className="flex min-h-screen bg-muted/10 overflow-hidden">
      {/* Sidebar */}
      <Sidebar activeView={activeView} onNavigate={setActiveView} />

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-background z-10">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold">
              L
            </div>
            <h1 className="font-bold text-xl tracking-tight">LAS <span className="font-normal text-muted-foreground">Dashboard</span></h1>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>v2.0.0</span>
            <div className="h-4 w-[1px] bg-border"></div>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              System Online
            </span>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {activeView === 'chat' ? (
            /* Chat Column */
            <div className="flex-1 flex flex-col p-4 gap-6 overflow-y-auto">
              <ChatInterface />

              {/* Bottom Panels */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TaskManager />
                <MemoryViewer />
              </div>
            </div>
          ) : (
            /* Workflow Builder View */
            <div className="flex-1 p-4 overflow-hidden">
              <WorkflowBuilder />
            </div>
          )}

          {/* Artifact View (Right Panel) */}
          {showArtifacts && (
            <div className="w-[500px] border-l bg-background h-full">
              <ArtifactView
                isOpen={showArtifacts}
                onClose={() => setShowArtifacts(false)}
                content={artifactContent}
              />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
