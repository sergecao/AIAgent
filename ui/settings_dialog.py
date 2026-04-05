"""
Settings Dialog - Диалог настроек приложения.
Позволяет настраивать авто-сохранение, пути и другие параметры.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import Dict, Any, Optional


class SettingsDialog:
    """Модальное окно настроек приложения."""

    def __init__(self, parent: tk.Tk, settings: Dict[str, Any], 
                 on_save: Optional[callable] = None):
        self.parent = parent
        self.settings = settings.copy()
        self.on_save = on_save
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._build_ui()
        
        # Центрирование
        self.dialog.update_idletasks()
        w = 450
        h = 400
        x = (parent.winfo_screenwidth() // 2) - (w // 2)
        y = (parent.winfo_screenheight() // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        """Построить интерфейс диалога."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка с настройками
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Вкладка "Основные"
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="Основные")
        self._build_general_tab(general_frame)
        
        # Вкладка "Хранилище"
        storage_frame = ttk.Frame(notebook, padding="10")
        notebook.add(storage_frame, text="Хранилище")
        self._build_storage_tab(storage_frame)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Сохранить", 
                   command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Отмена", 
                   command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _build_general_tab(self, parent):
        """Вкладка общих настроек."""
        # Авто-сохранение
        auto_save_var = tk.BooleanVar(value=self.settings.get('auto_save', True))
        self.settings['_auto_save_var'] = auto_save_var
        
        chk_auto = ttk.Checkbutton(
            parent, text="Авто-сохранение сессии (5 мин)",
            variable=auto_save_var
        )
        chk_auto.pack(anchor='w', pady=(0, 15))
        
        # Интервал проверки буфера
        lbl_interval = ttk.Label(parent, text="Интервал буфера (сек):")
        lbl_interval.pack(anchor='w')
        
        self.interval_spin = ttk.Spinbox(
            parent, from_=0.5, to=10.0, increment=0.5, width=10
        )
        self.interval_spin.set(self.settings.get('clipboard_interval', 1.0))
        self.interval_spin.pack(anchor='w', pady=(0, 15))

    def _build_storage_tab(self, parent):
        """Вкладка настроек хранилища."""
        # Путь к хранилищу
        lbl_path = ttk.Label(parent, text="Путь к хранилищу:")
        lbl_path.pack(anchor='w')
        
        path_frame = ttk.Frame(parent)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.insert(0, self.settings.get('storage_path', 'D:\\psa\\'))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="...", 
                   command=self._browse_path).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Резервное копирование
        backup_var = tk.BooleanVar(value=self.settings.get('backup_enabled', False))
        self.settings['_backup_var'] = backup_var
        
        chk_backup = ttk.Checkbutton(
            parent, text="Включить резервное копирование",
            variable=backup_var
        )
        chk_backup.pack(anchor='w')

    def _browse_path(self):
        """Выбор папки хранилища."""
        path = filedialog.askdirectory(initialdir=self.path_entry.get())
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _on_save(self):
        """Обработчик сохранения настроек."""
        # Собираем настройки
        new_settings = {
            'auto_save': self.settings['_auto_save_var'].get(),
            'clipboard_interval': float(self.interval_spin.get()),
            'storage_path': self.path_entry.get(),
            'backup_enabled': self.settings.get('_backup_var', tk.BooleanVar()).get()
        }
        
        self.result = new_settings
        
        if self.on_save:
            try:
                self.on_save(new_settings)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
                return
        
        self.dialog.destroy()

    def wait_for_result(self) -> Optional[Dict]:
        """Дождаться закрытия диалога и вернуть результат."""
        self.dialog.wait_window()
        return self.result
