"""
Storage CSV — операции с CSV файлами.

Отвечает за:
- Чтение CSV файлов
- Запись CSV файлов
- Поддержку различных кодировок
"""

import os
import csv
import logging
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger("StorageService")


def read_csv_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    ensure_path_func: Callable[[str], str]
) -> Optional[List[Dict[str, str]]]:
    """
    Чтение CSV файла из хранилища.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        filename: Имя файла (с расширением .csv)
        ensure_path_func: Функция создания пути
        
    Returns:
        Список словарей (строки CSV) или None если ошибка
    """
    try:
        path = os.path.join(ensure_path_func(subfolder), filename)
        if not os.path.exists(path):
            logger.warning(f"CSV файл не найден: {path}")
            return None
        
        with open(path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            logger.debug(f"Прочитан CSV: {path} ({len(data)} строк)")
            return data
    except Exception as e:
        logger.error(f"Ошибка чтения CSV {filename}: {str(e)}")
        return None


def write_csv_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    data: List[Dict[str, str]],
    fieldnames: Optional[List[str]] = None,
    ensure_path_func: Callable[[str], str] = None
) -> bool:
    """
    Запись CSV файла в хранилище.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        filename: Имя файла (с расширением .csv)
        data: Список словарей (строки)
        fieldnames: Имена колонок
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно, False иначе
    """
    try:
        if not data:
            logger.warning("Пустые данные для записи CSV")
            return False
        
        path = os.path.join(ensure_path_func(subfolder), filename)
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        logger.debug(f"Записан CSV: {path} ({len(data)} строк)")
        return True
    except Exception as e:
        logger.error(f"Ошибка записи CSV {filename}: {str(e)}")
        return False


def append_csv_impl(
    root_path: str,
    subfolder: str,
    filename: str,
    data: List[Dict[str, str]],
    ensure_path_func: Callable[[str], str]
) -> bool:
    """
    Добавление строк в существующий CSV файл.
    
    Args:
        root_path: Корневой путь хранилища
        subfolder: Подпапка
        filename: Имя файла
        data: Данные для добавления
        ensure_path_func: Функция создания пути
        
    Returns:
        True если успешно
    """
    try:
        path = os.path.join(ensure_path_func(subfolder), filename)
        if not os.path.exists(path):
            return write_csv_impl(root_path, subfolder, filename, data, 
                                  ensure_path_func=ensure_path_func)
        
        fieldnames = list(data[0].keys()) if data else []
        with open(path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(data)
        
        logger.debug(f"Добавлено {len(data)} строк в CSV: {path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления в CSV {filename}: {str(e)}")
        return False


def read_csv_with_encoding(
    filepath: str,
    encodings: list = None
) -> Optional[List[str]]:
    """
    Чтение CSV с авто-определением кодировки.
    
    Args:
        filepath: Путь к файлу
        encodings: Список кодировок для проверки
        
    Returns:
        Список строк или None
    """
    if encodings is None:
        encodings = ['utf-8', 'cp1251', 'latin-1']
    
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc, newline='') as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
    
    return None