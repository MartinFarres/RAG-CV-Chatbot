import { TypewriterHeading } from "./components/TypewriterHeading";
import { ChatInput } from "./components/ChatInput";
import { MessageList } from "./components/MessageList";
import { Footer } from "./components/Footer";
import { useConversation } from "./hooks/useConversation";

// Layout raíz de la landing: heading centrado, input de chat y footer.
// Una vez que arranca la conversación, el heading se reemplaza por la
// lista de mensajes.
function App() {
  const { messages, isLoading, error, sendMessage } = useConversation();
  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex flex-1 flex-col overflow-hidden">
        {hasMessages ? (
          <MessageList messages={messages} isLoading={isLoading} />
        ) : (
          <div className="flex flex-1 items-center justify-center">
            <TypewriterHeading />
          </div>
        )}
      </main>
      <div className="pb-6">
        <ChatInput onSend={sendMessage} isLoading={isLoading} error={error} />
      </div>
      <Footer />
    </div>
  );
}

export default App;
