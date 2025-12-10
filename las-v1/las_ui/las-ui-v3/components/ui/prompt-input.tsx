"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  Paperclip,
  X,
  Image as ImageIcon,
  Mic,
  MicOff,
  Send,
  Square,
  Command,
} from "lucide-react";
import { useFileUpload } from "@/hooks/use-file-upload";
import { useVoiceRecording } from "@/hooks/use-voice-recording";
import { useSlashCommands } from "@/hooks/use-slash-commands";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ContentBlock } from "@/app/utils/multimodal-utils";

export interface PromptInputProps
  extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, "onSubmit"> {
  onSubmit: (value: string, files: ContentBlock[]) => void;
  isLoading?: boolean;
  onStop?: () => void;
  className?: string;
  placeholder?: string;
  showSlashCommands?: boolean;
  showVoiceRecording?: boolean;
  maxFileSize?: number;
  allowedFileTypes?: string[];
}

export function PromptInput({
  onSubmit,
  isLoading,
  onStop,
  className,
  placeholder = "Send a message...",
  showSlashCommands = true,
  showVoiceRecording = true,
  maxFileSize = 10 * 1024 * 1024, // 10MB default
  allowedFileTypes = [
    ".txt",
    ".pdf",
    ".doc",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
  ],
  ...props
}: PromptInputProps) {
  const [input, setInput] = React.useState("");
  const [showCommands, setShowCommands] = React.useState(false);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const {
    contentBlocks,
    handleFileUpload,
    removeBlock,
    handlePaste,
    dropRef,
    dragOver,
  } = useFileUpload({ maxFileSize, allowedFileTypes });

  const {
    isRecording,
    isSupported: voiceSupported,
    startRecording,
    stopRecording,
    recordingTime,
    audioBlob,
    clearRecording,
  } = useVoiceRecording();

  const [isHydrated, setIsHydrated] = React.useState(false);
  React.useEffect(() => {
    setIsHydrated(true);
  }, []);

  const {
    commands,
    filteredCommands,
    selectedIndex,
    handleSlashInput,
    insertCommand,
    closeCommands,
  } = useSlashCommands();

  // Auto-resize textarea
  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "inherit";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  // Handle voice recording completion
  React.useEffect(() => {
    if (audioBlob && !isRecording) {
      // Convert audio blob to file and add as attachment
      const audioFile = new File(
        [audioBlob],
        `voice-recording-${Date.now()}.webm`,
        {
          type: "audio/webm",
        }
      );
      const dt = new DataTransfer();
      dt.items.add(audioFile);
      const event = {
        target: { files: dt.files },
      } as React.ChangeEvent<HTMLInputElement>;
      handleFileUpload(event);
      clearRecording();
    }
  }, [audioBlob, isRecording, clearRecording, handleFileUpload]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle slash commands navigation
    if (showCommands) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        handleSlashInput("ArrowDown");
        return;
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        handleSlashInput("ArrowUp");
        return;
      } else if (e.key === "Enter") {
        e.preventDefault();
        const command = filteredCommands[selectedIndex];
        if (command) {
          insertCommand(command);
          setShowCommands(false);
        }
        return;
      } else if (e.key === "Escape") {
        closeCommands();
        setShowCommands(false);
        return;
      }
    }

    // Handle normal submit
    if (e.key === "Enter" && !e.shiftKey && !showCommands) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInput(value);

    // Check for slash commands
    if (showSlashCommands) {
      const lastChar = value[value.length - 1];
      if (lastChar === "/") {
        setShowCommands(true);
        handleSlashInput("/");
      } else if (showCommands) {
        const lastSlashIndex = value.lastIndexOf("/");
        if (lastSlashIndex !== -1) {
          const query = value.slice(lastSlashIndex + 1);
          if (query.includes(" ")) {
            setShowCommands(false);
          } else {
            handleSlashInput(query);
          }
        } else {
          setShowCommands(false);
        }
      }
    }
  };

  const handleSubmit = () => {
    if (
      (!input.trim() && contentBlocks.length === 0) ||
      isLoading ||
      isRecording
    )
      return;

    // Process slash commands in input
    let processedInput = input;
    if (showSlashCommands) {
      const commandMatch = input.match(/^\/(\w+)(?:\s+(.*))?$/);
      if (commandMatch) {
        const [, command, args] = commandMatch;
        const commandConfig = commands.find((cmd) => cmd.command === command);
        if (commandConfig) {
          processedInput = commandConfig.handler(args || "");
        }
      }
    }

    onSubmit(processedInput, contentBlocks);
    setInput("");
    setShowCommands(false);
  };

  const handleVoiceToggle = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording();
    }
  };

  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="relative">
      {/* Slash Commands Dropdown */}
      {showCommands && filteredCommands.length > 0 && (
        <div className="absolute bottom-full left-0 mb-2 w-80 z-50">
          <div className="bg-popover border rounded-lg shadow-lg">
            <div className="p-2 border-b">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Command className="w-4 h-4" />
                <span>Slash Commands</span>
              </div>
            </div>
            <ScrollArea className="max-h-64">
              {filteredCommands.map((command, index) => (
                <button
                  key={command.command}
                  className={cn(
                    "w-full text-left px-3 py-2 text-sm hover:bg-accent transition-colors",
                    index === selectedIndex && "bg-accent"
                  )}
                  onClick={() => {
                    insertCommand(command);
                    setShowCommands(false);
                  }}>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                      /{command.command}
                    </span>
                    <span className="text-muted-foreground">
                      {command.description}
                    </span>
                  </div>
                </button>
              ))}
            </ScrollArea>
          </div>
        </div>
      )}

      <div
        ref={dropRef}
        className={cn(
          "relative flex flex-col w-full bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden transition-colors",
          dragOver && "border-primary bg-primary/5",
          className
        )}>
        {/* File Attachments */}
        {contentBlocks.length > 0 && (
          <div className="flex flex-wrap gap-2 p-3 border-b border-zinc-800/50">
            {contentBlocks.map((block, index) => (
              <div
                key={
                  block.metadata?.name
                    ? `${(block.metadata as any).name}-${block.mimeType}-${
                        (block.metadata as any).size ?? ""
                      }`
                    : `${block.mimeType}-${index}`
                }
                className="relative group flex items-center gap-2 bg-zinc-800 rounded-md px-2 py-1 text-xs">
                {block.type === "image" ? (
                  <ImageIcon className="w-3 h-3 text-blue-400" />
                ) : (
                  <Paperclip className="w-3 h-3 text-zinc-400" />
                )}
                <span className="max-w-[100px] truncate">
                  {block.metadata?.name || "File"}
                </span>
                <button
                  onClick={() => removeBlock(index)}
                  className="ml-1 p-0.5 hover:bg-zinc-700 rounded-full">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Voice Recording Indicator */}
        {isRecording && (
          <div className="flex items-center gap-2 p-3 border-b border-red-500/50 bg-red-500/10">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm text-red-500">
              Recording {formatRecordingTime(recordingTime)}
            </span>
            <button
              onClick={handleVoiceToggle}
              className="ml-auto p-1 hover:bg-red-500/20 rounded">
              <Square className="w-4 h-4 text-red-500" />
            </button>
          </div>
        )}

        {/* Text Input */}
        <Textarea
          ref={textareaRef}
          placeholder={placeholder}
          className="min-h-[60px] max-h-[200px] w-full resize-none bg-transparent border-0 focus-visible:ring-0 px-4 py-3 text-sm"
          rows={1}
          disabled={isLoading}
          {...props}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between p-2 pl-3">
          <div className="flex items-center gap-1">
            <input
              type="file"
              multiple
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept={allowedFileTypes.join(",")}
            />
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-400 hover:text-zinc-100"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || isRecording}
              aria-label="Attach file">
              <Paperclip className="w-4 h-4" />
            </Button>

            {showVoiceRecording && isHydrated && voiceSupported && (
              <Button
                variant="ghost"
                size="icon"
                className={cn(
                  "h-8 w-8 transition-colors",
                  isRecording
                    ? "text-red-500 hover:text-red-400"
                    : "text-zinc-400 hover:text-zinc-100"
                )}
                onClick={handleVoiceToggle}
                disabled={isLoading}
                aria-label={isRecording ? "Stop recording" : "Start recording"}>
                {isRecording ? (
                  <MicOff className="w-4 h-4" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </Button>
            )}

            {showSlashCommands && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-zinc-400 hover:text-zinc-100"
                    disabled={isLoading || isRecording}>
                    <Command className="w-4 h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-80">
                  <div className="p-2 border-b">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Command className="w-4 h-4" />
                      <span>Slash Commands</span>
                    </div>
                  </div>
                  <ScrollArea className="max-h-64">
                    {commands.map((command) => (
                      <DropdownMenuItem
                        key={command.command}
                        onClick={() => {
                          insertCommand(command);
                          setInput(input + `/${command.command} `);
                        }}>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                            /{command.command}
                          </span>
                          <span className="text-muted-foreground">
                            {command.description}
                          </span>
                        </div>
                      </DropdownMenuItem>
                    ))}
                  </ScrollArea>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>

          <div className="flex items-center gap-2">
            {isLoading ? (
              <Button
                onClick={onStop}
                variant="secondary"
                size="sm"
                className="h-8 px-3 text-xs">
                <Square className="w-3 h-3 mr-1" />
                Stop
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={
                  (!input.trim() && contentBlocks.length === 0) || isRecording
                }
                size="sm"
                className="h-8 px-3 text-xs bg-primary hover:bg-primary/90 text-primary-foreground">
                <Send className="w-3 h-3 mr-1" />
                Send
              </Button>
            )}
          </div>
        </div>

        {dragOver && (
          <div className="absolute inset-0 flex items-center justify-center bg-primary/10 backdrop-blur-sm z-10">
            <div className="bg-background/80 px-4 py-2 rounded-lg border border-primary text-primary font-medium text-sm">
              Drop files to attach
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
