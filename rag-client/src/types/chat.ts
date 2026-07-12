// Tipos compartidos del dominio de chat. Se definen ahora para dejar
// la base lista de cara a la integración con el backend del RAG.

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}
