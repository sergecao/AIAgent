# ui/branch_panel.py
import tkinter as tk
from tkinter import ttk
from config import COLORS
from core.branch_manager import BranchManager

class BranchPanel:
    """Панель управления ветками контекста."""
    
    def __init__(self, parent, branch_manager: BranchManager, on_close=None):
        self.parent = parent
        self.manager = branch_manager
        self.on_close = on_close  # ← Callback для главного окна
        self.window = tk.Toplevel(parent)
        self.window.title("🌿 Ветки Контекста")
        # geometry() убираем - позиционирует главное окно
        self.window.config(bg=COLORS["bg"])
        self.window.attributes('-topmost', True)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close_request)  # ← Перехват закрытия
        self._create_ui()
        self._load_branches()

    def _on_close_request(self):
        """Уведомляет главное окно о закрытии."""
        if self.on_close:
            self.on_close("branch")
        self.window.destroy()

    def _create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["header"], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="  🌿 Ветки Контекста", bg=COLORS["header"], 
                 fg=COLORS["fg"], font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="✕", command=self._on_close_request,
                  bg=COLORS["header"], fg="#ff6b6b", relief=tk.FLAT).pack(side=tk.RIGHT, padx=10)
        
        create_frame = tk.Frame(self.window, bg=COLORS["bg"])
        create_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(create_frame, text="Новая ветка:", bg=COLORS["bg"], 
                 fg=COLORS["fg"]).pack(anchor=tk.W)
        self.entry_name = tk.Entry(create_frame, font=("Segoe UI", 10),
                                   bg=COLORS["input_bg"], fg=COLORS["fg"])
        self.entry_name.pack(fill=tk.X, pady=5)
        self.entry_role = tk.Entry(create_frame, font=("Segoe UI", 10),
                                   bg=COLORS["input_bg"], fg=COLORS["fg"])
        self.entry_role.insert(0, "default")
        self.entry_role.pack(fill=tk.X, pady=5)
        tk.Button(create_frame, text="➕ Создать ветку", command=self._create_branch,
                  bg="#28a745", fg="white", relief=tk.FLAT).pack(fill=tk.X, pady=5)
        
        tk.Label(self.window, text="Ваши ветки:", bg=COLORS["bg"], 
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20)
        self.tree = ttk.Treeview(self.window, columns=("name", "role", "items"), 
                                 show="headings", height=8)
        self.tree.heading("name", text="Название")
        self.tree.heading("role", text="Роль")
        self.tree.heading("items", text="Записей")
        self.tree.column("name", width=250)
        self.tree.column("role", width=150)
        self.tree.column("items", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self._on_branch_double_click)
        
        btn_frame = tk.Frame(self.window, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(btn_frame, text="🔄 Переключить", command=self._switch_branch,
                  bg="#007acc", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="👁 Контекст", command=self._view_context,
                  bg="#5a67d8", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 Удалить", command=self._delete_branch,
                  bg="#dc3545", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        
        self.lbl_current = tk.Label(self.window, text="Текущая ветка: None",
                                    bg=COLORS["input_bg"], fg=COLORS["fg"],
                                    font=("Segoe UI", 9), anchor=tk.W)
        self.lbl_current.pack(fill=tk.X, padx=20, pady=(0, 10))

    def _load_branches(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in self.manager.get_all_branches():
            self.tree.insert("", tk.END, iid=b["id"],
                            values=(b["name"], b["role"], b["context_items"]))
        current = self.manager.get_current_branch()
        if current:
            self.lbl_current.config(text=f"🟢 Текущая: {current['name']} ({current['role']})")
        else:
            self.lbl_current.config(text="⚪ Нет активной ветки")

    def _create_branch(self):
        name = self.entry_name.get().strip()
        role = self.entry_role.get().strip() or "default"
        if not name:
            return
        self.manager.create_branch(name, role=role)
        self.entry_name.delete(0, tk.END)
        self._load_branches()

    def _get_selected_id(self):
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _switch_branch(self):
        branch_id = self._get_selected_id()
        if branch_id:
            self.manager.switch_branch(branch_id)
            self._load_branches()

    def _view_context(self):
        branch_id = self._get_selected_id()
        if branch_id:
            self._open_context_window(branch_id)

    def _delete_branch(self):
        branch_id = self._get_selected_id()
        if branch_id:
            self.manager.delete_branch(branch_id)
            self._load_branches()

    def _on_branch_double_click(self, event):
        self._switch_branch()

    def _open_context_window(self, branch_id):
        ctx_window = tk.Toplevel(self.window)
        ctx_window.title("📄 Контекст ветки")
        ctx_window.geometry("500x400")
        ctx_window.config(bg=COLORS["bg"])
        txt = tk.Text(ctx_window, bg=COLORS["input_bg"], fg=COLORS["fg"],
                      font=("Consolas", 10), relief=tk.FLAT)
        txt.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        items = self.manager.get_context(branch_id)
        for item in items:
            txt.insert(tk.END, f"[{item['category']}] {item['content'][:100]}...\n")
            txt.insert(tk.END, f"  🕐 {item['timestamp'][:16]}\n\n")