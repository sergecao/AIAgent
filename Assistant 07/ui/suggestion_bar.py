# ui/suggestion_bar.py
import tkinter as tk
from config import COLORS

class SuggestionBar:
    """Панель с 3 интерактивными кнопками от ИИ."""
    
    def __init__(self, parent, on_click_callback):
        self.parent = parent
        self.on_click = on_click_callback
        self.frame = tk.Frame(parent, bg=COLORS["bg"])
        self.buttons = []
        self._create_ui()
    
    def _create_ui(self):
        tk.Label(self.frame, text="💡 Предложения ИИ:",
                 bg=COLORS["bg"], fg="#888888",
                 font=("Segoe UI", 9)).pack(pady=(5, 0))
        
        btn_frame = tk.Frame(self.frame, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X, pady=5)
        
        for i in range(3):
            btn = tk.Button(btn_frame, text=f"Вариант {i+1}",
                            bg="#333333", fg="white",
                            font=("Segoe UI", 9),
                            relief=tk.FLAT, cursor="hand2",
                            command=lambda idx=i: self._handle_click(idx))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            self.buttons.append(btn)
        
        self.hide()
    
    def show(self, suggestions: list):
        """Показать кнопки с текстом из JSON."""
        self.frame.pack(fill=tk.X, padx=20)
        for i, btn in enumerate(self.buttons):
            if i < len(suggestions):
                label = suggestions[i].get("label", f"Действие {i+1}")
                btn.config(text=label, bg="#007acc")
                btn.data = suggestions[i] # Сохраняем данные
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            else:
                btn.pack_forget()
    
    def hide(self):
        self.frame.pack_forget()
    
    def _handle_click(self, index):
        btn = self.buttons[index]
        if hasattr(btn, 'data'):
            self.on_click(btn.data)