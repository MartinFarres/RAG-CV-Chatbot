import { useTypewriter } from "../hooks/useTypewriter";

const HEADING_TEXT = "Hola, soy el chatbot de Martín Farrés. ¿En qué puedo ayudarte?";

// Encabezado principal de la landing: escribe el saludo caracter por
// caracter y deja un cursor parpadeando mientras escribe y al terminar.
export function TypewriterHeading() {
  const { displayedText } = useTypewriter(HEADING_TEXT);

  return (
    <h1 className="font-mono text-center text-2xl sm:text-3xl md:text-4xl px-4 leading-relaxed">
      {displayedText}
      <span aria-hidden="true" className="inline-block ml-1 animate-blink">
        |
      </span>
    </h1>
  );
}
