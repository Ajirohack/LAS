'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface StreamMessage {
    type: 'token' | 'tool' | 'complete' | 'error' | 'thought';
    data: unknown;
}

interface UseStreamOptions {
    url?: string;
    autoConnect?: boolean;
    maxRetries?: number;
    mode?: 'sse' | 'websocket';
}

/**
 * Unified streaming hook supporting both SSE (Server-Sent Events) and WebSocket.
 * 
 * SSE mode: Connects to the backend's EventSource endpoint (recommended)
 * WebSocket mode: Connects to a WebSocket endpoint
 * 
 * By default, uses SSE which is more compatible with the LAS backend.
 */
export function useStream(options: UseStreamOptions = {}) {
    const {
        url = '/api/v1/stream/stream', // SSE endpoint
        autoConnect = false, // Don't auto-connect by default - connect on message send
        maxRetries = 3,
        mode = 'sse', // Default to SSE
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [messages, setMessages] = useState<StreamMessage[]>([]);
    const [currentToken, setCurrentToken] = useState('');
    const [connectionError, setConnectionError] = useState<string | null>(null);

    const eventSourceRef = useRef<EventSource | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // ========== SSE (Server-Sent Events) Implementation ==========

    const connectSSE = useCallback(() => {
        if (eventSourceRef.current) {
            return;
        }

        try {
            const eventSource = new EventSource(url);

            eventSource.onopen = () => {
                console.log('✓ SSE connected to LAS backend');
                setIsConnected(true);
                setConnectionError(null);
                retryCountRef.current = 0;
            };

            eventSource.onmessage = (event) => {
                try {
                    const message: StreamMessage = JSON.parse(event.data);
                    setMessages((prev) => [...prev, message]);

                    if (message.type === 'token') {
                        setCurrentToken((prev) => prev + message.data);
                    } else if (message.type === 'complete') {
                        setCurrentToken('');
                        setIsStreaming(false);
                    } else if (message.type === 'error') {
                        setConnectionError(String(message.data));
                        setIsStreaming(false);
                    }
                } catch (error) {
                    console.error('Failed to parse SSE message:', error);
                }
            };

            eventSource.onerror = () => {
                setIsConnected(false);
                eventSourceRef.current = null;

                if (autoConnect && retryCountRef.current < maxRetries) {
                    const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
                    retryCountRef.current++;
                    console.log(`Retrying SSE connection in ${delay}ms... (Attempt ${retryCountRef.current}/${maxRetries})`);

                    retryTimeoutRef.current = setTimeout(() => {
                        connectSSE();
                    }, delay);
                } else if (retryCountRef.current >= maxRetries) {
                    setConnectionError('Backend connection unavailable. Please start the LAS backend server.');
                }
            };

            eventSourceRef.current = eventSource;
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown SSE connection error';
            setConnectionError(errorMsg);
            console.error('Failed to create SSE connection:', errorMsg);
        }
    }, [url, autoConnect, maxRetries]);

    const disconnectSSE = useCallback(() => {
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current);
            retryTimeoutRef.current = null;
        }

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setIsConnected(false);
    }, []);

    // ========== WebSocket Implementation (Legacy) ==========

    const connectWS = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const wsUrl = url.startsWith('ws') ? url : `ws://localhost:8080/ws/stream`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('✓ WebSocket connected to LAS backend');
                setIsConnected(true);
                setConnectionError(null);
                retryCountRef.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const message: StreamMessage = JSON.parse(event.data);
                    setMessages((prev) => [...prev, message]);

                    if (message.type === 'token') {
                        setCurrentToken((prev) => prev + message.data);
                    } else if (message.type === 'complete') {
                        setCurrentToken('');
                        setIsStreaming(false);
                    }
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            ws.onerror = () => {
                const errorMsg = `Unable to connect to LAS backend at ${wsUrl}`;
                setConnectionError(errorMsg);
                console.warn('⚠ WebSocket connection failed - Is the backend running?');
            };

            ws.onclose = (event) => {
                setIsConnected(false);
                wsRef.current = null;

                if (!event.wasClean && autoConnect && retryCountRef.current < maxRetries) {
                    const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
                    retryCountRef.current++;
                    retryTimeoutRef.current = setTimeout(() => {
                        connectWS();
                    }, delay);
                }
            };

            wsRef.current = ws;
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown connection error';
            setConnectionError(errorMsg);
        }
    }, [url, autoConnect, maxRetries]);

    const disconnectWS = useCallback(() => {
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current);
            retryTimeoutRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    // ========== Unified API ==========

    const connect = useCallback(() => {
        if (mode === 'sse') {
            connectSSE();
        } else {
            connectWS();
        }
    }, [mode, connectSSE, connectWS]);

    const disconnect = useCallback(() => {
        if (mode === 'sse') {
            disconnectSSE();
        } else {
            disconnectWS();
        }

        // Cancel any pending fetch requests
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
    }, [mode, disconnectSSE, disconnectWS]);

    /**
     * Send a message and stream the response.
     * Uses fetch with streaming for SSE mode, or WebSocket for WS mode.
     */
    const sendMessage = useCallback(async (
        message: string | Record<string, unknown>,
        streamUrl?: string
    ) => {
        // For SSE mode, use fetch with streaming
        if (mode === 'sse') {
            return sendMessageSSE(message, streamUrl);
        }

        // For WebSocket mode, send through socket
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            const payload = typeof message === 'string'
                ? { type: 'query', content: message }
                : message;
            wsRef.current.send(JSON.stringify(payload));
        } else {
            console.error('WebSocket is not connected');
        }
    }, [mode]);

    /**
     * Send a message using fetch() with SSE streaming response.
     * This is the recommended approach for chat completions.
     */
    const sendMessageSSE = useCallback(async (
        message: string | Record<string, unknown>,
        customUrl?: string
    ) => {
        setIsStreaming(true);
        setCurrentToken('');
        setConnectionError(null);

        // Create abort controller for this request
        abortControllerRef.current = new AbortController();

        try {
            const requestUrl = customUrl || '/api/v1/litellm/chat/completions';

            // Build request body
            const body = typeof message === 'string'
                ? {
                    messages: [{ role: 'user', content: message }],
                    stream: true,
                }
                : { ...message, stream: true };

            const response = await fetch(requestUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify(body),
                signal: abortControllerRef.current.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) {
                throw new Error('No response body reader available');
            }

            const decoder = new TextDecoder();
            let buffer = '';

            setIsConnected(true);

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    break;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);

                        if (data === '[DONE]') {
                            setMessages((prev) => [...prev, { type: 'complete', data: null }]);
                            setIsStreaming(false);
                            continue;
                        }

                        try {
                            const parsed = JSON.parse(data);

                            // Handle different SSE message formats
                            if (parsed.type === 'token') {
                                setCurrentToken((prev) => prev + parsed.content);
                                setMessages((prev) => [...prev, { type: 'token', data: parsed.content }]);
                            } else if (parsed.type === 'tool_call') {
                                setMessages((prev) => [...prev, { type: 'tool', data: parsed.tool_calls }]);
                            } else if (parsed.type === 'complete') {
                                setMessages((prev) => [...prev, { type: 'complete', data: null }]);
                                setIsStreaming(false);
                            } else if (parsed.type === 'error') {
                                setConnectionError(parsed.error || 'Unknown error');
                                setMessages((prev) => [...prev, { type: 'error', data: parsed.error }]);
                                setIsStreaming(false);
                            } else if (parsed.choices?.[0]?.delta?.content) {
                                // OpenAI-style streaming response
                                const content = parsed.choices[0].delta.content;
                                setCurrentToken((prev) => prev + content);
                                setMessages((prev) => [...prev, { type: 'token', data: content }]);
                            }
                        } catch {
                            // Not JSON, might be raw text
                            if (data.trim()) {
                                setCurrentToken((prev) => prev + data);
                                setMessages((prev) => [...prev, { type: 'token', data }]);
                            }
                        }
                    }
                }
            }

            setIsStreaming(false);
        } catch (error) {
            if (error instanceof Error && error.name === 'AbortError') {
                console.log('Stream request was aborted');
            } else {
                const errorMsg = error instanceof Error ? error.message : 'Stream error';
                setConnectionError(errorMsg);
                console.error('Stream error:', errorMsg);
            }
            setIsStreaming(false);
        } finally {
            abortControllerRef.current = null;
        }
    }, []);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setCurrentToken('');
    }, []);

    const cancelStream = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
        setIsStreaming(false);
    }, []);

    // Auto-connect on mount if enabled
    useEffect(() => {
        if (autoConnect) {
            queueMicrotask(() => {
                connect();
            });
        }

        return () => {
            disconnect();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [autoConnect]);

    return {
        // Connection state
        isConnected,
        isStreaming,
        connectionError,

        // Message state
        messages,
        currentToken,

        // Actions
        connect,
        disconnect,
        sendMessage,
        sendMessageSSE,
        clearMessages,
        cancelStream,
    };
}

export default useStream;
