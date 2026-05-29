import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// In dev, /api and /health are proxied to the FastAPI backend so the frontend
// can use same-origin relative URLs. In production set VITE_API_BASE instead.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
