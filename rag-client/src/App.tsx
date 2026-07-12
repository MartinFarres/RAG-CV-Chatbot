import { TypewriterHeading } from "./components/TypewriterHeading";
import { ChatInput } from "./components/ChatInput";
import { Footer } from "./components/Footer";

// Layout raíz de la landing: heading centrado, input de chat y footer.
function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex flex-1 items-center justify-center">
        <TypewriterHeading />
      </main>
      <div className="pb-6">
        <ChatInput />
      </div>
      <Footer />
    </div>
  );
}

export default App;
