import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  build: {
    lib: {
      entry: "widget/widget-entry.jsx",
      name: "RAGChatWidget",
      formats: ["iife"],
      fileName: () => "widget.js",
      cssFileName: "widget"
    },

    outDir: "dist-widget",
    emptyOutDir: true,
  }
});