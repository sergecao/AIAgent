"""
Storage Backup — резервное копирование и файловые операции.

Отвечает за:
- Проверку существования файлов
- Удаление файлов
- Список файлов в папке
- Резервное копирование
- Информацию о хранилище
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Any, Dict, List, Callable

logger = logging.getLogger("StorageService")


def file_exists_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Проверка существования файла.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        filename: Имя файла
        ensure_path_func: Функция создания пути
        
    Returns:
        True если файл существует
    """
    path = os.path.join(ensure_path_func(subfolder), filename)
    exists = os.path.exists(path)
    logger.debug(f"Проверка файла {filename}: {'существует' if exists else 'не найден'}")
    return exists


def delete_file_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Удаление файла из хранилища.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        filename: Имя файла
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно, False иначе
    """
    try:
        path = os.path.join(ensure_path_func(subfolder), filename)
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Удалён файл: {path}")
            return True
        else:
            logger.warning(f"Файл не найден для удаления: {path}")
            return False
    except Exception as e:
        logger.error(f"Ошибка удаления {filename}: {str(e)}")
        return False


def list_files_impl(
    root_path: str,
    subfolder: str,
    extension: str = ".json",
    ensure_path_func: Callable[[str], str] = None
) -> List[str]:
    """
    Список файлов в подпапке по расширению.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        extension: Расширение файлов
        ensure_path_func: Функция создания пути
        
    Returns:
        Список имён файлов
    """
    try:
        path = ensure_path_func(subfolder) if ensure_path_func else os.path.join(root_path, subfolder)
        files = [f for f in os.listdir(path) if f.endswith(extension)]
        logger.debug(f"Найдено {len(files)} файлов с расширением {extension} в {subfolder}")
        return files
    except Exception as e:
        logger.error(f"Ошибка списка файлов в {subfolder}: {str(e)}")
        return []


def backup_folder_impl(
    root_path: str,
    subfolder: str,
    backup_path: str,
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Резервное копирование подпапки.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка для копирования
        backup_path: Путь назначения для резервной копии
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно, False иначе
    """
    try:
        source = ensure_path_func(subfolder)
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(source, backup_path)
        logger.info(f"Резервная копия создана: {subfolder} → {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка резервного копирования {subfolder}: {str(e)}")
        return False


def get_storage_info_impl(root_path: str) -> Dict[str, Any]:
    """
    Получение информации о хранилище.
    
    Args:
        root_path: Корневой путь хранилища
        
    Returns:
        Словарь с информацией (размер, количество файлов, и т.д.)
    """
    try:
        total_size = 0
        total_files = 0
        
        if not os.path.exists(root_path):
            return {"error": "Хранилище не существует", "root_path": root_path}
        
        for folder in os.listdir(root_path):
            folder_path = os.path.join(root_path, folder)
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    total_files += len(files)
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            total_size += os.path.getsize(fp)
                        except OSError:
                            pass
        
        info = {
            "root_path": root_path,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": total_files,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"Информация о хранилище: {info}")
        return info
    except Exception as e:
        logger.error(f"Ошибка получения информации о хранилище: {str(e)}")
        return {"error": str(e)}


def cleanup_old_files(
    root_path: str,
    subfolder: str,
    max_age_days: int = 30,
    extension: str = ".json"
) -> int:
    """
    Очистка старых файлов из подпапки.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        max_age_days: Максимальный возраст файлов в днях
        extension: Расширение файлов для очистки
        
    Returns:
        Количество удалённых файлов
    """
    try:
        import time
        path = os.path.join(root_path, subfolder)
        if not os.path.exists(path):
            return 0
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(path):
            if not filename.endswith(extension):
                continue
            filepath = os.path.join(path, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                deleted_count += 1
                logger.info(f"Удалён старый файл: {filename}")
        
        logger.info(f"Очистка завершена: удалено {deleted_count} файлов")
        return deleted_count
    except Exception as e:
        logger.error(f"Ошибка очистки старых файлов: {str(e)}")
        return 0