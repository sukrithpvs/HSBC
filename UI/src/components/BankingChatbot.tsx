import { useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChatMessage, type Message } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { ConnectionStatus, type ConnectionState } from '@/components/ConnectionStatus';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Building2, RotateCcw, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BankingChatbotProps {
  className?: string;
  websocketUrl?: string;
  userId?: string;
}

export function BankingChatbot({ 
  className, 
  websocketUrl = 'ws://localhost:8000/ws',
  userId = 'user_demo1'
}: BankingChatbotProps) {
  const { messages, connectionStatus, sendMessage, clearMessages, reconnect } = useWebSocket(websocketUrl, userId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickActions = [
    "What's my account balance?",
    "Block my debit card", 
    "Apply for a $15,000 loan for home improvement",
    "Show my recent transactions",
    "Unblock my card",
    "Transfer $500 to savings"
  ];

  return (
    <div className={cn("flex flex-col h-full max-h-screen bg-gradient-subtle", className)}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-border bg-card shadow-sm">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center shadow-glow">
              <Building2 className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">AI Banking Assistant</h1>
              <p className="text-sm text-muted-foreground">John Smith • Demo Account</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ConnectionStatus status={connectionStatus} />
            <Button
              variant="outline"
              size="sm"
              onClick={reconnect}
              disabled={connectionStatus === 'connecting'}
              className="hidden sm:flex"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reconnect
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearMessages}
              className="hidden sm:flex"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && connectionStatus === 'connected' && (
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-primary mx-auto mb-4 flex items-center justify-center shadow-glow">
                  <Building2 className="w-8 h-8 text-primary-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2 text-foreground">Ready to help!</h3>
                <p className="text-muted-foreground">How can I assist you with your banking needs today?</p>
              </div>
            )}

            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {connectionStatus === 'connecting' && messages.length === 0 && (
              <div className="p-8 text-center">
                <div className="animate-pulse">
                  <div className="w-12 h-12 rounded-full bg-muted mx-auto mb-4"></div>
                  <p className="text-muted-foreground">Connecting to banking services...</p>
                </div>
              </div>
            )}

            {connectionStatus === 'error' && (
              <div className="p-8 text-center">
                <div className="w-12 h-12 rounded-full bg-destructive/10 mx-auto mb-4 flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-destructive" />
                </div>
                <h3 className="text-lg font-semibold mb-2 text-destructive">Connection Error</h3>
                <p className="text-muted-foreground mb-4">
                  Unable to connect to banking services. Please check if the backend is running.
                </p>
                <Button onClick={reconnect} variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0">
          <ChatInput
            onSendMessage={sendMessage}
            disabled={connectionStatus !== 'connected'}
            placeholder={
              connectionStatus === 'connected' 
                ? "Ask about your account, loans, cards, or transactions..."
                : connectionStatus === 'connecting'
                ? "Connecting..."
                : "Disconnected - please reconnect"
            }
          />
        </div>
      </div>
    </div>
  );
}