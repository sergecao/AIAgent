# ui/window_controller.py
"""
Window Controller — управление панелями окна.

Отвечает за:
- Открытие/закрытие панелей
- Позиционирование панелей
- Трекер открытых окон
- Фокус на панелях
"""

import tkinter as tk
from typing import Dict, Optional


class WindowController:
    """Контроллер управления панелями главного окна."""
    
    def __init__(self, main_window):
        self.main = main_window
        self.root = main_window.root
        self.open_panels: Dict[str, Optional[tk.Toplevel]] = {
            "task": None, "session": None, "branch": None, "ai": None
        }

    def open_task_panel(self):
        """Открыть панель задач."""
        if self._is_panel_open("task"):
            self._focus_panel("task")
            return
        try:
            from ui.task_panel import TaskPanel
            if self.main.task_engine:
                panel = TaskPanel(self.root, self.main.task_engine, on_close=self._on_panel_close)
                self.open_panels["task"] = panel.window
                self._position_top_right(panel.window, 500, 450)
            else:
                self.main._log("⚠ TaskEngine не подключен")
        except Exception as e:
            self.main._log(f"Ошибка: {str(e)}")

    def open_session_panel(self):
        """Открыть панель сессий."""
        if self._is_panel_open("session"):
            self._focus_panel("session")
            return
        try:
            from ui.session_panel import SessionPanel
            if self.main.session_manager:
                panel = SessionPanel(self.root, self.main.session_manager, on_close=self._on_panel_close)
                self.open_panels["session"] = panel.window
                self._position_top_right(panel.window, 550, 600)
            else:
                self.main._log("⚠ SessionManager не подключен")
        except Exception as e:
            self.main._log(f"Ошибка: {str(e)}")

    def open_branch_panel(self):
        """Открыть панель веток."""
        if self._is_panel_open("branch"):
            self._focus_panel("branch")
            return
        try:
            from ui.branch_panel import BranchPanel
            if self.main.branch_manager:
                panel = BranchPanel(self.root, self.main.branch_manager, on_close=self._on_panel_close)
                self.open_panels["branch"] = panel.window
                self._position_top_right(panel.window, 550, 550)
            else:
                self.main._log("⚠ BranchManager не подключен")
        except Exception as e:
            self.main._log(f"Ошибка: {str(e)}")

    def open_ai_panel(self):
        """Открыть AI панель."""
        if self._is_panel_open("ai"):
            self._focus_panel("ai")
            return
        try:
            from ui.ai_panel import AIPanel
            panel = AIPanel(self.root, on_close=self._on_panel_close)
            self.open_panels["ai"] = panel.window
            self._position_top_right(panel.window, 550, 550)
        except Exception as e:
            self.main._log(f"Ошибка: {str(e)}")

    def _on_panel_close(self, panel_key: str):
        """Вызывается при закрытии панели."""
        if panel_key in self.open_panels:
            self.open_panels[panel_key] = None

    def close_all_panels(self):
        """Закрыть все открытые панели."""
        for panel_key, panel_window in self.open_panels.items():
            if panel_window and panel_window.winfo_exists():
                panel_window.destroy()
        self.open_panels = {k: None for k in self.open_panels}

    def _position_top_right(self, window: tk.Toplevel, width: int, height: int):
        """Позиционирует окно в правом верхнем углу с отступом."""
        sw = window.winfo_screenwidth()
        offset = len([p for p in self.open_panels.values() if p]) * 30
        window.geometry(f"{width}x{height}+{sw-width-30}+{30+offset}")

    def _is_panel_open(self, panel_key: str) -> bool:
        """Проверяет, открыта ли панель."""
        window = self.open_panels.get(panel_key)
        return window is not None and window.winfo_exists()

    def _focus_panel(self, panel_key: str):
        """Переводит фокус на открытую панель."""
        window = self.open_panels.get(panel_key)
        if window and window.winfo_exists():
            window.focus_force()
            window.attributes('-topmost', True)
            self.main._log("ℹ️ Панель уже открыта")

    def get_open_panel(self, panel_key: str) -> Optional[tk.Toplevel]:
        """Получить ссылку на открытую панель."""
        window = self.open_panels.get(panel_key)
        return window if window and window.winfo_exists() else None

    def get_panel_count(self) -> int:
        """Получить количество открытых панелей."""
        return len([p for p in self.open_panels.values() if p and p.winfo_exists()])