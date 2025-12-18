"""
Ícone na bandeja do sistema (System Tray)
Permite controlar o programa em segundo plano
"""

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


class SystemTrayIcon:
    """Gerencia o ícone na bandeja do sistema"""
    
    def __init__(
        self,
        on_show: Optional[Callable] = None,
        on_toggle: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        on_autostart_toggle: Optional[Callable] = None
    ):
        self.on_show = on_show
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.on_autostart_toggle = on_autostart_toggle
        
        self.icon: Optional[pystray.Icon] = None
        self.is_monitoring = False
        self.is_autostart_enabled = False
        self._thread: Optional[threading.Thread] = None
    
    def _create_icon_image(self, color: str = '#4ecca3') -> Image.Image:
        """Cria imagem do ícone"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        shield_color = color
        
        draw.polygon([
            (32, 5),
            (55, 15),
            (55, 35),
            (32, 58),
            (9, 35),
            (9, 15),
        ], fill=shield_color, outline='white')
        
        draw.rectangle([20, 25, 44, 38], fill='white')
        draw.rectangle([22, 32, 32, 35], fill=shield_color)
        
        return image
    
    def _get_menu(self) -> pystray.Menu:
        """Cria o menu de contexto"""
        
        def toggle_monitoring(icon, item):
            if self.on_toggle:
                self.on_toggle()
        
        def show_window(icon, item):
            if self.on_show:
                self.on_show()
        
        def toggle_autostart(icon, item):
            if self.on_autostart_toggle:
                self.on_autostart_toggle()
        
        def exit_app(icon, item):
            if self.on_exit:
                self.on_exit()
            self.stop()
        
        status_text = "✅ Monitorando" if self.is_monitoring else "⏸️ Pausado"
        autostart_text = "✅ Iniciar com Windows" if self.is_autostart_enabled else "⬜ Iniciar com Windows"
        
        return pystray.Menu(
            pystray.MenuItem(
                "🔒 Card Security Monitor",
                show_window,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                status_text,
                toggle_monitoring
            ),
            pystray.MenuItem(
                "▶️ Iniciar" if not self.is_monitoring else "⏹️ Parar",
                toggle_monitoring
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                autostart_text,
                toggle_autostart
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ Sair",
                exit_app
            )
        )
    
    def update_status(self, is_monitoring: bool, is_autostart_enabled: bool = None):
        """Atualiza o status do ícone"""
        self.is_monitoring = is_monitoring
        
        if is_autostart_enabled is not None:
            self.is_autostart_enabled = is_autostart_enabled
        
        if self.icon:
            color = '#4ecca3' if is_monitoring else '#6c757d'
            self.icon.icon = self._create_icon_image(color)
            
            self.icon.menu = self._get_menu()
            
            status = "Monitorando" if is_monitoring else "Pausado"
            self.icon.title = f"Card Security - {status}"
    
    def show_notification(self, title: str, message: str):
        """Mostra notificação do sistema"""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except:
                pass
    
    def start(self):
        """Inicia o ícone na bandeja"""
        if not HAS_PYSTRAY:
            return
        
        def run_icon():
            self.icon = pystray.Icon(
                "card_security",
                self._create_icon_image(),
                "Card Security Monitor",
                self._get_menu()
            )
            self.icon.run()
        
        self._thread = threading.Thread(target=run_icon, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Para o ícone"""
        if self.icon:
            self.icon.stop()
            self.icon = None
