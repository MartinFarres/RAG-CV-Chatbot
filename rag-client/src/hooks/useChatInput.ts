import { useState } from "react";

// Encapsula el estado del input de chat: valor actual, setter,
// submit (placeholder hasta conectar el backend del RAG) y flag de vacío.
export function useChatInput() {
  const [value, setValue] = useState("");

  const isEmpty = value.trim().length === 0;

  const handleSubmit = () => {
    if (isEmpty) return;
    console.log("Mensaje enviado:", value);
    setValue("");
  };

  return { value, setValue, handleSubmit, isEmpty };
}
