"""
Layout Manager - Управление режимами отображения окна.
Режимы: Widget (мини), Extended (средний), Full (полный).
"""
import tkinter as tk
from typing import Tuple, Dict, Any


class LayoutMode:
    WIDGET = "widget"
    EXTENDED = "extended"
    FULL = "full"


class LayoutManager:
    """Управляет геометрией и видимостью элементов интерфейса."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_mode = LayoutMode.EXTENDED
        self.default_geometry = "400x600+100+100"
        
        # Конфигурация режимов
        self.configs: Dict[str, Dict[str, Any]] = {
            LayoutMode.WIDGET: {
                "geometry": "300x150+100+100",
                "resizable": (False, False),
                "show_elements": ["header", "input_mini"],
                "title_suffix": "[Mini]"
            },
            LayoutMode.EXTENDED: {
                "geometry": "450x500+100+100",
                "resizable": (True, True),
                "show_elements": ["header", "input", "history_short"],
                "title_suffix": ""
            },
            LayoutMode.FULL: {
                "geometry": "800x700+50+50",
                "resizable": (True, True),
                "show_elements": ["all"],
                "title_suffix": "[Full]"
            }
        }

    def set_mode(self, mode: str):
        """Переключить режим отображения."""
        if mode not in self.configs:
            return False
        
        self.current_mode = mode
        cfg = self.configs[mode]
        
        # Применяем геометрию
        self.root.geometry(cfg["geometry"])
        self.root.resizable(*cfg["resizable"])
        
        # Обновляем заголовок
        base_title = "AI Assistant"
        self.root.title(f"{base_title} {cfg['title_suffix']}")
        
        # Скрываем/показываем элементы (требуется регистрация элементов)
        # Реализуется через колбэки в UI
        return True

    def toggle_mode(self):
        """Циклическое переключение режимов."""
        order = [LayoutMode.WIDGET, LayoutMode.EXTENDED, LayoutMode.FULL]
        idx = order.index(self.current_mode)
        next_mode = order[(idx + 1) % len(order)]
        return self.set_mode(next_mode)

    def get_current_mode(self) -> str:
        return self.current_mode

    def register_element(self, name: str, widget: tk.Widget):
        """Регистрация элемента для управления видимостью."""
        if not hasattr(self, 'elements'):
            self.elements = {}
        self.elements[name] = widget

    def apply_visibility(self, mode: str = None):
        """Применить видимость элементов для текущего режима."""
        if not hasattr(self, 'elements'):
            return
            
        mode = mode or self.current_mode
        cfg = self.configs.get(mode)
        if not cfg:
            return

        show_all = "all" in cfg["show_elements"]
        allowed = cfg["show_elements"] if not show_all else []

        for name, widget in self.elements.items():
            if show_all or name in allowed:
                widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            else:
                widget.pack_forget()
