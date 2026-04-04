"""
Storage JSON — операции с JSON файлами.

Отвечает за:
- Чтение JSON файлов
- Запись JSON файлов
- Обработку ошибок парсинга
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Callable

logger = logging.getLogger("StorageService")


def read_json_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    ensure_path_func: Callable[[str], str]
) -> Optional[Dict[str, Any]]:
    """
    Чтение JSON файла из хранилища.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка (sessions, tasks, и т.д.)
        filename: Имя файла (с расширением .json)
        ensure_path_func: Функция создания пути
        
    Returns:
        Словарь с данными или None если файл не найден
    """
    try:
        path = os.path.join(ensure_path_func(subfolder), filename)
        if not os.path.exists(path):
            logger.warning(f"Файл не найден: {path}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Прочитан файл: {path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON {filename}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Ошибка чтения {filename}: {str(e)}")
        return None


def write_json_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    data: Dict[str, Any],
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Запись JSON файла в хранилище.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка (sessions, tasks, и т.д.)
        filename: Имя файла (с расширением .json)
        data: Данные для записи
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно, False иначе
    """
    try:
        path = os.path.join(ensure_path_func(subfolder), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Записан файл: {path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка записи {filename}: {str(e)}")
        return False


def validate_json(data: Any) -> bool:
    """
    Валидация JSON данных.
    
    Args:
        data: Данные для проверки
        
    Returns:
        True если данные валидны
    """
    if data is None:
        return False
    try:
        json.dumps(data, ensure_ascii=False)
        return True
    except (TypeError, ValueError):
        return False


def merge_json_files(
    root_path: str,
    subfolder: str,
    target_file: str,
    source_files: list,
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Объединение нескольких JSON файлов в один.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        target_file: Целевой файл
        source_files: Список исходных файлов
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно
    """
    try:
        merged_data = []
        for src_file in source_files:
            path = os.path.join(ensure_path_func(subfolder), src_file)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        merged_data.extend(data)
                    else:
                        merged_data.append(data)
        
        target_path = os.path.join(ensure_path_func(subfolder), target_file)
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Объединено {len(source_files)} файлов в {target_file}")
        return True
    except Exception as e:
        logger.error(f"Ошибка объединения JSON: {str(e)}")
        return False