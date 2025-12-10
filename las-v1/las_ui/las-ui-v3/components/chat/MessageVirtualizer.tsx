"use client";

import { useVirtualScroll } from "@/hooks/use-virtual-scroll";
import { useCallback, useMemo } from "react";
import { formatRelativeTime } from "@/lib/utils";
import { ToolInvocation } from "./ToolInvocation";
import { User, Bot, Loader2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToolData {
  tool: string;
  input: Record<string, unknown>;
  output?: unknown;
  status: "running" | "completed" | "failed";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  tools?: ToolData[];
  attachments?: Array<{ name?: string; type?: string; size?: number }>;
  error?: string;
  metadata?: {
    model?: string;
    tokens?: number;
    cost?: number;
  };
}

interface MessageVirtualizerProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onMessageEdit?: (messageId: string, newContent: string) => void;
  onMessageDelete?: (messageId: string) => void;
  className?: string;
  itemSize?: number;
  overscan?: number;
}

export function MessageVirtualizer({
  messages,
  isLoading = false,
  onMessageEdit,
  onMessageDelete,
  className = "",
  itemSize = 120,
  overscan = 5,
}: MessageVirtualizerProps) {
  // Use our custom hook which handles auto-scrolling
  const { parentRef, rowVirtualizer } = useVirtualScroll({
    count: messages.length,
    estimateSize: useCallback(() => itemSize, [itemSize]),
    overscan,
    autoScroll: true, // Enable auto-scroll behavior
  });

  // Get virtual items
  const virtualItems = rowVirtualizer.getVirtualItems();
  const totalSize = rowVirtualizer.getTotalSize();

  // Memoize message rendering to prevent unnecessary re-renders
  const renderMessage = useCallback(
    (message: ChatMessage, index: number) => {
      const isUser = message.role === "user";
      const isLastMessage = index === messages.length - 1;
      const isAssistantLoading = isLoading && isLastMessage && !isUser;

      return (
        <div
          key={message.id}
          data-index={index}
          ref={rowVirtualizer.measureElement}
          className={cn(
            "group relative py-4 px-6 transition-colors",
            isUser ? "bg-muted/30" : "bg-background",
            "hover:bg-accent/5"
          )}>
          <div className="max-w-4xl mx-auto">
            {/* Message Header */}
            <div className="flex items-start gap-4">
              {/* Avatar */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-primary to-primary/60">
                {isUser ? (
                  <User className="w-4 h-4 text-primary-foreground" />
                ) : (
                  <Bot className="w-4 h-4 text-primary-foreground" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium text-sm capitalize">
                    {message.role}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatRelativeTime(new Date(message.timestamp))}
                  </span>
                  {message.metadata?.model && (
                    <span className="text-xs text-muted-foreground">
                      • {message.metadata.model}
                    </span>
                  )}
                </div>

                {/* Message Content */}
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <div
                    className={cn(
                      "whitespace-pre-wrap break-words",
                      isAssistantLoading && "animate-pulse"
                    )}>
                    {message.content}
                    {isAssistantLoading && (
                      <span className="inline-flex items-center ml-2">
                        <Loader2 className="w-3 h-3 animate-spin" />
                      </span>
                    )}
                  </div>
                </div>

                {/* Attachments */}
                {message.attachments && message.attachments.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {message.attachments.map((file, i) => (
                      <div
                        key={i}
                        className="text-xs bg-black/20 rounded px-2 py-1 flex items-center gap-1">
                        <span>📎</span>
                        <span className="truncate max-w-[150px]">
                          {file.name || "Attachment"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Tools */}
                {message.tools && message.tools.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {message.tools.map((tool, tIdx) => (
                      <ToolInvocation key={tIdx} {...tool} />
                    ))}
                  </div>
                )}

                {/* Error State */}
                {message.error && (
                  <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-red-700">{message.error}</div>
                  </div>
                )}

                {/* Message Actions */}
                <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center gap-2">
                    {onMessageEdit && (
                      <button
                        onClick={() =>
                          onMessageEdit(message.id, message.content)
                        }
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                        title="Edit message">
                        Edit
                      </button>
                    )}
                    {onMessageDelete && (
                      <button
                        onClick={() => onMessageDelete(message.id)}
                        className="text-xs text-muted-foreground hover:text-red-600 transition-colors"
                        title="Delete message">
                        Delete
                      </button>
                    )}
                    {message.metadata?.tokens && (
                      <span className="text-xs text-muted-foreground">
                        {message.metadata.tokens} tokens
                      </span>
                    )}
                    {message.metadata?.cost && (
                      <span className="text-xs text-muted-foreground">
                        ${message.metadata.cost.toFixed(4)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    },
    [messages.length, isLoading, onMessageEdit, onMessageDelete, rowVirtualizer]
  );

  // Memoize virtual items to prevent unnecessary re-renders
  const virtualItemsMemo = useMemo(
    () =>
      virtualItems.map((virtualItem) => {
        const message = messages[virtualItem.index];
        if (!message) return null;

        return (
          <div
            key={virtualItem.key}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}>
            {renderMessage(message, virtualItem.index)}
          </div>
        );
      }),
    [virtualItems, messages, renderMessage]
  );

  return (
    <div
      ref={parentRef}
      className={cn("relative h-full overflow-auto", className)}>
      <div
        style={{
          height: `${totalSize}px`,
          width: "100%",
          position: "relative",
        }}>
        {virtualItemsMemo}
      </div>

      {/* Loading indicator for initial load */}
      {messages.length === 0 && isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading messages...</span>
          </div>
        </div>
      )}

      {/* Empty state */}
      {messages.length === 0 && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No messages yet</p>
            <p className="text-xs mt-1">
              Start a conversation to see messages here
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
