function Message({ message }) {
    const isUser = message.role === "user";

    return (
        <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>

            {!isUser && (
                <div className="message-avatar ai-avatar">
                    <img src="/ai-assistant.png" alt="AI Assistant" />
                </div>
            )}

            <div className={`message-content ${isUser ? "user-content" : "assistant-content"}`}>

                <div className="message-sender">
                    {isUser ? "You" : "AI Assistant"}
                </div>

                <div className="message-text">
                    {message.content}
                </div>

            </div>

            {isUser && (
                <div className="message-avatar user-avatar">
                    You
                </div>
            )}

        </div>
    );
}

export default Message;