import { useEffect, useRef } from "react";
import type { ChatMessage } from "../types/chat";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

// Lista de mensajes de la conversación con bubbles estilo chat y un
// indicador de "escribiendo" (tres puntos animados) mientras se espera
// la respuesta del backend.
export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="w-full max-w-2xl mx-auto flex-1 overflow-y-auto px-4 py-6 space-y-3">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm sm:text-base whitespace-pre-wrap ${
              message.role === "user"
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-900"
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="flex items-center gap-1 rounded-2xl bg-gray-100 px-4 py-3">
            <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
            <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
            <span className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
