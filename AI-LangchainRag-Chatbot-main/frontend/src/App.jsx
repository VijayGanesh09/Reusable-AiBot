
import { useState, useEffect } from "react";
import axios from "axios";
import ChatWindow from "./components/ChatWindow";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
    const [isReady, setIsReady] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState("Connecting");

    useEffect(() => {
        let isMounted = true;

        const checkBackendStatus = async () => {
            try {
                const response = await axios.get(`${API_URL}/`);

                if (!isMounted) return;

                if (response.data.ready) {
                    setIsReady(true);
                    setConnectionStatus("Online");
                } else {
                    setIsReady(false);
                    setConnectionStatus("Preparing");
                }

            } catch {
                if (!isMounted) return;

                setIsReady(false);
                setConnectionStatus("Offline");
            }
        };

        checkBackendStatus();

        const interval = setInterval(checkBackendStatus, 3000);

        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, []);

    return (
        <div className="app">

            <header className="app-header">

              <div className="brand">
        <div className="brand-icon">
            <img
                src="/ai-assistant.png"
                alt="AI Assistant"
            />
        </div>

        <div className="brand-details">
            <h1>AI Assistant</h1>
            <p>Your intelligent workspace</p>
        </div>
</div>
                <div className={`connection-status ${
                    isReady ? "ready" : connectionStatus === "Offline" ? "offline" : ""
                }`}>
                    <span className="status-dot"></span>
                    {connectionStatus}
                </div>

            </header>

            <main className="app-layout">

                <ChatWindow
                    isReady={isReady}
                    connectionStatus={connectionStatus}
                />

            </main>

            <footer className="app-footer">
                Powered by AI <span>·</span> Built to help you think better
            </footer>

        </div>
    );
}

export default App;

