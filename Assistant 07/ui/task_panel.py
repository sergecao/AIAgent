# ui/task_panel.py
import tkinter as tk
from tkinter import ttk
from config import COLORS
from core.task_engine import TaskEngine

class TaskPanel:
    """Панель управления задачами в UI."""
    
    def __init__(self, parent, task_engine: TaskEngine, on_close=None):
        self.parent = parent
        self.engine = task_engine
        self.on_close = on_close  # ← Callback для главного окна
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Менеджер задач")
        # geometry() убираем - позиционирует главное окно
        self.window.config(bg=COLORS["bg"])
        self.window.attributes('-topmost', True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close_request)  # ← Перехват закрытия
        self._create_ui()
        self._load_tasks()

    def _on_close_request(self):
        """Уведомляет главное окно о закрытии."""
        if self.on_close:
            self.on_close("task")
        self.window.destroy()

    def _create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["header"], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="  Задачи", bg=COLORS["header"], 
                 fg=COLORS["fg"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="✕", command=self._on_close_request,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)
        
        form = tk.Frame(self.window, bg=COLORS["bg"])
        form.pack(fill=tk.X, padx=20, pady=10)
        self.entry_title = tk.Entry(form, font=("Segoe UI", 10),
                                    bg=COLORS["input_bg"], fg=COLORS["fg"])
        self.entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_title.bind("<Return>", lambda e: self._create_task())
        tk.Button(form, text="➕", command=self._create_task,
                  bg="#007acc", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT)
        
        filter_frame = tk.Frame(self.window, bg=COLORS["bg"])
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        self.filter_var = tk.StringVar(value="all")
        for status, label in [("all", "Все"), ("new", "Новые"), 
                               ("done", "Готовые"), ("archived", "Архив")]:
            tk.Radiobutton(filter_frame, text=label, variable=self.filter_var,
                          value=status, bg=COLORS["bg"], fg=COLORS["fg"],
                          command=self._load_tasks).pack(side=tk.LEFT, padx=5)
        
        self.tree = ttk.Treeview(self.window, columns=("id", "title", "status"), 
                                 show="headings", height=10)
        self.tree.heading("id", text="#")
        self.tree.heading("title", text="Задача")
        self.tree.heading("status", text="Статус")
        self.tree.column("id", width=40)
        self.tree.column("title", width=300)
        self.tree.column("status", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self._on_task_double_click)
        
        btn_frame = tk.Frame(self.window, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(btn_frame, text="✅ Готово", command=self._mark_done,
                  bg="#28a745", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 Удалить", command=self._delete_task,
                  bg="#dc3545", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📦 Архив", command=self._archive_completed,
                  bg="#6c757d", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)

    def _load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        status = self.filter_var.get()
        tasks = self.engine.get_tasks(None if status == "all" else status)
        for t in tasks:
            self.tree.insert("", tk.END, iid=t["id"],
                            values=(t["id"], t["title"][:40], t["status"]))

    def _create_task(self):
        title = self.entry_title.get().strip()
        if not title:
            return
        self.engine.create_task(title)
        self.entry_title.delete(0, tk.END)
        self._load_tasks()

    def _get_selected_id(self):
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

    def _mark_done(self):
        task_id = self._get_selected_id()
        if task_id:
            self.engine.update_status(task_id, "done")
            self._load_tasks()

    def _delete_task(self):
        task_id = self._get_selected_id()
        if task_id:
            self.engine.delete_task(task_id)
            self._load_tasks()

    def _archive_completed(self):
        self.engine.archive_completed()
        self._load_tasks()

    def _on_task_double_click(self, event):
        task_id = self._get_selected_id()
        if task_id:
            task = self.engine.get_task_by_id(task_id)
            if task:
                self.engine.update_status(task_id, "done" if task["status"] == "new" else "new")
                self._load_tasks()