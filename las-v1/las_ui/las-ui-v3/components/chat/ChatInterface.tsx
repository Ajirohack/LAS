"use client";

import { useState, useEffect, useRef } from "react";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";

import { useStream } from "@/hooks/use-stream";
import { lasApi } from "@/app/api-client";
import { ToolInvocation } from "./ToolInvocation";
import { useAppStore } from "@/app/store";
import { PromptInput } from "../ui/prompt-input";
import { ChatSkeleton } from "../ui/loading-skeleton";
import { ThoughtChain, ThoughtStep } from "./ThoughtChain";
import { MessageVirtualizer } from "./MessageVirtualizer";
import { Brain, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

// Define specific types for tool data
interface ToolData {
  tool: string;
  input: Record<string, unknown>;
  output?: unknown;
  status: "running" | "completed" | "failed";
}

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  tools?: ToolData[];
  attachments?: Array<File & { metadata?: { name?: string } }>;
  error?: string;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
  };
}

interface ChatInterfaceProps {
  className?: string;
  showThoughtChain?: boolean;
  showMessageVirtualizer?: boolean;
  onMessageEdit?: (messageId: string, newContent: string) => void;
  onMessageDelete?: (messageId: string) => void;
}

export function ChatInterface({
  className = "",
  showThoughtChain = true,
  showMessageVirtualizer = true,
  onMessageEdit,
  onMessageDelete,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [thoughtSteps, setThoughtSteps] = useState<ThoughtStep[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const [activeTab, setActiveTab] = useState<"messages" | "thoughts">(
    "messages"
  );
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevStreamLengthRef = useRef(0);

  const { selectedProvider, selectedModel } = useAppStore();
  const {
    isConnected,
    sendMessage,
    messages: streamMessages,
    clearMessages,
  } = useStream();

  // Convert messages to ChatMessage format for virtualizer
  const chatMessages = messages.map((msg) => ({
    id: msg.id,
    role: msg.role,
    content: msg.content,
    timestamp: msg.timestamp.toISOString(),
    error: msg.error,
    metadata: msg.metadata,
    tools: msg.tools,
    attachments: msg.attachments?.map((f) => ({
      name: f.metadata?.name || f.name,
      type: f.type,
      size: f.size,
    })),
  }));

  // Handle stream completion separately
  useEffect(() => {
    if (streamMessages.length === 0) return;
    const lastMsg = streamMessages[streamMessages.length - 1];
    if (lastMsg.type === "complete" && isLoading) {
      setIsLoading(false);
      setIsThinking(false);
    }
  }, [streamMessages, isLoading]);

  // Handle incoming stream messages and update chat messages
  useEffect(() => {
    // Only process new messages
    if (streamMessages.length <= prevStreamLengthRef.current) return;

    const lastMsg = streamMessages[streamMessages.length - 1];

    // Skip completion messages (handled elsewhere)
    if (lastMsg.type === "complete") {
      prevStreamLengthRef.current = streamMessages.length;
      return;
    }

    // Update messages based on stream type
    if (lastMsg.type === "token" || lastMsg.type === "tool") {
      prevStreamLengthRef.current = streamMessages.length;

      setMessages((prev) => {
        const newHistory = [...prev];
        const lastHistoryMsg = newHistory[newHistory.length - 1];

        if (lastHistoryMsg && lastHistoryMsg.role === "assistant") {
          // Update existing assistant message
          if (lastMsg.type === "token") {
            return [
              ...newHistory.slice(0, -1),
              {
                ...lastHistoryMsg,
                content: lastHistoryMsg.content + lastMsg.data,
              },
            ];
          } else if (lastMsg.type === "tool") {
            const tools = lastHistoryMsg.tools || [];
            return [
              ...newHistory.slice(0, -1),
              {
                ...lastHistoryMsg,
                tools: [...tools, lastMsg.data as ToolData],
              },
            ];
          }
        } else if (lastMsg.type === "token") {
          // Start new assistant message
          return [
            ...newHistory,
            {
              id: `msg-${Date.now()}`,
              role: "assistant",
              content: lastMsg.data as string,
              timestamp: new Date(),
              tools: [],
            },
          ];
        }

        return newHistory;
      });
    }
  }, [streamMessages]);
  

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current && activeTab === "messages") {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, activeTab]);

  // Simulate thought process for demonstration
  const simulateThoughtProcess = (userInput: string) => {
    setIsThinking(true);
    setThoughtSteps([]);

    const steps: ThoughtStep[] = [
      {
        id: "step-1",
        type: "reasoning",
        title: "Analyzing user query",
        content: `Understanding the user's request: "${userInput}"`,
        timestamp: new Date(),
        status: "running",
        duration: 150,
        metadata: {
          model: selectedModel,
          tokens: 45,
        },
      },
      {
        id: "step-2",
        type: "tool_call",
        title: "Searching knowledge base",
        content: "Retrieving relevant information from memory",
        timestamp: new Date(),
        status: "pending",
        duration: 300,
        tool: {
          name: "memory_search",
          input: { query: userInput, limit: 10 },
        },
        metadata: {
          model: selectedModel,
          tokens: 120,
        },
      },
      {
        id: "step-3",
        type: "observation",
        title: "Processing search results",
        content: "Analyzing retrieved information and context",
        timestamp: new Date(),
        status: "pending",
        duration: 200,
        metadata: {
          model: selectedModel,
          tokens: 89,
        },
      },
      {
        id: "step-4",
        type: "reflection",
        title: "Evaluating response quality",
        content: "Checking if the response meets user requirements",
        timestamp: new Date(),
        status: "pending",
        duration: 100,
        metadata: {
          model: selectedModel,
          tokens: 34,
          confidence: 0.92,
        },
      },
      {
        id: "step-5",
        type: "decision",
        title: "Finalizing response",
        content: "Preparing the final answer for the user",
        timestamp: new Date(),
        status: "pending",
        duration: 50,
        metadata: {
          model: selectedModel,
          tokens: 28,
        },
      },
    ];

    // Simulate step-by-step execution
    steps.forEach((step, index) => {
      setTimeout(() => {
        setThoughtSteps((prev) => {
          const updated = [...prev];
          if (index > 0) {
            updated[index - 1] = { ...updated[index - 1], status: "completed" };
          }
          updated[index] = { ...step, status: "running" };
          return updated;
        });
      }, index * 200);
    });

    // Complete the last step
    setTimeout(() => {
      setThoughtSteps((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          status: "completed",
        };
        return updated;
      });
    }, steps.length * 200);
  };

  const handleSubmit = async (
    input: string,
    files: Array<File & { metadata?: { name?: string } }>
  ) => {
    if (!input.trim() && files.length === 0) return;
    if (isLoading) return;

    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
      attachments: files,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    clearMessages();
    prevStreamLengthRef.current = 0;

    // Simulate thought process
    if (showThoughtChain) {
      simulateThoughtProcess(input);
    }

    try {
      // Send to backend via WebSocket if connected, else fallback to REST
      if (isConnected) {
        sendMessage({
          query: input,
          provider: selectedProvider,
          model: selectedModel,
          stream: true,
        });
      } else {
        // Fallback to REST API
        const res = await lasApi.query({
          query: input,
          provider: selectedProvider,
          model: selectedModel,
        });

        setMessages((prev) => [
          ...prev,
          {
            id: `msg-${Date.now()}`,
            role: "assistant",
            content: res.response,
            timestamp: new Date(),
            tools: [],
            metadata: {
              model: selectedModel,
              tokens: res.metadata?.tokens,
            },
          },
        ]);
        setIsLoading(false);
        setIsThinking(false);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          role: "system",
          content: "Error connecting to LAS backend. Is it running?",
          timestamp: new Date(),
          error: error instanceof Error ? error.message : "Unknown error",
        },
      ]);
      setIsLoading(false);
      setIsThinking(false);
    }
  };

  const handleMessageEdit = (messageId: string, newContent: string) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, content: newContent } : msg
      )
    );
    if (onMessageEdit) {
      onMessageEdit(messageId, newContent);
    }
  };

  const handleMessageDelete = (messageId: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    if (onMessageDelete) {
      onMessageDelete(messageId);
    }
  };

  return (
    <div className={cn("flex flex-col h-full w-full", className)}>
      {/* Tab Navigation */}
      {showThoughtChain && (
        <div className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <Tabs
            value={activeTab}
            onValueChange={(value) =>
              setActiveTab(value as "messages" | "thoughts")
            }>
            <TabsList className="w-full justify-start rounded-none h-12 bg-transparent p-0">
              <TabsTrigger
                value="messages"
                className="flex-1 data-[state=active]:bg-background data-[state=active]:shadow-none rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
                <MessageSquare className="w-4 h-4 mr-2" />
                Messages
              </TabsTrigger>
              <TabsTrigger
                value="thoughts"
                className="flex-1 data-[state=active]:bg-background data-[state=active]:shadow-none rounded-none border-b-2 border-transparent data-[state=active]:border-primary">
                <Brain className="w-4 h-4 mr-2" />
                Thoughts
                {isThinking && (
                  <span className="ml-2 w-2 h-2 bg-primary rounded-full animate-pulse" />
                )}
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      )}

      {/* Content Area */}
      <div className="flex-1 relative">
        {/* Messages Tab */}
        {activeTab === "messages" &&
          (showMessageVirtualizer ? (
            <div className="h-full">
              <MessageVirtualizer
                messages={chatMessages}
                isLoading={isLoading}
                onMessageEdit={handleMessageEdit}
                onMessageDelete={handleMessageDelete}
                className="h-full"
              />
            </div>
          ) : (
            <ScrollArea className="h-full" ref={scrollRef}>
              <div className="max-w-4xl mx-auto">
                <div className="space-y-6 p-6">
                  {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center py-20">
                      <div className="w-16 h-16 mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                        <div className="w-8 h-8 rounded-full bg-primary/20" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">
                        Start a Conversation
                      </h3>
                      <p className="text-sm text-foreground-muted max-w-md">
                        Ask me anything. I&apos;ll use my tools and context to
                        help you.
                      </p>
                    </div>
                  )}

                  {messages.map((msg, idx) => (
                    <div
                      key={msg.id}
                      className={`flex ${
                        msg.role === "user" ? "justify-end" : "justify-start"
                      }`}>
                      <div
                        className={`
                                max-w-[85%] rounded-xl px-4 py-3
                                ${
                                  msg.role === "user"
                                    ? "bg-primary text-white"
                                    : msg.role === "assistant"
                                    ? "glass-panel"
                                    : "bg-error/10 text-error"
                                }
                            `}>
                        <div className="text-sm prose dark:prose-invert max-w-none prose-p:my-2 prose-pre:my-0">
                          {msg.content}
                        </div>

                        {msg.attachments && msg.attachments.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {msg.attachments.map((file, i) => (
                              <div
                                key={i}
                                className="text-xs bg-black/20 rounded px-2 py-1 flex items-center gap-1">
                                <span>📎</span>
                                <span className="truncate max-w-[150px]">
                                  {file.metadata?.name}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}

                        {msg.tools && msg.tools.length > 0 && (
                          <div className="mt-3 space-y-1">
                            {msg.tools.map((tool, tIdx) => (
                              <ToolInvocation key={tIdx} {...tool} />
                            ))}
                          </div>
                        )}

                        <div className="text-xs opacity-60 mt-2">
                          {msg.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start w-full">
                      <div className="max-w-2xl w-full">
                        <ChatSkeleton />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </ScrollArea>
          ))}

        {/* Thoughts Tab */}
        {activeTab === "thoughts" && (
          <div className="h-full overflow-auto">
            <ThoughtChain
              steps={thoughtSteps}
              isActive={isThinking}
              className="h-full border-0 rounded-none"
            />
          </div>
        )}
      </div>

      {/* Input Deck */}
      <div className="glass-panel border-t border-border p-4">
        <div className="max-w-4xl mx-auto">
          <PromptInput
            onSubmit={handleSubmit}
            isLoading={isLoading}
            onStop={() => {
              setIsLoading(false);
              setIsThinking(false);
            }}
          />
          <div className="flex items-center justify-between mt-2 text-xs text-foreground-muted px-1">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {selectedModel}
              </Badge>
              <span>•</span>
              <span>
                Context:{" "}
                {messages.reduce(
                  (acc, msg) => acc + (msg.metadata?.tokens || 0),
                  0
                )}{" "}
                tokens
              </span>
            </div>
            <span>Press Enter to send, Shift+Enter for new line</span>
          </div>
        </div>
      </div>
    </div>
  );
}
