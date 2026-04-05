"""
Tray Icon - Иконка в системном трее.
Позволяет сворачивать приложение в угол экрана.
"""
import tkinter as tk
from typing import Callable, Optional

try:
    import pystray
    from pystray import Icon as icon
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class TrayIconManager:
    """Управление иконкой в системном трее."""

    def __init__(self, root: tk.Tk, on_show: Optional[Callable] = None):
        self.root = root
        self.on_show = on_show
        self.icon = None
        self.is_in_tray = False
        
        # Создаем изображение для иконки (заглушка)
        self.image = self._create_icon_image()

    def _create_icon_image(self):
        """Создать простое изображение иконки."""
        img = Image.new('RGB', (64, 64), color=(70, 130, 180))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 54, 54], outline='white', width=4)
        draw.text((20, 25), "AI", fill='white')
        return img

    def show_in_tray(self):
        """Показать иконку в трее и скрыть окно."""
        if not PYSTRAY_AVAILABLE:
            return False
        
        if self.is_in_tray:
            return True
            
        menu = (
            item("Показать", self._on_show, default=True),
            item("Выход", self._on_exit)
        )
        
        self.icon = icon(self.image, "AI Assistant", menu)
        
        # Скрываем окно Tkinter
        self.root.withdraw()
        self.is_in_tray = True
        
        # Запускаем трей в отдельном потоке
        import threading
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()
        return True

    def _on_show(self, icon=None, item=None):
        """Обработчик показа окна из трея."""
        if self.icon:
            self.icon.stop()
            self.icon = None
        
        self.root.deiconify()
        self.is_in_tray = False
        
        if self.on_show:
            self.on_show()

    def _on_exit(self, icon=None, item=None):
        """Обработчик выхода из приложения."""
        if self.icon:
            self.icon.stop()
        self.root.quit()
        self.root.destroy()

    def hide_to_tray(self):
        """Алиас для show_in_tray."""
        return self.show_in_tray()

    def is_available(self) -> bool:
        """Проверить доступность функционала трея."""
        return PYSTRAY_AVAILABLE
