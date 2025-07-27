import { cn } from "@/lib/utils";
import { Bot, User, AlertCircle } from "lucide-react";
import ReactMarkdown from 'react-markdown';

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  message: string;
  timestamp: string;
  intent?: string;
  workflow_active?: boolean;
  completed?: boolean;
  context_switched?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const isAssistant = message.type === 'assistant';

  return (
    <div className={cn(
      "flex gap-3 p-4 animate-in slide-in-from-bottom-2 duration-300",
      isUser && "flex-row-reverse"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser && "bg-chat-user-bubble",
        isAssistant && "bg-chat-assistant-bubble border border-border",
        isSystem && "bg-chat-system-bubble border border-border"
      )}>
        {isUser && <User className="w-4 h-4 text-chat-user-text" />}
        {isAssistant && <Bot className="w-4 h-4 text-chat-assistant-text" />}
        {isSystem && <AlertCircle className="w-4 h-4 text-chat-system-text" />}
      </div>

      {/* Message bubble */}
      <div className={cn(
        "max-w-[80%] rounded-2xl px-4 py-3 shadow-sm",
        isUser && "bg-chat-user-bubble text-chat-user-text rounded-br-md",
        isAssistant && "bg-chat-assistant-bubble text-chat-assistant-text rounded-bl-md border border-border",
        isSystem && "bg-chat-system-bubble text-chat-system-text border border-border rounded-md"
      )}>
        {/* Message content */}
        <div className="text-sm leading-relaxed max-w-none">
          {isUser ? (
            <div className="whitespace-pre-wrap">{message.message}</div>
          ) : (
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="text-lg font-bold mb-3 text-foreground">{children}</h1>,
                h2: ({ children }) => <h2 className="text-base font-bold mb-3 text-foreground">{children}</h2>,
                h3: ({ children }) => <h3 className="text-sm font-bold mb-2 text-foreground">{children}</h3>,
                h4: ({ children }) => <h4 className="text-sm font-semibold mb-2 text-foreground">{children}</h4>,
                p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                ul: ({ children }) => <ul className="list-disc list-outside ml-4 mb-3 space-y-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-outside ml-4 mb-3 space-y-2">{children}</ol>,
                li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                em: ({ children }) => <em className="italic">{children}</em>,
                code: ({ children }) => <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
                br: () => <br className="mb-2" />,
              }}
            >
              {message.message
                .replace(/Number:\s*(\d+)/g, '\n\n**$1.**')
                .replace(/(Card Number|Card Type|Status|Account Number|Credit Limit|Block Reason):/g, '\n- **$1:**')
                .replace(/\n\n\n/g, '\n\n')
                .trim()}
            </ReactMarkdown>
          )}
        </div>

        {/* Banking metadata */}
        {isAssistant && (message.intent || message.workflow_active || message.context_switched) && (
          <div className="mt-3 pt-2 border-t border-border/50">
            <div className="flex flex-wrap gap-2 text-xs">
              {message.intent && (
                <span className="px-2 py-1 bg-accent rounded-full text-accent-foreground">
                  Intent: {message.intent}
                </span>
              )}
              {message.workflow_active && (
                <span className="px-2 py-1 bg-primary/10 rounded-full text-primary">
                  Workflow Active
                </span>
              )}
              {message.context_switched && (
                <span className="px-2 py-1 bg-secondary rounded-full text-secondary-foreground">
                  Context Switched
                </span>
              )}
              {message.completed && (
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full">
                  Completed
                </span>
              )}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div className="mt-2 text-xs opacity-60">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}