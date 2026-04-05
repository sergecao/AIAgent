# data/session_index.py
"""Индекс сессий для поиска и архивирования."""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from services.storage_service import StorageService
from config import PSA_ROOT

logger = logging.getLogger("SessionIndex")


class SessionIndex:
    """Управление индексом сессий с поиском по тегам и фильтрами."""

    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or StorageService()
        self.subfolder = "sessions"
        self.index_file = "index.json"
        self._ensure_index()

    def _ensure_index(self):
        """Создаёт индексный файл если не существует."""
        if not self.storage.file_exists(self.subfolder, self.index_file):
            self.storage.write_json(self.subfolder, self.index_file, {"sessions": []})

    def _load_index(self) -> List[Dict]:
        """Загружает индекс из файла."""
        data = self.storage.read_json(self.subfolder, self.index_file)
        return data.get("sessions", []) if data else []

    def _save_index(self, sessions: List[Dict]):
        """Сохраняет индекс в файл."""
        self.storage.write_json(self.subfolder, self.index_file, {"sessions": sessions})

    def add_session(self, session_id: str, title: str, start_time: str, tags: List[str] = None):
        """Добавляет запись о сессии в индекс."""
        index = self._load_index()
        entry = {
            "id": session_id,
            "title": title,
            "start": start_time,
            "tags": tags or [],
            "end": None,
            "status": "active"
        }
        index.append(entry)
        self._save_index(index)
        logger.info(f"Сессия {session_id} добавлена в индекс")

    def update_session(self, session_id: str, end_time: str = None, status: str = None):
        """Обновляет статус сессии в индексе."""
        index = self._load_index()
        for entry in index:
            if entry["id"] == session_id:
                if end_time:
                    entry["end"] = end_time
                if status:
                    entry["status"] = status
                break
        self._save_index(index)
        logger.info(f"Сессия {session_id} обновлена в индексе")

    def search_by_tag(self, tag: str) -> List[Dict]:
        """Ищет сессии по тегу."""
        index = self._load_index()
        results = [s for s in index if tag in s.get("tags", [])]
        logger.info(f"Найдено {len(results)} сессий по тегу '{tag}'")
        return results

    def search_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Ищет сессии в диапазоне дат (формат ISO)."""
        index = self._load_index()
        results = [
            s for s in index
            if start_date <= s.get("start", "")[:10] <= end_date
        ]
        logger.info(f"Найдено {len(results)} сессий за период {start_date} - {end_date}")
        return results

    def search_by_title(self, keyword: str) -> List[Dict]:
        """Ищет сессии по ключевому слову в заголовке."""
        index = self._load_index()
        keyword_lower = keyword.lower()
        results = [s for s in index if keyword_lower in s.get("title", "").lower()]
        logger.info(f"Найдено {len(results)} сессий по запросу '{keyword}'")
        return results

    def get_archive(self, limit: int = 100) -> List[Dict]:
        """Получает архив закрытых сессий."""
        index = self._load_index()
        archived = [s for s in index if s.get("status") == "closed"]
        archived.sort(key=lambda x: x.get("end", ""), reverse=True)
        return archived[:limit]

    def get_active_sessions(self) -> List[Dict]:
        """Получает список активных сессий."""
        index = self._load_index()
        return [s for s in index if s.get("status") == "active"]

    def delete_session(self, session_id: str) -> bool:
        """Удаляет сессию из индекса."""
        index = self._load_index()
        original_len = len(index)
        index = [s for s in index if s["id"] != session_id]
        if len(index) < original_len:
            self._save_index(index)
            logger.info(f"Сессия {session_id} удалена из индекса")
            return True
        logger.warning(f"Сессия {session_id} не найдена для удаления")
        return False

    def get_stats(self) -> Dict:
        """Возвращает статистику по сессиям."""
        index = self._load_index()
        total = len(index)
        active = len([s for s in index if s.get("status") == "active"])
        closed = len([s for s in index if s.get("status") == "closed"])
        return {
            "total_sessions": total,
            "active_sessions": active,
            "closed_sessions": closed,
            "last_updated": datetime.now().isoformat()
        }