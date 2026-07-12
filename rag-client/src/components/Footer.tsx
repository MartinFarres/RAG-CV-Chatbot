import { Github, Linkedin, Mail, MessageCircle } from "lucide-react";
import {
  GITHUB_URL,
  LINKEDIN_URL,
  EMAIL_ADDRESS,
  WHATSAPP_URL,
} from "../constants/links";

// Pie de página con links sociales/contacto y aviso de copyright.
export function Footer() {
  return (
    <footer className="w-full py-6 px-4">
      <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6">
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="GitHub"
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Github size={22} />
        </a>
        <a
          href={LINKEDIN_URL}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="LinkedIn"
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Linkedin size={22} />
        </a>
        <a
          href={`mailto:${EMAIL_ADDRESS}`}
          aria-label="Email"
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Mail size={22} />
        </a>
        <a
          href={WHATSAPP_URL}
          target="_blank"
          rel="noopener noreferrer"
          aria-label="WhatsApp"
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <MessageCircle size={22} />
        </a>
      </div>
      <p className="mt-4 text-center text-xs sm:text-sm text-gray-500">
        © 2026 Martín Farrés. Todos los derechos reservados.
      </p>
    </footer>
  );
}
