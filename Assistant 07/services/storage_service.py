"""
Storage Service — основной сервис для работы с хранилищем D:\psa\

Модульная архитектура:
- storage_json.py — JSON операции
- storage_csv.py — CSV операции
- storage_backup.py — Резервное копирование и информация
"""

import os
import logging
from typing import Any, Dict, List, Optional
from config import PSA_ROOT

# Глобальный логгер
logger = None


class StorageService:
    """Сервис для работы с хранилищем D:\psa\\"""
    
    def __init__(self, root_path: str = PSA_ROOT):
        """
        Инициализация сервиса.
        
        Args:
            root_path: Корневой путь хранилища
        """
        global logger
        
        self.root_path = root_path
        
        # Инициализация логирования
        if logger is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(os.path.join(log_dir, "storage.log"), encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            logger = logging.getLogger("StorageService")
        
        logger.info(f"StorageService инициализирован: {self.root_path}")
    
    def _ensure_path(self, subfolder: str) -> str:
        """Проверка и создание пути подпапки."""
        path = os.path.join(self.root_path, subfolder)
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.debug(f"Создана папка: {path}")
        except Exception as e:
            logger.error(f"Ошибка создания папки {path}: {str(e)}")
            fallback_path = os.path.join(os.getcwd(), "psa_fallback", subfolder)
            os.makedirs(fallback_path, exist_ok=True)
            logger.warning(f"Используем fallback: {fallback_path}")
            return fallback_path
        return path
    
    # === JSON ОПЕРАЦИИ (делегирование) ===
    def read_json(self, subfolder: str, filename: str) -> Optional[Dict[str, Any]]:
        from services.storage_json import read_json_impl
        return read_json_impl(self.root_path, subfolder, filename, self._ensure_path)
    
    def write_json(self, subfolder: str, filename: str, data: Dict[str, Any]) -> bool:
        from services.storage_json import write_json_impl
        return write_json_impl(self.root_path, subfolder, filename, data, self._ensure_path)
    
    # === CSV ОПЕРАЦИИ (делегирование) ===
    def read_csv(self, subfolder: str, filename: str) -> Optional[List[Dict[str, str]]]:
        from services.storage_csv import read_csv_impl
        return read_csv_impl(self.root_path, subfolder, filename, self._ensure_path)
    
    def write_csv(self, subfolder: str, filename: str, data: List[Dict[str, str]], 
                  fieldnames: Optional[List[str]] = None) -> bool:
        from services.storage_csv import write_csv_impl
        return write_csv_impl(self.root_path, subfolder, filename, data, fieldnames, self._ensure_path)
    
    # === ФАЙЛОВЫЕ ОПЕРАЦИИ (делегирование) ===
    def file_exists(self, subfolder: str, filename: str) -> bool:
        from services.storage_backup import file_exists_impl
        return file_exists_impl(self.root_path, subfolder, filename, self._ensure_path)
    
    def delete_file(self, subfolder: str, filename: str) -> bool:
        from services.storage_backup import delete_file_impl
        return delete_file_impl(self.root_path, subfolder, filename, self._ensure_path)
    
    def list_files(self, subfolder: str, extension: str = ".json") -> List[str]:
        from services.storage_backup import list_files_impl
        return list_files_impl(self.root_path, subfolder, extension, self._ensure_path)
    
    # === РЕЗЕРВНОЕ КОПИРОВАНИЕ И ИНФО (делегирование) ===
    def backup_folder(self, subfolder: str, backup_path: str) -> bool:
        from services.storage_backup import backup_folder_impl
        return backup_folder_impl(self.root_path, subfolder, backup_path, self._ensure_path)
    
    def get_storage_info(self) -> Dict[str, Any]:
        from services.storage_backup import get_storage_info_impl
        return get_storage_info_impl(self.root_path)