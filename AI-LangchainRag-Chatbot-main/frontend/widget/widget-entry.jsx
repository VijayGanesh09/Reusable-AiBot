
import React from "react";
import { createRoot } from "react-dom/client";
import ChatWidget from "./ChatWidget";

const currentScript = document.currentScript;

if (currentScript) {
  const apiUrl = currentScript.dataset.apiUrl;

  if (!apiUrl) {
    console.error("Chatbot API URL is missing");
  } else {
    // Automatically load widget CSS
    const cssUrl = new URL("widget.css", currentScript.src).href;

    const stylesheet = document.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = cssUrl;
    document.head.appendChild(stylesheet);

    // Create widget container
    const container = document.createElement("div");
    container.id = "rag-chatbot-widget";
    document.body.appendChild(container);

    // Render chatbot
    const root = createRoot(container);

    root.render(
      <ChatWidget apiUrl={apiUrl.replace(/\/$/, "")} />
    );
  }
} else {
  console.error("Unable to detect chatbot widget script.");
}
