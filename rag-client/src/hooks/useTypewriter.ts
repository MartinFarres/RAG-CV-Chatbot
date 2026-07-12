import { useEffect, useState } from "react";

// Revela un string progresivamente, caracter por caracter, simulando
// una máquina de escribir. Devuelve el texto parcial y si ya terminó.
export function useTypewriter(text: string, speedMs = 50) {
  // Si "text" cambia, se resetea el progreso durante el render
  // (patrón recomendado por React en vez de hacerlo en un efecto).
  const [trackedText, setTrackedText] = useState(text);
  const [displayedText, setDisplayedText] = useState("");

  if (text !== trackedText) {
    setTrackedText(text);
    setDisplayedText("");
  }

  useEffect(() => {
    const intervalId = setInterval(() => {
      setDisplayedText((prev) => {
        if (prev.length >= text.length) {
          clearInterval(intervalId);
          return prev;
        }
        return text.slice(0, prev.length + 1);
      });
    }, speedMs);

    return () => clearInterval(intervalId);
  }, [text, speedMs]);

  return { displayedText, isDone: displayedText.length === text.length };
}
