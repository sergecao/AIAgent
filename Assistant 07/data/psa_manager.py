"""
PSA Manager — менеджер структуры хранилища D:\psa\

Отвечает за:
- Проверку существования хранилища при старте
- Авто-создание структуры папок
- Валидацию структуры
- Инициализацию файлов конфигурации по умолчанию

Вызывается один раз при запуске приложения.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List
import logging

from config import PSA_ROOT, PSA_SUBFOLDERS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PSAManager")


class PSAManager:
    """Менеджер структуры хранилища D:\psa\\"""
    
    def __init__(self, root_path: str = PSA_ROOT, subfolders: List[str] = PSA_SUBFOLDERS):
        """
        Инициализация менеджера.
        
        Args:
            root_path: Корневой путь хранилища
            subfolders: Список подпапок для создания
        """
        self.root_path = root_path
        self.subfolders = subfolders
        logger.info(f"PSAManager инициализирован: {self.root_path}")
    
    def ensure_structure(self) -> bool:
        """
        Проверка и создание структуры хранилища.
        
        Returns:
            True если структура создана/существует, False при ошибке
        """
        try:
            # Создаём корневую папку если нет
            if not os.path.exists(self.root_path):
                os.makedirs(self.root_path)
                logger.info(f"Создано хранилище: {self.root_path}")
            else:
                logger.debug(f"Хранилище существует: {self.root_path}")
            
            # Создаём подпапки
            for folder in self.subfolders:
                folder_path = os.path.join(self.root_path, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    logger.debug(f"Создана подпапка: {folder_path}")
            
            # Инициализируем файлы конфигурации по умолчанию
            self._init_default_configs()
            
            logger.info("Структура хранилища проверена и готова")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания структуры хранилища: {str(e)}")
            return False
    
    def _init_default_configs(self) -> None:
        """Инициализация файлов конфигурации по умолчанию."""
        
        # config.json в корне хранилища
        config_path = os.path.join(self.root_path, "config.json")
        if not os.path.exists(config_path):
            default_config = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "user_id": "default",
                "settings": {
                    "auto_save_enabled": True,
                    "auto_save_interval_minutes": 5,
                    "language": "ru"
                }
            }
            # Используем простой json.dump без StorageService
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logger.debug("Создан config.json по умолчанию")
        
        # index.json для сессий
        sessions_index_path = os.path.join(self.root_path, "sessions", "index.json")
        if not os.path.exists(sessions_index_path):
            with open(sessions_index_path, 'w', encoding='utf-8') as f:
                json.dump({"sessions": []}, f, ensure_ascii=False, indent=2)
            logger.debug("Создан sessions/index.json по умолчанию")
        
        # index.json для задач
        tasks_index_path = os.path.join(self.root_path, "tasks", "index.json")
        if not os.path.exists(tasks_index_path):
            with open(tasks_index_path, 'w', encoding='utf-8') as f:
                json.dump({"tasks": []}, f, ensure_ascii=False, indent=2)
            logger.debug("Создан tasks/index.json по умолчанию")
    
    def validate_structure(self) -> Dict[str, Any]:
        """
        Валидация структуры хранилища.
        
        Returns:
            Словарь с результатами валидации
        """
        result = {
            "valid": True,
            "root_exists": os.path.exists(self.root_path),
            "missing_folders": [],
            "errors": []
        }
        
        if not result["root_exists"]:
            result["valid"] = False
            result["errors"].append(f"Корневая папка не существует: {self.root_path}")
            return result
        
        for folder in self.subfolders:
            folder_path = os.path.join(self.root_path, folder)
            if not os.path.exists(folder_path):
                result["missing_folders"].append(folder)
                result["valid"] = False
        
        if result["valid"]:
            logger.info("Валидация хранилища: успешно")
        else:
            logger.warning(f"Валидация хранилища: найдено проблем - {len(result['missing_folders'])}")
        
        return result
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Получение расширенной информации о хранилище.
        
        Returns:
            Словарь с информацией о хранилище
        """
        validation = self.validate_structure()
        
        total_size = 0
        total_files = 0
        
        if os.path.exists(self.root_path):
            for folder in os.listdir(self.root_path):
                folder_path = os.path.join(self.root_path, folder)
                if os.path.isdir(folder_path):
                    for root, dirs, files in os.walk(folder_path):
                        total_files += len(files)
                        for f in files:
                            fp = os.path.join(root, f)
                            try:
                                total_size += os.path.getsize(fp)
                            except OSError:
                                pass
        
        return {
            "root_path": self.root_path,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": total_files,
            "validation": validation,
            "subfolders": self.subfolders
        }
    
    def reset_storage(self, confirm: bool = False) -> bool:
        """
        Сброс хранилища (удаление всех данных).
        
        WARNING: Удаляет все данные в D:\psa\!
        
        Args:
            confirm: Должно быть True для подтверждения
            
        Returns:
            True если успешно, False иначе
        """
        if not confirm:
            logger.warning("Сброс хранилища отменён: нет подтверждения")
            return False
        
        try:
            if os.path.exists(self.root_path):
                # Сохраняем config.json перед удалением
                config_path = os.path.join(self.root_path, "config.json")
                config_data = None
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                
                # Удаляем всё кроме корневой папки
                for item in os.listdir(self.root_path):
                    item_path = os.path.join(self.root_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                
                # Пересоздаём структуру
                self.ensure_structure()
                
                # Восстанавливаем config если был
                if config_data:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                logger.info("Хранилище сброшено")
                return True
            else:
                logger.warning("Хранилище не существует для сброса")
                return False
        except Exception as e:
            logger.error(f"Ошибка сброса хранилища: {str(e)}")
            return False