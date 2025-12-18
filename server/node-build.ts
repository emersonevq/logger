import path from "path";
import { createServer } from "./index";
import { createServer as createHttpServer } from "http";
import * as express from "express";
import { WebSocketManager } from "./websocket";

const app = createServer();
const port = process.env.PORT || 8080;

// In production, serve the built SPA files
const __dirname = import.meta.dirname;
const distPath = path.join(__dirname, "../spa");
const publicPath = path.join(__dirname, "../public");

// Serve static files from public directory
app.use(express.static(publicPath));

// Serve static files from dist/spa
app.use(express.static(distPath));

// Handle React Router - serve index.html for all non-API routes
app.get("*", (req, res) => {
  // Don't serve index.html for API routes
  if (req.path.startsWith("/api/") || req.path.startsWith("/health")) {
    return res.status(404).json({ error: "API endpoint not found" });
  }

  res.sendFile(path.join(distPath, "index.html"));
});

// Criar servidor HTTP com suporte a WebSocket
const httpServer = createHttpServer(app);
const wsManager = new WebSocketManager(httpServer);

httpServer.listen(port, () => {
  console.log(`🚀 Fusion Starter server running on port ${port}`);
  console.log(`📱 Frontend: http://localhost:${port}`);
  console.log(`🔧 API: http://localhost:${port}/api`);
  console.log(`🔗 WebSocket: ws://localhost:${port}/ws`);
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("🛑 Received SIGTERM, shutting down gracefully");
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("🛑 Received SIGINT, shutting down gracefully");
  process.exit(0);
});
