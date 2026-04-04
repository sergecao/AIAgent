# ui/floating_window.py
"""
Floating Window — главное окно AI Assistant.

Отвечает за:
- Создание основного окна
- Позиционирование на экране
- Базовые UI компоненты
- Перетаскивание окна
"""

import tkinter as tk
from config import COLORS
from ui.components import UIComponents
from ui.suggestion_bar import SuggestionBar
from ui.window_controller import WindowController
from ui.window_actions import WindowActions


class FloatingAssistant:
    """Главное окно AI Assistant со всеми панелями."""
    
    def __init__(self, root, task_engine=None, session_manager=None, branch_manager=None):
        self.root = root
        self.root.title("AI Assistant")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.config(bg=COLORS["bg"])
        self.width, self.height = 400, 500
        
        # Движки
        self.task_engine = task_engine
        self.session_manager = session_manager
        self.branch_manager = branch_manager
        
        # Контроллеры
        self.controller = WindowController(self)
        self.actions = WindowActions(self)
        
        self._setup_position()
        self._setup_ui()
        
        # Сервисы для действий
        self.actions.setup_services()
        
        self.suggestion_bar = SuggestionBar(self.root, self._on_suggestion_click)
        self.root.bind("<Map>", self._on_restore)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._drag_data = {"x": 0, "y": 0}

    def _setup_position(self):
        """Позиция: правый верхний угол экрана."""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}+{sw-self.width-30}+30")

    def _setup_ui(self):
        """Создание интерфейса."""
        # Заголовок
        self.header_frame, self.lbl_title = UIComponents.create_header(
            self.root, "AI Assistant", self._start_move, self._do_move)
        
        # Кнопки заголовка
        tk.Button(self.header_frame, text="▁", command=self._minimize,
                  bg=COLORS["header"], fg=COLORS["fg"], relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        tk.Button(self.header_frame, text="✕", command=self._on_close,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        
        # Кнопки панелей
        tk.Button(self.header_frame, text="📋", command=self.controller.open_task_panel,
                  bg=COLORS["header"], fg=COLORS["fg"], relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(self.header_frame, text="⏱", command=self.controller.open_session_panel,
                  bg=COLORS["header"], fg=COLORS["fg"], relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(self.header_frame, text="🌿", command=self.controller.open_branch_panel,
                  bg=COLORS["header"], fg="#90EE90", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(self.header_frame, text="🤖", command=self.controller.open_ai_panel,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # Поле ввода
        self.entry_query = tk.Entry(self.root, font=("Segoe UI", 11),
                                    bg=COLORS["input_bg"], fg=COLORS["fg"], relief=tk.FLAT)
        self.entry_query.pack(pady=10, padx=20, fill=tk.X, ipady=5)
        self.entry_query.bind("<Return>", lambda e: self.actions.run_search())
        
        # Кнопки действий
        bf = tk.Frame(self.root, bg=COLORS["bg"])
        bf.pack(pady=5)
        tk.Button(bf, text="🔍 Найти", command=self.actions.run_search,
                  bg="#007acc", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(bf, text="📝 Текст", command=self._toggle_text_opts,
                  bg="#5a67d8", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(bf, text="🔗 Ссылки", command=self.actions.open_links,
                  bg="#28a745", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(bf, text="🤖 ИИ", command=self.controller.open_ai_panel,
                  bg="#ff6b6b", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        # Опции текста
        self.text_opts = tk.Frame(self.root, bg=COLORS["bg"])
        tk.Button(self.text_opts, text="Улучшить", command=lambda: self.actions.process_text("улучшить"),
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        tk.Button(self.text_opts, text="Кратко", command=lambda: self.actions.process_text("кратко"),
                  relief=tk.FLAT).pack(side=tk.LEFT, padx=2)
        
        # Результат и статус
        self.txt_result = UIComponents.create_text_area(self.root)
        self.lbl_status = UIComponents.create_status_bar(self.root)

    def _start_move(self, e):
        self._drag_data = {"x": e.x, "y": e.y}

    def _do_move(self, e):
        dx = e.x - self._drag_data["x"]
        dy = e.y - self._drag_data["y"]
        self.root.geometry(f"+{self.root.winfo_x()+dx}+{self.root.winfo_y()+dy}")

    def _minimize(self):
        """Сворачивание в правый нижний угол."""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw-self.width-30}+{sh-100}")
        self.root.overrideredirect(False)
        self.root.attributes('-topmost', False)
        self.root.iconify()

    def _on_restore(self, e):
        """Восстановление из свёрнутого состояния."""
        self.root.after(100, lambda: [
            self.root.overrideredirect(True),
            self.root.attributes('-topmost', True),
            self._setup_position()
        ])

    def _on_close(self):
        """Закрытие приложения с очисткой."""
        self.controller.close_all_panels()
        if self.session_manager:
            self.session_manager.stop_auto_save()
        self.root.quit()

    def _on_suggestion_click(self, data):
        """Обработка клика по предложению ИИ."""
        self._log(f"\n✅ Выбрано: {data.get('label')}")
        self.actions.handle_suggestion(data)

    def _toggle_text_opts(self):
        """Показать/скрыть опции текста."""
        if self.text_opts.winfo_viewable():
            self.text_opts.pack_forget()
        else:
            self.text_opts.pack(pady=5, padx=20, fill=tk.X)

    def _log(self, text):
        """Логирование в текстовое поле."""
        self.txt_result.insert(tk.END, text + "\n")
        self.txt_result.see(tk.END)

    def _set_status(self, text):
        """Установка статуса."""
        self.lbl_status.config(text=text)