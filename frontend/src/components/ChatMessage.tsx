import { Message } from '@/types/api';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatContent = (content: string) => {
    // Handle newlines and preserve formatting
    return content.split('\n').map((line, index, array) => (
      <span key={index}>
        {line}
        {index < array.length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div className={cn(
      "mb-4",
      message.isUser ? "text-right" : "text-left"
    )}>
      <div className={cn(
        "inline-block max-w-[80%] p-4 rounded-lg",
        message.isUser 
          ? "bg-blue-600 text-white" 
          : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
      )}>
        <div className="whitespace-pre-wrap break-words">
          {formatContent(message.content)}
        </div>
        <div className={cn(
          "text-xs mt-2 opacity-75",
          message.isUser 
            ? "text-blue-100" 
            : "text-gray-500 dark:text-gray-400"
        )}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}