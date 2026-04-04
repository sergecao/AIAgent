import os
import webbrowser
import subprocess
import re
from urllib.parse import urlparse

class LinkOpener:
    """Класс для открытия ссылок, файлов и папок"""
    
    @staticmethod
    def extract_links(text: str) -> list:
        """Извлечение ссылок из текста"""
        links = []
        
        # Разбиваем текст на строки
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Убираем кавычки в начале и конце
            line = line.strip('"\'')
            
            # Проверяем различные типы путей и ссылок
            if LinkOpener._is_valid_link(line):
                links.append(line)
                
        return links
    
    @staticmethod
    def _is_valid_link(link: str) -> bool:
        """Проверка является ли строка допустимой ссылкой"""
        if not link:
            return False
            
        # Проверяем URL
        if link.startswith(('http://', 'https://', 'www.')):
            return True
            
        # Проверяем локальные пути
        if os.path.exists(link) or os.path.exists(link.strip('"')):
            return True
            
        # Проверяем сетевые пути
        if link.startswith('\\\\') or link.startswith('//'):
            return True
            
        return False
    
    @staticmethod
    def open_link(link: str) -> tuple:
        """Открытие одной ссылки/файла/папки"""
        try:
            # Очищаем от кавычек
            clean_link = link.strip('"\'')
            
            # Проверяем URL
            if clean_link.startswith(('http://', 'https://')) or \
               (clean_link.startswith('www.') and '.' in clean_link):
                webbrowser.open(clean_link)
                return True, f"Открыт URL: {clean_link}"
            
            # Проверяем www ссылки
            if clean_link.startswith('www.') and '.' in clean_link:
                webbrowser.open(f"https://{clean_link}")
                return True, f"Открыт URL: https://{clean_link}"
            
            # Проверяем локальные файлы и папки
            if os.path.exists(clean_link):
                if os.path.isfile(clean_link):
                    # Открываем файл
                    if os.name == 'nt':  # Windows
                        os.startfile(clean_link)
                    else:
                        subprocess.call(['xdg-open', clean_link])
                    return True, f"Открыт файл: {clean_link}"
                elif os.path.isdir(clean_link):
                    # Открываем папку
                    if os.name == 'nt':  # Windows
                        os.startfile(clean_link)
                    else:
                        subprocess.call(['xdg-open', clean_link])
                    return True, f"Открыта папка: {clean_link}"
            
            # Проверяем сетевые пути
            if clean_link.startswith('\\\\') or clean_link.startswith('//'):
                if os.name == 'nt':  # Только для Windows
                    os.startfile(clean_link)
                    return True, f"Открыт сетевой путь: {clean_link}"
            
            return False, f"Не удалось открыть: {link}"
            
        except Exception as e:
            return False, f"Ошибка при открытии {link}: {str(e)}"
    
    @staticmethod
    def open_all_links(links: list) -> list:
        """Открытие всех ссылок из списка"""
        results = []
        
        if not links:
            results.append(("warning", "Нет ссылок для открытия"))
            return results
            
        for link in links:
            success, message = LinkOpener.open_link(link)
            status = "success" if success else "error"
            results.append((status, message))
            
        return results