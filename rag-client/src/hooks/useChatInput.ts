import { useState } from "react";

// Encapsula sólo el estado del input de chat: valor actual, setter y
// submit. El envío real, el historial, el loading y el error viven en
// useConversation; `disabled` llega desde ahí para bloquear el submit
// mientras hay una request en curso.
export function useChatInput(
  onSend: (message: string) => void,
  disabled: boolean
) {
  const [value, setValue] = useState("");

  const isEmpty = value.trim().length === 0;

  const handleSubmit = () => {
    if (isEmpty || disabled) return;

    const message = value.trim();
    setValue("");
    onSend(message);
  };

  return { value, setValue, handleSubmit, isEmpty };
}
