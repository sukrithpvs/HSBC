import { useState, useEffect, useCallback, useRef } from 'react';
import type { Message } from '@/components/ChatMessage';
import type { ConnectionState } from '@/components/ConnectionStatus';

interface UseWebSocketReturn {
  messages: Message[];
  connectionStatus: ConnectionState;
  sendMessage: (message: string) => void;
  clearMessages: () => void;
  reconnect: () => void;
}

export function useWebSocket(url: string, userId: string = 'user_demo1'): UseWebSocketReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionState>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      setConnectionStatus('connecting');
      const wsUrl = `${url}?user_id=${userId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const newMessage: Message = {
            id: `${Date.now()}-${Math.random()}`,
            type: data.type || 'assistant',
            message: data.message || '',
            timestamp: data.timestamp || new Date().toISOString(),
            intent: data.intent,
            workflow_active: data.workflow_active,
            completed: data.completed,
            context_switched: data.context_switched
          };
          setMessages(prev => [...prev, newMessage]);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        
        // Auto-reconnect logic
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [url, userId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Add user message to local state immediately
      const userMessage: Message = {
        id: `${Date.now()}-user`,
        type: 'user',
        message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);

      // Send to server
      wsRef.current.send(JSON.stringify({ message }));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(connect, 1000);
  }, [connect, disconnect]);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return {
    messages,
    connectionStatus,
    sendMessage,
    clearMessages,
    reconnect
  };
}