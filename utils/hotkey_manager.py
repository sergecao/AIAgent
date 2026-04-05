"""
Hotkey Manager - Глобальные горячие клавиши.
Поддержка Ctrl+Alt+A и других комбинаций.
"""
import tkinter as tk
from typing import Callable, Dict, Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class HotkeyManager:
    """Управление глобальными горячими клавишами."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.listeners = []
        self.hotkeys: Dict[str, Callable] = {}
        self._active_keys = set()
        self.listener = None

    def register_hotkey(self, key_combo: str, callback: Callable):
        """
        Регистрация горячей клавиши.
        key_combo: строка вида 'ctrl+alt+a' или 'ctrl+shift+s'
        """
        if not PYNPUT_AVAILABLE:
            return False
        
        key_combo = key_combo.lower()
        self.hotkeys[key_combo] = callback
        
        # Запускаем слушатель если еще не запущен
        if self.listener is None:
            self._start_listener()
        
        return True

    def _start_listener(self):
        """Запустить фоновый слушатель клавиатуры."""
        def on_press(key):
            try:
                k = str(key).replace('Key.', '').lower()
                self._active_keys.add(k)
                self._check_hotkeys()
            except Exception:
                pass

        def on_release(key):
            try:
                k = str(key).replace('Key.', '').lower()
                self._active_keys.discard(k)
            except Exception:
                pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def _check_hotkeys(self):
        """Проверить нажатые комбинации."""
        for combo, callback in self.hotkeys.items():
            keys = combo.split('+')
            if all(k in self._active_keys for k in keys):
                # Вызываем callback в главном потоке
                self.root.after(0, callback)
                # Сбрасываем чтобы не срабатывало многократно
                self._active_keys.clear()
                break

    def unregister_hotkey(self, key_combo: str):
        """Удалить регистрацию горячей клавиши."""
        key_combo = key_combo.lower()
        if key_combo in self.hotkeys:
            del self.hotkeys[key_combo]

    def unregister_all(self):
        """Удалить все зарегистрированные хоткеи."""
        self.hotkeys.clear()
        if self.listener:
            self.listener.stop()
            self.listener = None
        self._active_keys.clear()

    def is_available(self) -> bool:
        """Проверить доступность функционала."""
        return PYNPUT_AVAILABLE

    def get_registered_hotkeys(self) -> list:
        """Вернуть список зарегистрированных комбинаций."""
        return list(self.hotkeys.keys())
