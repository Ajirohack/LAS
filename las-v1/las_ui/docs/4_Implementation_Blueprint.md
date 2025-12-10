# LAS UI - Implementation Blueprint

**Version:** 1.0
**Stack:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn UI, Zustand, React Query.

---

## 1. Initialization

```bash
# 1. Create Next.js App
npx create-next-app@latest las-ui --typescript --tailwind --eslint
cd las-ui

# 2. Install Dependencies
npm install axios @tanstack/react-query zustand framer-motion lucide-react clsx tailwind-merge
npm install reactflow d3-force react-markdown react-syntax-highlighter
npm install socket.io-client # For real-time streaming

# 3. Initialize Shadcn UI
npx shadcn-ui@latest init
# (Select: Slate, CSS Variables, default config)

# 4. Install Core Components
npx shadcn-ui@latest add button input card sheet dialog dropdown-menu avatar separator scroll-area tooltip badge accordion
```

---

## 2. Global State Management (`lib/store.ts`)

We use **Zustand** for a lightweight, performant global store.

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  activePanel: 'chat' | 'workflow' | 'memory';
  setActivePanel: (panel: 'chat' | 'workflow' | 'memory') => void;

  // Agent State
  selectedProvider: string;
  selectedModel: string;
  setProvider: (provider: string, model: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      activePanel: 'chat',
      setActivePanel: (panel) => set({ activePanel: panel }),
      
      selectedProvider: 'openai',
      selectedModel: 'gpt-4',
      setProvider: (provider, model) => set({ selectedProvider: provider, selectedModel: model }),
    }),
    { name: 'las-ui-storage' }
  )
);
```

---

## 3. API Client & AI SDK Setup

We use **Vercel AI SDK** for robust streaming and state management.

```bash
npm install ai
```

### `app/api/chat/route.ts` (Backend Handler)

```typescript
import { OpenAIStream, StreamingTextResponse } from 'ai';
import { Configuration, OpenAIApi } from 'openai-edge';

// Connect to LAS Backend
const config = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
  basePath: 'http://localhost:8080/api/v1', // Proxy to LAS Core
});
const openai = new OpenAIApi(config);

export async function POST(req: Request) {
  const { messages } = await req.json();
  const response = await openai.createChatCompletion({
    model: 'gpt-4',
    stream: true,
    messages,
  });
  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
}
```

---

## 4. Main Layout (`components/layout/AppShell.tsx`)

The responsive grid container.

```tsx
'use client';

import { Sidebar } from './Sidebar';
import { Inspector } from './Inspector';
import { useAppStore } from '@/lib/store';
import { motion, AnimatePresence } from 'framer-motion';

export function AppShell({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useAppStore();

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-zinc-100 overflow-hidden">
      {/* Left Sidebar */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="border-r border-white/10 bg-zinc-900/50 backdrop-blur-xl"
          >
            <Sidebar />
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative min-w-0">
        {children}
      </main>

      {/* Right Inspector (Optional/Collapsible) */}
      <aside className="w-80 border-l border-white/10 bg-zinc-900/50 hidden xl:block">
        <Inspector />
      </aside>
    </div>
  );
}
```

---

## 5. Streaming Chat Component (`components/chat/ChatInterface.tsx`)

Using Vercel AI SDK `useChat` hook.

```tsx
'use client';

import { useChat } from 'ai/react';
import { MessageList } from './MessageList';
import { InputDeck } from './InputDeck';

export function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, stop } = useChat({
    api: '/api/chat',
    initialMessages: [],
  });

  return (
    <div className="flex flex-col h-full relative">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <MessageList messages={messages} />
        {isLoading && (
          <div className="flex justify-center">
            <button onClick={stop} className="text-xs bg-red-500/10 text-red-400 px-3 py-1 rounded-full border border-red-500/20">
              Stop Generating
            </button>
          </div>
        )}
      </div>

      {/* Input Deck */}
      <div className="p-4 border-t border-white/10 bg-zinc-900/50 backdrop-blur-md">
        <InputDeck 
          value={input} 
          onChange={handleInputChange} 
          onSubmit={handleSubmit} 
          loading={isLoading} 
        />
      </div>
    </div>
  );
}
```

---

## 6. Next Steps for Developer

1. **Setup:** Run the initialization commands in Section 1.
2. **Scaffold:** Create the directory structure defined in the Wireframes doc.
3. **Auth:** Implement the Login page using the `api.ts` client.
4. **Core:** Build the `AppShell` and `ChatInterface`.
5. **Advanced:** Integrate React Flow for the Workflow Builder.
