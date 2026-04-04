import os
from config import CSV_FILE_PATH

class CSVService:
    def __init__(self, file_path=None):
        self.file_path = file_path or CSV_FILE_PATH

    def search(self, query: str, limit: int = 10) -> list:
        """Поиск строк в CSV файле"""
        found_data = []
        
        if not os.path.exists(self.file_path):
            return [f" Ошибка: Файл не найден по пути:\n{self.file_path}"]
            
        try:
            encodings = ['utf-8', 'cp1251', 'latin-1']
            content = None
            
            for enc in encodings:
                try:
                    with open(self.file_path, 'r', encoding=enc, newline='') as f:
                        content = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue
                    
            if content is None:
                return [" Ошибка: Не удалось прочитать файл (неподходящая кодировка)"]
                
            for line in content:
                if query.lower() in line.lower():
                    found_data.append(line.strip())
                    if len(found_data) >= limit:
                        break
                        
            if not found_data:
                return [" В локальном реестре совпадений не найдено."]
                
            return found_data
            
        except Exception as e:
            return [f" Ошибка чтения CSV: {str(e)}"]