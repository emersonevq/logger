"""
Janela de alerta de segurança com screenshot
Mostra quando TODOS os dados do cartão são detectados
"""

import tkinter as tk
from tkinter import ttk
import threading
from typing import Optional
from PIL import Image, ImageTk
from pattern_detector import CardData


class AlertWindow:
    """Janela de alerta com screenshot da tela"""
    
    BG_COLOR = '#0d1117'
    CARD_BG = '#161b22'
    TEXT_COLOR = '#c9d1d9'
    DANGER_COLOR = '#f85149'
    WARNING_COLOR = '#d29922'
    SUCCESS_COLOR = '#3fb950'
    ACCENT_COLOR = '#58a6ff'
    
    def __init__(self):
        self.root = None
        self.is_showing = False
        self.photo_image = None
    
    def show(self, card_data: CardData, screenshot: Image.Image):
        """Mostra o alerta com dados e screenshot"""
        if self.is_showing:
            return
        
        self.is_showing = True
        
        thread = threading.Thread(
            target=self._create_window,
            args=(card_data, screenshot),
            daemon=True
        )
        thread.start()
    
    def _create_window(self, card_data: CardData, screenshot: Image.Image):
        """Cria a janela de alerta"""
        try:
            self.root = tk.Tk()
            self.root.title("🚨 ALERTA DE SEGURANÇA - DADOS DE CARTÃO DETECTADOS")
            self.root.geometry("900x750")
            self.root.configure(bg=self.BG_COLOR)
            self.root.attributes('-topmost', True)
            self.root.resizable(True, True)
            self.root.minsize(800, 650)
            
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - 450
            y = (self.root.winfo_screenheight() // 2) - 375
            self.root.geometry(f"+{x}+{y}")
            
            main_canvas = tk.Canvas(self.root, bg=self.BG_COLOR, highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
            scrollable_frame = tk.Frame(main_canvas, bg=self.BG_COLOR)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            )
            
            main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            main_canvas.configure(yscrollcommand=scrollbar.set)
            
            main_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
            scrollbar.pack(side="right", fill="y")
            
            header = tk.Frame(scrollable_frame, bg=self.BG_COLOR)
            header.pack(fill='x', pady=(0, 15))
            
            self.alert_icon = tk.Label(
                header,
                text="🚨",
                font=('Segoe UI Emoji', 48),
                bg=self.BG_COLOR
            )
            self.alert_icon.pack()
            
            tk.Label(
                header,
                text="DADOS COMPLETOS DE CARTÃO DETECTADOS!",
                font=('Segoe UI', 20, 'bold'),
                fg=self.DANGER_COLOR,
                bg=self.BG_COLOR
            ).pack(pady=(10, 5))
            
            tk.Label(
                header,
                text="Todos os campos do formulário de pagamento foram preenchidos",
                font=('Segoe UI', 11),
                fg=self.TEXT_COLOR,
                bg=self.BG_COLOR
            ).pack()
            
            data_frame = tk.Frame(scrollable_frame, bg=self.CARD_BG, padx=20, pady=15)
            data_frame.pack(fill='x', pady=15)
            
            tk.Label(
                data_frame,
                text="💳 DADOS DETECTADOS:",
                font=('Segoe UI', 12, 'bold'),
                fg=self.ACCENT_COLOR,
                bg=self.CARD_BG
            ).pack(anchor='w', pady=(0, 10))
            
            masked_data = card_data.get_masked_data()
            
            data_grid = tk.Frame(data_frame, bg=self.CARD_BG)
            data_grid.pack(fill='x')
            
            fields = [
                ("Número do Cartão:", masked_data['card_number'], self.DANGER_COLOR),
                ("Bandeira:", masked_data['card_brand'], self.TEXT_COLOR),
                ("Validade:", masked_data['expiry_date'], self.WARNING_COLOR),
                ("CVV:", masked_data['cvv'], self.WARNING_COLOR),
                ("Titular:", masked_data['holder_name'], self.TEXT_COLOR),
                ("CPF:", masked_data['cpf'], self.TEXT_COLOR),
            ]
            
            for i, (label, value, color) in enumerate(fields):
                row = tk.Frame(data_grid, bg=self.CARD_BG)
                row.pack(fill='x', pady=2)
                
                tk.Label(
                    row,
                    text=label,
                    font=('Segoe UI', 10),
                    fg='#8b949e',
                    bg=self.CARD_BG,
                    width=18,
                    anchor='w'
                ).pack(side='left')
                
                tk.Label(
                    row,
                    text=value,
                    font=('Consolas', 11, 'bold'),
                    fg=color,
                    bg=self.CARD_BG,
                    anchor='w'
                ).pack(side='left', padx=(10, 0))
            
            screenshot_frame = tk.Frame(scrollable_frame, bg=self.CARD_BG, padx=10, pady=10)
            screenshot_frame.pack(fill='x', pady=15)
            
            tk.Label(
                screenshot_frame,
                text="📸 SCREENSHOT DA TELA (momento da detecção):",
                font=('Segoe UI', 12, 'bold'),
                fg=self.ACCENT_COLOR,
                bg=self.CARD_BG
            ).pack(anchor='w', pady=(0, 10))
            
            screenshot_display = screenshot.copy()
            screenshot_display.thumbnail((850, 400), Image.Resampling.LANCZOS)
            
            self.photo_image = ImageTk.PhotoImage(screenshot_display)
            
            screenshot_label = tk.Label(
                screenshot_frame,
                image=self.photo_image,
                bg=self.CARD_BG,
                relief='solid',
                borderwidth=2
            )
            screenshot_label.pack(pady=5)
            
            if card_data.window_title:
                tk.Label(
                    screenshot_frame,
                    text=f"🌐 Janela: {card_data.window_title[:70]}...",
                    font=('Segoe UI', 9),
                    fg='#8b949e',
                    bg=self.CARD_BG
                ).pack(anchor='w', pady=(5, 0))
            
            warning_frame = tk.Frame(scrollable_frame, bg='#3d1a1a', padx=20, pady=15)
            warning_frame.pack(fill='x', pady=15)
            
            tk.Label(
                warning_frame,
                text="⚠️ VERIFIQUE ANTES DE CONTINUAR!",
                font=('Segoe UI', 14, 'bold'),
                fg='#ff6b6b',
                bg='#3d1a1a'
            ).pack(anchor='w', pady=(0, 10))
            
            checklist = """✓ O site tem HTTPS? (cadeado verde no navegador)
✓ É realmente o site oficial? (verifique a URL)
✓ Você está em uma rede segura? (não use Wi-Fi público)
✓ Conhece e confia neste site?
✓ A compra foi iniciada por você?

❌ SINAIS DE PERIGO:
• URL estranha ou com erros de digitação
• Site sem cadeado de segurança
• Link recebido por e-mail ou WhatsApp
• Preços muito abaixo do mercado
• Pressão para finalizar rápido"""
            
            tk.Label(
                warning_frame,
                text=checklist,
                font=('Segoe UI', 10),
                fg='#f8d7da',
                bg='#3d1a1a',
                justify='left'
            ).pack(anchor='w')
            
            btn_frame = tk.Frame(scrollable_frame, bg=self.BG_COLOR)
            btn_frame.pack(fill='x', pady=20)
            
            def close_safe():
                """Fecha indicando que é seguro"""
                self.is_showing = False
                self.root.destroy()
            
            def close_cancel():
                """Fecha indicando para cancelar"""
                self.is_showing = False
                self.root.destroy()
            
            safe_btn = tk.Button(
                btn_frame,
                text="✓ Verifiquei, é seguro continuar",
                font=('Segoe UI', 11, 'bold'),
                fg='white',
                bg=self.SUCCESS_COLOR,
                activebackground='#2ea043',
                relief='flat',
                padx=25,
                pady=12,
                cursor='hand2',
                command=close_safe
            )
            safe_btn.pack(side='right', padx=10)
            
            cancel_btn = tk.Button(
                btn_frame,
                text="🛑 Não tenho certeza - PARAR",
                font=('Segoe UI', 11, 'bold'),
                fg='white',
                bg=self.DANGER_COLOR,
                activebackground='#da3633',
                relief='flat',
                padx=25,
                pady=12,
                cursor='hand2',
                command=close_cancel
            )
            cancel_btn.pack(side='right', padx=10)
            
            self._play_alert_sound()
            
            self._animate_icon()
            
            self.root.protocol("WM_DELETE_WINDOW", close_safe)
            self.root.mainloop()
            
        except Exception as e:
            print(f"Erro ao criar janela de alerta: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_showing = False
    
    def _play_alert_sound(self):
        """Toca som de alerta"""
        try:
            import winsound
            for _ in range(3):
                winsound.Beep(800, 200)
                winsound.Beep(600, 200)
        except:
            try:
                self.root.bell()
            except:
                pass
    
    def _animate_icon(self):
        """Anima o ícone de alerta (pisca)"""
        def blink():
            if not self.is_showing or not self.root:
                return
            
            try:
                current = self.alert_icon.cget('fg')
                new_color = self.DANGER_COLOR if current != self.DANGER_COLOR else '#0d1117'
                self.alert_icon.config(fg=new_color)
                self.root.after(500, blink)
            except:
                pass
        
        if self.root:
            self.root.after(500, blink)
