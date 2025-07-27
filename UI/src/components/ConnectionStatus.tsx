import { cn } from "@/lib/utils";
import { Wifi, WifiOff, Loader2 } from "lucide-react";

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface ConnectionStatusProps {
  status: ConnectionState;
  className?: string;
}

export function ConnectionStatus({ status, className }: ConnectionStatusProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'connecting':
        return {
          icon: Loader2,
          text: 'Connecting...',
          color: 'text-muted-foreground',
          bgColor: 'bg-muted',
          animate: 'animate-spin'
        };
      case 'connected':
        return {
          icon: Wifi,
          text: 'Connected',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          animate: ''
        };
      case 'disconnected':
        return {
          icon: WifiOff,
          text: 'Disconnected',
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          animate: ''
        };
      case 'error':
        return {
          icon: WifiOff,
          text: 'Connection Error',
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          animate: ''
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={cn(
      "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border",
      config.bgColor,
      config.color,
      className
    )}>
      <Icon className={cn("w-3 h-3", config.animate)} />
      <span>{config.text}</span>
    </div>
  );
}