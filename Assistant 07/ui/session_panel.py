# ui/session_panel.py
"""
Session Panel — панель управления сессиями в UI.

Отвечает за:
- Запуск/остановка сессий
- Просмотр истории сессий
- Восстановление последней сессии
- Просмотр деталей сессии
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import COLORS
from core.session_manager import SessionManager


class SessionPanel:
    """Панель управления сессиями в UI."""
    
    def __init__(self, parent, session_manager: SessionManager, on_close=None):
        self.parent = parent
        self.manager = session_manager
        self.on_close = on_close
        self.window = tk.Toplevel(parent)
        self.window.title("⏱ Сессии")
        self.window.config(bg=COLORS["bg"])
        self.window.attributes('-topmost', True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close_request)
        self._create_ui()
        self._update_status()
        self._load_history()

    def _on_close_request(self):
        """Уведомляет главное окно о закрытии."""
        if self.on_close:
            self.on_close("session")
        self.window.destroy()

    def _create_ui(self):
        """Создание интерфейса панели."""
        header = tk.Frame(self.window, bg=COLORS["header"], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="  Сессии", bg=COLORS["header"], 
                 fg=COLORS["fg"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="✕", command=self._on_close_request,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)
        
        self.status_frame = tk.Frame(self.window, bg=COLORS["bg"])
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        self.lbl_status = tk.Label(self.status_frame, text="Нет активной сессии",
                                   bg=COLORS["input_bg"], fg=COLORS["fg"],
                                   font=("Segoe UI", 10), padx=10, pady=5)
        self.lbl_status.pack(fill=tk.X)
        
        ctrl_frame = tk.Frame(self.window, bg=COLORS["bg"])
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(ctrl_frame, text="Название:", bg=COLORS["bg"], 
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.entry_title = tk.Entry(ctrl_frame, font=("Segoe UI", 10),
                                    bg=COLORS["input_bg"], fg=COLORS["fg"])
        self.entry_title.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(ctrl_frame, text="Теги (через запятую):", bg=COLORS["bg"], 
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor=tk.W)
        self.entry_tags = tk.Entry(ctrl_frame, font=("Segoe UI", 10),
                                   bg=COLORS["input_bg"], fg=COLORS["fg"])
        self.entry_tags.pack(fill=tk.X, pady=(0, 10))
        self.entry_tags.insert(0, "#работа, #фокус")
        
        btn_row = tk.Frame(ctrl_frame, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X)
        self.btn_start = tk.Button(btn_row, text="▶ Старт", command=self._start_session,
                                   bg="#28a745", fg="white", relief=tk.FLAT)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        self.btn_stop = tk.Button(btn_row, text="⏹ Стоп", command=self._stop_session,
                                  bg="#dc3545", fg="white", relief=tk.FLAT, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.window, text="История сессий:", bg=COLORS["bg"], 
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20)
        self.tree = ttk.Treeview(self.window, columns=("id", "title", "tags", "start"), 
                                 show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("tags", text="Теги")
        self.tree.heading("start", text="Начало")
        self.tree.column("id", width=100)
        self.tree.column("title", width=200)
        self.tree.column("tags", width=150)
        self.tree.column("start", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self._on_session_double_click)
        
        btn_frame = tk.Frame(self.window, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(btn_frame, text="📂 Открыть", command=self._open_session,
                  bg="#007acc", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Восстановить", command=self._restore_last,
                  bg="#6c757d", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        
        self.lbl_token_stats = tk.Label(self.window, text="",
                                        bg=COLORS["bg"], fg="#888888",
                                        font=("Segoe UI", 8), anchor=tk.W)
        self.lbl_token_stats.pack(fill=tk.X, padx=20, pady=(0, 10))

    def _update_status(self):
        """Обновление статуса активной сессии."""
        session = self.manager.current_session
        if session:
            tags = ", ".join(session.get('tags', []))
            tag_text = f" [{tags}]" if tags else ""
            self.lbl_status.config(text=f"🟢 Активна: {session['title']}{tag_text}", bg="#1f5f2f")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.lbl_status.config(text="Нет активной сессии", bg=COLORS["input_bg"])
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def _start_session(self):
        """Запуск новой сессии."""
        title = self.entry_title.get().strip()
        if not title:
            title = f"Сессия {datetime.now().strftime('%H:%M')}"
        tags_text = self.entry_tags.get().strip()
        tags = [t.strip() for t in tags_text.split(',') if t.strip()]
        self.manager.start_session(title, tags=tags)
        self.entry_title.delete(0, tk.END)
        self._update_status()
        self._load_history()

    def _stop_session(self):
        """Остановка текущей сессии."""
        self.manager.end_session()
        self._update_status()
        self._load_history()

    def _load_history(self):
        """Загрузка истории сессий в таблицу."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in self.manager.get_history(20):
            tags = ", ".join(s.get('tags', []))[:20]
            self.tree.insert("", tk.END, values=(s["id"][:12], s["title"][:25], tags, s["start"][:16]))

    def _open_session(self):
        """Открыть детали выбранной сессии."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            session_id = str(item["values"][0])  # ← ИСПРАВЛЕНО: конвертация в str
            self._open_session_details(session_id)

    def _open_session_details(self, session_id: str):
        """Открыть окно с деталями сессии."""
        files = self.manager.storage.list_files("sessions", ".json")
        for f in files:
            if f.startswith(session_id):  # ← Теперь работает (оба str)
                data = self.manager.storage.read_json("sessions", f)
                if data:
                    self._show_session_details(data)
                break

    def _show_session_details(self, data: dict):
        """Показать детали сессии в новом окне."""
        details_window = tk.Toplevel(self.window)
        details_window.title(f"📄 {data.get('title', 'Сессия')}")
        details_window.geometry("500x400")
        details_window.config(bg=COLORS["bg"])
        txt = tk.Text(details_window, bg=COLORS["input_bg"], fg=COLORS["fg"],
                      font=("Consolas", 10), relief=tk.FLAT)
        txt.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        txt.insert(tk.END, f"Название: {data.get('title', 'N/A')}\n")
        txt.insert(tk.END, f"Теги: {', '.join(data.get('tags', []))}\n")
        txt.insert(tk.END, f"Начало: {data.get('start_time', 'N/A')}\n")
        txt.insert(tk.END, f"Конец: {data.get('end_time', 'Активна')}\n")
        txt.insert(tk.END, f"Статус: {data.get('status', 'N/A')}\n\n")
        txt.insert(tk.END, "КОНТЕКСТ:\n")
        for key, value in data.get('context', {}).items():
            txt.insert(tk.END, f"  {key}: {value}\n")

    def _restore_last(self):
        """Восстановить последнюю сессию."""
        session = self.manager.restore_last_session()
        if session:
            self._update_status()
            self._load_history()

    def _on_session_double_click(self, event):
        """Двойной клик по сессии = восстановить."""
        self._restore_last()

    def update_token_stats(self, stats: dict):
        """Обновить статистику токенов."""
        if stats:
            text = (f"💾 Токены: ориг={stats.get('original_tokens', 0)}, "
                    f"оптим={stats.get('optimized_tokens', 0)}, "
                    f"экономия={stats.get('savings_percent', 0)}%")
            self.lbl_token_stats.config(text=text)