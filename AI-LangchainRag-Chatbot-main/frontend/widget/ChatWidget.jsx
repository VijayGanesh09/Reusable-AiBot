
import React, { useState } from "react";
import "./ChatWidget.css";

export default function ChatWidget({ apiUrl }) {
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const currentQuestion = question.trim();

    if (!currentQuestion || loading) return;

    const userMessage = {
      role: "user",
      content: currentQuestion
    };

    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: currentQuestion,
          history: messages
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Unable to get response");
      }

      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: data.answer
        }
      ]);
    } catch (error) {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: `Error: ${error.message}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {isOpen && (
        <div className="rag-chat-window">
          <div className="rag-chat-header">
            AI Assistant
          </div>

          <div className="rag-chat-messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`rag-message ${
                  message.role === "user"
                    ? "rag-user-message"
                    : "rag-assistant-message"
                }`}
              >
                {message.content}
              </div>
            ))}

            {loading && (
              <p className="rag-thinking">Thinking...</p>
            )}
          </div>

          <div className="rag-chat-input-area">
            <input
              className="rag-chat-input"
              value={question}
              placeholder="Ask a question..."
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") sendMessage();
              }}
            />

            <button
              className="rag-send-button"
              onClick={sendMessage}
              disabled={loading}
            >
              Send
            </button>
          </div>
        </div>
      )}

      <button
        className="rag-chat-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? "×" : "💬"}
      </button>
    </>
  );
}
