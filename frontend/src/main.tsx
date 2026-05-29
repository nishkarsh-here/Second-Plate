import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { ThemeProvider } from "./state/theme";
import { AppStateProvider } from "./state/appState";
import "./index.css";
import "leaflet/dist/leaflet.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false, staleTime: 30_000, retry: 1 },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AppStateProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AppStateProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
