"""
Janela de alerta com screenshot
Mostra todos os 5 campos detectados
"""

import tkinter as tk
from tkinter import ttk
import threading
from PIL import Image, ImageTk
from monitor import CardData


class AlertWindow:
    """Janela de alerta quando todos os dados são detectados"""
    
    BG = '#0d1117'
    CARD_BG = '#161b22'
    TEXT = '#c9d1d9'
    DANGER = '#f85149'
    SUCCESS = '#3fb950'
    WARNING = '#d29922'
    ACCENT = '#58a6ff'
    
    def __init__(self):
        self.root = None
        self.is_showing = False
        self._photo = None
    
    def show(self, card_data: CardData, screenshot: Image.Image, url: str):
        """Mostra o alerta com todos os dados"""
        if self.is_showing:
            return
        
        self.is_showing = True
        
        thread = threading.Thread(
            target=self._create_window,
            args=(card_data, screenshot, url),
            daemon=True
        )
        thread.start()
    
    def _create_window(self, card_data: CardData, screenshot: Image.Image, url: str):
        """Cria a janela de alerta"""
        try:
            self.root = tk.Tk()
            self.root.title("🚨 ALERTA DE SEGURANÇA - DADOS COMPLETOS DETECTADOS")
            self.root.geometry("900x750")
            self.root.configure(bg=self.BG)
            self.root.attributes('-topmost', True)
            self.root.resizable(True, True)
            
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - 450
            y = (self.root.winfo_screenheight() // 2) - 375
            self.root.geometry(f"+{x}+{y}")
            
            main = tk.Frame(self.root, bg=self.BG, padx=25, pady=20)
            main.pack(fill='both', expand=True)
            
            header = tk.Frame(main, bg=self.BG)
            header.pack(fill='x')
            
            tk.Label(
                header, text="🚨",
                font=('Segoe UI Emoji', 48), bg=self.BG
            ).pack()
            
            tk.Label(
                header,
                text="TODOS OS DADOS DO CARTÃO DETECTADOS!",
                font=('Segoe UI', 18, 'bold'),
                fg=self.DANGER,
                bg=self.BG
            ).pack(pady=(5, 10))
            
            data_frame = tk.Frame(main, bg=self.CARD_BG, padx=20, pady=15)
            data_frame.pack(fill='x', pady=10)
            
            tk.Label(
                data_frame,
                text="💳 DADOS DETECTADOS:",
                font=('Segoe UI', 12, 'bold'),
                fg=self.ACCENT,
                bg=self.CARD_BG
            ).pack(anchor='w', pady=(0, 10))
            
            masked = card_data.get_masked()
            
            fields = [
                ("Número do Cartão:", masked['card'], self.DANGER),
                ("Data de Validade:", masked['expiry'], self.WARNING),
                ("CVV:", masked['cvv'], self.WARNING),
                ("Nome do Titular:", masked['name'], self.TEXT),
                ("CPF:", masked['cpf'], self.TEXT),
            ]
            
            for label, value, color in fields:
                row = tk.Frame(data_frame, bg=self.CARD_BG)
                row.pack(fill='x', pady=2)
                
                tk.Label(
                    row, text=label,
                    font=('Segoe UI', 10),
                    fg='#8b949e', bg=self.CARD_BG,
                    width=18, anchor='w'
                ).pack(side='left')
                
                tk.Label(
                    row, text=value,
                    font=('Consolas', 11, 'bold'),
                    fg=color, bg=self.CARD_BG
                ).pack(side='left')
            
            if url:
                tk.Label(
                    data_frame,
                    text=f"🌐 URL: {url[:65]}...",
                    font=('Consolas', 9),
                    fg='#8b949e',
                    bg=self.CARD_BG
                ).pack(anchor='w', pady=(10, 0))
            
            screenshot_frame = tk.Frame(main, bg=self.CARD_BG, padx=10, pady=10)
            screenshot_frame.pack(fill='both', expand=True, pady=10)
            
            tk.Label(
                screenshot_frame,
                text="📸 SCREENSHOT DA TELA (momento da detecção):",
                font=('Segoe UI', 11, 'bold'),
                fg=self.ACCENT,
                bg=self.CARD_BG
            ).pack(anchor='w', pady=(0, 5))
            
            display = screenshot.copy()
            display.thumbnail((850, 350), Image.Resampling.LANCZOS)
            self._photo = ImageTk.PhotoImage(display)
            
            screenshot_label = tk.Label(
                screenshot_frame,
                image=self._photo,
                bg=self.CARD_BG,
                relief='solid',
                borderwidth=2
            )
            screenshot_label.pack()
            
            warning_frame = tk.Frame(main, bg='#3d1a1a', padx=15, pady=12)
            warning_frame.pack(fill='x', pady=10)
            
            tk.Label(
                warning_frame,
                text="⚠️ VERIFIQUE ANTES DE CONTINUAR!",
                font=('Segoe UI', 13, 'bold'),
                fg='#ff6b6b',
                bg='#3d1a1a'
            ).pack()
            
            tk.Label(
                warning_frame,
                text="✓ O site tem HTTPS (cadeado)?    ✓ É o site oficial?    ✓ Você confia neste site?",
                font=('Segoe UI', 10),
                fg='#f8d7da',
                bg='#3d1a1a'
            ).pack(pady=(5, 0))
            
            btn_frame = tk.Frame(main, bg=self.BG)
            btn_frame.pack(fill='x', pady=15)
            
            def close():
                self.is_showing = False
                self.root.destroy()
            
            tk.Button(
                btn_frame,
                text="✓ Entendi, o site é seguro",
                font=('Segoe UI', 11, 'bold'),
                fg='white', bg=self.SUCCESS,
                activebackground='#2ea043',
                relief='flat', padx=25, pady=10,
                cursor='hand2',
                command=close
            ).pack(side='right', padx=5)
            
            tk.Button(
                btn_frame,
                text="🛑 Não tenho certeza!",
                font=('Segoe UI', 11, 'bold'),
                fg='white', bg=self.DANGER,
                activebackground='#da3633',
                relief='flat', padx=25, pady=10,
                cursor='hand2',
                command=close
            ).pack(side='right', padx=5)
            
            try:
                import winsound
                for _ in range(3):
                    winsound.Beep(800, 150)
                    winsound.Beep(600, 150)
            except:
                self.root.bell()
            
            self.root.protocol("WM_DELETE_WINDOW", close)
            self.root.mainloop()
            
        except Exception as e:
            print(f"Erro na janela de alerta: {e}")
        finally:
            self.is_showing = False
