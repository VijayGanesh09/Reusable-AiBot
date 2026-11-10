import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Message from "./Message";

const API_URL = "http://127.0.0.1:5000";

const suggestions = [
    {
        icon: "✦",
        title: "Understand a topic",
        description: "Explain something in simple words.",
        prompt: "Explain an important topic in simple words."
    },
    {
        icon: "⌕",
        title: "Explore your documents",
        description: "Find information from your knowledge base.",
        prompt: "Give me an overview of the available knowledge base."
    },
    {
        icon: "✧",
        title: "Summarize information",
        description: "Get a clear and concise summary.",
        prompt: "Give me a clear summary of the main information."
    }
];

function ChatWindow({ isReady, connectionStatus }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth"
        });
    }, [messages, loading]);

    const sendMessage = async (text = question) => {
        const userQuestion = text.trim();

        if (!userQuestion || !isReady || loading) return;

        const updatedMessages = [
            ...messages,
            {
                role: "user",
                content: userQuestion
            }
        ];

        setMessages(updatedMessages);
        setQuestion("");
        setLoading(true);

        try {
            const response = await axios.post(`${API_URL}/chat`, {
                question: userQuestion,
                history: messages
            });

            setMessages([
                ...updatedMessages,
                {
                    role: "assistant",
                    content: response.data.answer
                }
            ]);

        } catch (error) {
            setMessages([
                ...updatedMessages,
                {
                    role: "assistant",
                    content:
                        error.response?.data?.error ||
                        "Something went wrong. Please try again."
                }
            ]);

        } finally {
            setLoading(false);
            inputRef.current?.focus();
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    };

    return (
        <section className="chat-window">

            <header className="chat-header">
                <div className="chat-header-left">

                    <div className="assistant-avatar">
                        <img src="/ai-assistant.png" alt="AI Assistant" />
                    </div>

                    <div>
                        <h2>AI Assistant</h2>
                        <p>Your personal AI workspace</p>
                    </div>
                </div>

                <div className={`chat-status ${
                    isReady ? "status-ready" : "status-waiting"
                }`}>
                    <span className="status-dot"></span>
                    {connectionStatus}
                </div>
            </header>

            <section className="chat-body">

                {messages.length === 0 ? (
                    <div className="welcome-screen">

                        <div className="welcome-icon">
                            <img src="/ai-assistant.png" alt="AI Assistant" />
                        </div>

                        <p className="welcome-eyebrow">
                            YOUR AI WORKSPACE
                        </p>

                        <h1>
                            What can I help
                            <br />
                            <span>you with today?</span>
                        </h1>

                        <p className="welcome-description">
                            Ask questions, explore information, or get help
                            understanding complex topics.
                        </p>

                        {!isReady && (
                            <div className="preparing-message">
                                <span className="status-dot"></span>
                                {connectionStatus === "Offline"
                                    ? "Cannot connect to the backend. Please start your server."
                                    : "Preparing your AI assistant..."}
                            </div>
                        )}

                        <div className="suggestion-list">
                            {suggestions.map((item) => (
                                <button
                                    className="suggestion-card"
                                    key={item.title}
                                    onClick={() => {
                                        setQuestion(item.prompt);
                                        inputRef.current?.focus();
                                    }}
                                    disabled={!isReady}
                                >
                                    <div className="suggestion-icon">
                                        {item.icon}
                                    </div>

                                    <div className="suggestion-content">
                                        <h3>{item.title}</h3>
                                        <p>{item.description}</p>
                                    </div>

                                    <span className="suggestion-arrow">
                                        ↗
                                    </span>
                                </button>
                            ))}
                        </div>

                    </div>
                ) : (
                    <div className="messages-container">
                        {messages.map((message, index) => (
                            <Message
                                key={index}
                                message={message}
                            />
                        ))}
                    </div>
                )}

                {loading && (
                    <div className="thinking-indicator">

                        <div className="thinking-avatar">
                            <img src="/ai-assistant.png" alt="" />
                        </div>

                        <div className="thinking-content">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>

                        <p>Thinking...</p>
                    </div>
                )}

                <div ref={messagesEndRef} />

            </section>

            <footer className="chat-footer">

                <div className="chat-composer">
                    <input
                        ref={inputRef}
                        type="text"
                        value={question}
                        onChange={(event) => setQuestion(event.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={
                            isReady
                                ? "Message your AI assistant..."
                                : "AI assistant is preparing..."
                        }
                        disabled={!isReady || loading}
                    />

                    <button
                        className="send-button"
                        onClick={() => sendMessage()}
                        disabled={!isReady || loading || !question.trim()}
                        aria-label="Send message"
                    >
                        ↑
                    </button>
                </div>

                <p className="composer-note">
                    AI can make mistakes. Verify important information.
                </p>

            </footer>

        </section>
    );
}

export default ChatWindow;