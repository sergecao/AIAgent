# ui/ai_panel.py
import tkinter as tk
from tkinter import scrolledtext
import threading
from config import COLORS
from services.ai_service import AIService
from core.prompt_builder import PromptBuilder

class AIPanel:
    """Отдельная панель для AI-взаимодействия (чат + генерация)."""
    
    def __init__(self, parent, on_close=None):
        self.parent = parent
        self.on_close = on_close  # ← Callback для главного окна
        self.window = tk.Toplevel(parent)
        self.window.title("🤖 AI Ассистент")
        # geometry() убираем - позиционирует главное окно
        self.window.config(bg=COLORS["bg"])
        self.window.attributes('-topmost', True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close_request)  # ← Перехват закрытия
        
        self.ai_service = AIService()
        self.prompt_builder = PromptBuilder()
        self._create_ui()
    
    def _on_close_request(self):
        """Уведомляет главное окно о закрытии."""
        if self.on_close:
            self.on_close("ai")
        self.window.destroy()
    
    def _create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["header"], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="  🤖 AI Ассистент", bg=COLORS["header"], 
                 fg=COLORS["fg"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="✕", command=self._on_close_request,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)
        
        quick_frame = tk.Frame(self.window, bg=COLORS["bg"])
        quick_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(quick_frame, text="Быстрые команды:", bg=COLORS["bg"], 
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor=tk.W)
        cmds = [
            ("📊 Анализ", "Проанализируй это:"),
            ("💡 Идеи", "Предложи 5 идей для:"),
            ("📝 План", "Составь план для:"),
            ("✉️ Письмо", "Напиши письмо на тему:"),
            ("🔍 Резюме", "Сделай резюме текста:")
        ]
        for label, text in cmds:
            tk.Button(quick_frame, text=label, command=lambda t=text: self._insert_quick(t),
                      bg="#333333", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        self.chat_display = scrolledtext.ScrolledText(self.window, 
                                                       bg=COLORS["input_bg"], 
                                                       fg=COLORS["fg"],
                                                       font=("Consolas", 10),
                                                       relief=tk.FLAT,
                                                       wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        input_frame = tk.Frame(self.window, bg=COLORS["bg"])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        self.entry_query = tk.Entry(input_frame, font=("Segoe UI", 11),
                                    bg=COLORS["input_bg"], fg=COLORS["fg"],
                                    relief=tk.FLAT)
        self.entry_query.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry_query.bind("<Return>", lambda e: self._send_query())
        tk.Button(input_frame, text="🚀 Отправить", command=self._send_query,
                  bg="#007acc", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = tk.Label(self.window, text="Готов к работе",
                                   bg=COLORS["bg"], fg="#888888",
                                   font=("Segoe UI", 8), anchor=tk.W)
        self.lbl_status.pack(fill=tk.X, padx=20, pady=(0, 10))
    
    def _insert_quick(self, text):
        self.entry_query.delete(0, tk.END)
        self.entry_query.insert(0, text)
        self.entry_query.focus()
    
    def _send_query(self):
        query = self.entry_query.get().strip()
        if not query:
            return
        self.chat_display.insert(tk.END, f"\n👤 Вы: {query}\n")
        self.entry_query.delete(0, tk.END)
        self.lbl_status.config(text="ИИ думает...")
        threading.Thread(target=self._process_ai_query, args=(query,), daemon=True).start()
    
    def _process_ai_query(self, query):
        prompt = self.prompt_builder.build_system_prompt(query)
        self.ai_service.generate_text_async(
            prompt, 
            callback=lambda id, r: self._handle_response(r)
        )
    
    def _handle_response(self, response):
        self.chat_display.insert(tk.END, f"\n🤖 ИИ: {response}\n")
        self.chat_display.see(tk.END)
        self.lbl_status.config(text="Готов к работе")
    
    def log(self, text):
        self.chat_display.insert(tk.END, f"\n{text}\n")
        self.chat_display.see(tk.END)