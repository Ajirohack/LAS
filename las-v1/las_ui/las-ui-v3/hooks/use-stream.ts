'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface StreamMessage {
    type: 'token' | 'tool' | 'complete' | 'error';
    data: unknown;
}

interface UseStreamOptions {
    url?: string;
    autoConnect?: boolean;
    maxRetries?: number;
}

export function useStream(options: UseStreamOptions = {}) {
    const {
        url = 'ws://localhost:8080/ws/stream',
        autoConnect = true,
        maxRetries = 3,
    } = options;

    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState<StreamMessage[]>([]);
    const [currentToken, setCurrentToken] = useState('');
    const [connectionError, setConnectionError] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const connectFnRef = useRef<(() => void) | null>(null);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        try {
            const ws = new WebSocket(url);

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
                    }
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            ws.onerror = (_event) => {
                // WebSocket error events don't contain useful error information
                // The actual error details will be in the onclose event
                const errorMsg = `Unable to connect to LAS backend at ${url}`;
                setConnectionError(errorMsg);
                console.warn('⚠ WebSocket connection failed - Is the backend running?');
            };

            ws.onclose = (event) => {
                setIsConnected(false);
                wsRef.current = null;

                if (!event.wasClean) {
                    const reason = event.reason || 'Connection closed unexpectedly';
                    console.log(`WebSocket disconnected: ${reason} (Code: ${event.code})`);

                    // Retry with exponential backoff if within retry limit
                    if (autoConnect && retryCountRef.current < maxRetries) {
                        const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
                        retryCountRef.current++;
                        console.log(`Retrying connection in ${delay}ms... (Attempt ${retryCountRef.current}/${maxRetries})`);

                        retryTimeoutRef.current = setTimeout(() => {
                            connectFnRef.current?.();
                        }, delay);
                    } else if (retryCountRef.current >= maxRetries) {
                        console.log('Max retry attempts reached. WebSocket will remain disconnected.');
                        setConnectionError('Backend connection unavailable. Please start the LAS backend server.');
                    }
                } else {
                    console.log('WebSocket disconnected cleanly');
                }
            };

            wsRef.current = ws;
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown connection error';
            setConnectionError(errorMsg);
            console.error('Failed to create WebSocket connection:', errorMsg);
        }
    }, [url, autoConnect, maxRetries]);

    // Keep a ref to the connect function for retry logic
    connectFnRef.current = connect;

    const disconnect = useCallback(() => {
        // Clear any pending retry attempts
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

    const sendMessage = useCallback((message: Record<string, unknown>) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not connected');
        }
    }, []);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setCurrentToken('');
    }, []);

    useEffect(() => {
        if (autoConnect) {
            // Use queueMicrotask to avoid "cascading renders" warning
            // This allows the effect to complete before setState is called
            queueMicrotask(() => {
                connect();
            });
        }

        return () => {
            disconnect();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [autoConnect]); // Only depend on autoConnect, not connect/disconnect to avoid re-running

    return {
        isConnected,
        connectionError,
        messages,
        currentToken,
        connect,
        disconnect,
        sendMessage,
        clearMessages,
    };
}
