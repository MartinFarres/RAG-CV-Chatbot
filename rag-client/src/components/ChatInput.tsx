import { ArrowRight } from "lucide-react";
import { useChatInput } from "../hooks/useChatInput";

// Input de chat con botón circular embebido. La lógica de estado y
// envío vive en useChatInput; este componente sólo renderiza la UI.
export function ChatInput() {
  const { value, setValue, handleSubmit, isEmpty } = useChatInput();

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div className="flex items-center gap-2 rounded-full border border-gray-300 bg-white px-4 py-2 shadow-sm focus-within:ring-2 focus-within:ring-gray-400">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribí tu mensaje..."
          className="flex-1 min-w-0 bg-transparent outline-none text-sm sm:text-base"
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={isEmpty}
          aria-label="Enviar mensaje"
          className="flex-shrink-0 flex items-center justify-center w-9 h-9 rounded-full bg-gray-900 text-white disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}
