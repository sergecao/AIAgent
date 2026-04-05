"""
Clipboard Monitor - Мониторинг буфера обмена.
Отслеживает копирование текста и предлагает действия.
"""
import tkinter as tk
from typing import Callable, Optional
import threading
import time


class ClipboardMonitor:
    """Мониторинг изменений в буфере обмена."""

    def __init__(self, root: tk.Tk, check_interval: float = 1.0):
        self.root = root
        self.check_interval = check_interval
        self.last_content = ""
        self.callbacks = []
        self.running = False
        self.thread = None

    def register_callback(self, callback: Callable[[str], None]):
        """Регистрация обработчика нового содержимого буфера."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        """Удаление обработчика."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def start(self):
        """Запустить мониторинг в фоновом потоке."""
        if self.running:
            return
        
        self.running = True
        try:
            # Получаем текущее содержимое
            self.last_content = self.root.clipboard_get()
        except Exception:
            self.last_content = ""
        
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Остановить мониторинг."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None

    def _monitor_loop(self):
        """Цикл проверки буфера обмена."""
        while self.running:
            try:
                current = self.root.clipboard_get()
                
                if current != self.last_content and current.strip():
                    self.last_content = current
                    # Вызываем колбэки в главном потоке
                    for callback in self.callbacks:
                        self.root.after(0, lambda c=current: callback(c))
                
            except Exception:
                pass
            
            time.sleep(self.check_interval)

    def get_current_content(self) -> str:
        """Получить текущее содержимое буфера."""
        try:
            return self.root.clipboard_get()
        except Exception:
            return ""

    def is_running(self) -> bool:
        """Проверить запущен ли мониторинг."""
        return self.running
