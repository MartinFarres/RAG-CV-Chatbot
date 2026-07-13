import { useState } from "react";
import axios from "axios";
import type { ChatMessage } from "../types/chat";

const API_URL = "http://localhost:8000/chat";
const CONVERSATION_ID_KEY = "rag_conversation_id";

interface ChatResponse {
  response: string;
  conversation_id: string;
}

// Maneja el historial de mensajes de la conversación y la comunicación
// con el backend. El conversation_id se persiste en sessionStorage para
// reusarlo en los siguientes mensajes de la misma sesión. isLoading/error
// viven acá porque están atados a la request de sendMessage y los
// necesitan tanto el input (deshabilitarse) como la lista de mensajes
// (indicador de "escribiendo").
export function useConversation() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(() =>
    sessionStorage.getItem(CONVERSATION_ID_KEY)
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (message: string) => {
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setError(null);
    setIsLoading(true);

    try {
      const { data } = await axios.post<ChatResponse>(API_URL, {
        message,
        conversation_id: conversationId,
      });

      setConversationId(data.conversation_id);
      sessionStorage.setItem(CONVERSATION_ID_KEY, data.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch {
      setError("No se pudo enviar el mensaje. Intentá de nuevo.");
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, error, sendMessage };
}
