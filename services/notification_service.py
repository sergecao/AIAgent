"""
Notification Service - Pop-up уведомления о событиях.
Использует нативные уведомления ОС или встроенные окна.
"""
import tkinter as tk
from typing import Optional, Callable
import threading


class NotificationService:
    """Сервис показа уведомлений пользователю."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_notification = None
        self.auto_hide_delay = 5000  # 5 секунд по умолчанию

    def show(self, title: str, message: str, 
             duration_ms: int = None,
             on_click: Optional[Callable] = None):
        """
        Показать всплывающее уведомление.
        
        Args:
            title: Заголовок уведомления
            message: Текст сообщения
            duration_ms: Время авто-скрытия (мс), None = бесконечно
            on_click: Обработчик клика
        """
        duration_ms = duration_ms or self.auto_hide_delay
        
        # Создаем всплывающее окно
        notif = tk.Toplevel(self.root)
        notif.title(title)
        notif.overrideredirect(True)  # Без рамки
        
        # Стиль
        notif.configure(bg='#2b2b2b')
        notif.attributes('-topmost', True)
        
        # Размеры
        width, height = 300, 100
        
        # Позиция: правый нижний угол
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - width - 20
        y = screen_height - height - 50
        
        notif.geometry(f"{width}x{height}+{x}+{y}")
        
        # Контент
        frame = tk.Frame(notif, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        lbl_title = tk.Label(
            frame, text=title, 
            font=('Arial', 11, 'bold'),
            bg='#2b2b2b', fg='#4CAF50',
            anchor='w'
        )
        lbl_title.pack(fill=tk.X)
        
        lbl_message = tk.Label(
            frame, text=message,
            font=('Arial', 9),
            bg='#2b2b2b', fg='white',
            anchor='w', wraplength=270
        )
        lbl_message.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Обработчик клика
        if on_click:
            for widget in [notif, frame, lbl_title, lbl_message]:
                widget.bind('<Button-1>', lambda e: on_click())
                widget.bind('<Button-1>', lambda e: notif.destroy(), add='+')
        
        # Авто-скрытие
        if duration_ms > 0:
            notif.after(duration_ms, lambda: notif.destroy() if notif.winfo_exists() else None)
        
        self.current_notification = notif
        return notif

    def show_info(self, message: str, **kwargs):
        """Показать информационное уведомление."""
        return self.show("Информация", message, **kwargs)

    def show_warning(self, message: str, **kwargs):
        """Показать предупреждение."""
        return self.show("Предупреждение", message, **kwargs)

    def show_error(self, message: str, **kwargs):
        """Показать ошибку."""
        return self.show("Ошибка", message, **kwargs)

    def show_success(self, message: str, **kwargs):
        """Показать успешное действие."""
        return self.show("Готово", message, **kwargs)

    def hide_current(self):
        """Скрыть текущее уведомление."""
        if self.current_notification and self.current_notification.winfo_exists():
            self.current_notification.destroy()
            self.current_notification = None
