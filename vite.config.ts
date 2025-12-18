import { defineConfig, Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { createServer } from "./server";
import { WebSocketManager } from "./server/websocket";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    fs: {
      allow: [".", "./client", "./shared"],
      deny: [".env", ".env.*", "*.{crt,pem}", "**/.git/**", "server/**"],
    },
  },
  build: {
    outDir: "dist/spa",
  },
  plugins: [react(), expressPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./client"),
      "@shared": path.resolve(__dirname, "./shared"),
    },
  },
}));

function expressPlugin(): Plugin {
  let wsManager: WebSocketManager;

  return {
    name: "express-plugin",
    apply: "serve",
    configureServer(server) {
      const app = createServer();

      // Initialize WebSocket manager with Vite's HTTP server
      if (server.httpServer) {
        wsManager = new WebSocketManager(server.httpServer);
        console.log("✅ WebSocket initialized on ws://localhost:8080/ws");
      }

      // Add Express app as middleware to Vite dev server
      server.middlewares.use(app);
    },
  };
}
