# core/session_manager.py
from core.token_optimizer import TokenOptimizer
from data.session_index import SessionIndex
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Any
from services.storage_service import StorageService
from config import SESSION_CONFIG, PSA_ROOT


logger = logging.getLogger("SessionManager")

class SessionManager:
    """Управление сессиями пользователя (Контекст + Авто-сохранение)."""
    
    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or StorageService()
        self.subfolder = "sessions"
        self.index_file = "index.json"
        self.current_session: Optional[Dict] = None
        self.auto_save_thread: Optional[threading.Thread] = None
        self._stop_flag = False
        self.token_optimizer = TokenOptimizer()
        self.session_index = SessionIndex(self.storage)  # ← Индекс сессий
        self._ensure_index()
        if SESSION_CONFIG.get("auto_save_enabled"):
            self._start_auto_save()

    def _ensure_index(self):
        if not self.storage.file_exists(self.subfolder, self.index_file):
            self.storage.write_json(self.subfolder, self.index_file, {"sessions": []})

    def _load_index(self) -> list:
        data = self.storage.read_json(self.subfolder, self.index_file)
        return data.get("sessions", []) if data else []

    def _save_index(self, sessions: list):
        self.storage.write_json(self.subfolder, self.index_file, {"sessions": sessions})

    def start_session(self, title: str, tags: list = None) -> Dict:
        """Начинает новую сессию."""
        if self.current_session:
            self.end_session()
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = {
            "id": session_id,
            "title": title,
            "tags": tags or [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "context": {},
            "status": "active"
        }
        # Добавляем в индекс через SessionIndex
        self.session_index.add_session(session_id, title, self.current_session["start_time"], tags)
        logger.info(f"Сессия начата: {session_id}")
        return self.current_session

    def end_session(self):
        """Завершает текущую сессию."""
        if not self.current_session:
            return
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["status"] = "closed"
        self._save_session_file()
        # Обновляем статус в индексе
        self.session_index.update_session(
            self.current_session["id"],
            self.current_session["end_time"],
            "closed"
        )
        self.current_session = None
        logger.info("Сессия завершена")

    def update_context(self, key: str, value: Any):
        """Обновляет контекст текущей сессии."""
        if self.current_session:
            self.current_session["context"][key] = value
            # Триггер ручного сохранения контекста
            if SESSION_CONFIG.get("auto_save_enabled"):
                self._save_session_file()

    def get_context(self, key: str = None) -> Any:
        """Получает данные из контекста."""
        if not self.current_session:
            return None
        if key:
            return self.current_session["context"].get(key)
        return self.current_session["context"]

    def _save_session_file(self):
        """Сохраняет полную сессию в отдельный файл."""
        if not self.current_session:
            return
        filename = f"{self.current_session['id']}.json"
        self.storage.write_json(self.subfolder, filename, self.current_session)

    def _start_auto_save(self):
        """Запускает поток авто-сохранения."""
        self._stop_flag = False
        self.auto_save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.auto_save_thread.start()

    def _auto_save_loop(self):
        """Цикл авто-сохранения (каждые N минут)."""
        interval = SESSION_CONFIG.get("auto_save_interval_minutes", 5) * 60
        while not self._stop_flag:
            time.sleep(interval)
            if self.current_session:
                logger.debug("Авто-сохранение сессии...")
                self._save_session_file()

    def stop_auto_save(self):
        """Останавливает поток авто-сохранения."""
        self._stop_flag = True
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=2)

    def get_history(self, limit: int = 10) -> list:
        """Получает историю сессий."""
        return self.session_index.get_archive(limit)

    def restore_last_session(self) -> Optional[Dict]:
        """Пытается восстановить последнюю активную сессию."""
        active = self.session_index.get_active_sessions()
        if not active:
            return None
        # Берем последнюю активную
        last = active[-1]
        session_id = last["id"]
        filename = f"{session_id}.json"
        if self.storage.file_exists(self.subfolder, filename):
            data = self.storage.read_json(self.subfolder, filename)
            if data and data.get("status") == "active":
                self.current_session = data
                logger.info(f"Сессия восстановлена: {filename}")
                return data
        return None

    def get_optimized_context(self) -> str:
        """Получает оптимизированный контекст для промпта ИИ."""
        if not self.current_session:
            return "Нет активной сессии"
        return self.token_optimizer.summarize_for_prompt(self.current_session)

    def get_token_stats(self) -> Dict:
        """Возвращает статистику оптимизации токенов."""
        return self.token_optimizer.get_stats()

    def search_sessions_by_tag(self, tag: str) -> list:
        """Ищет сессии по тегу."""
        return self.session_index.search_by_tag(tag)

    def search_sessions_by_title(self, keyword: str) -> list:
        """Ищет сессии по заголовку."""
        return self.session_index.search_by_title(keyword)

    def get_session_stats(self) -> Dict:
        """Возвращает статистику по сессиям."""
        return self.session_index.get_stats()

    def add_tag_to_current(self, tag: str):
        """Добавляет тег к текущей сессии."""
        if self.current_session:
            if tag not in self.current_session["tags"]:
                self.current_session["tags"].append(tag)
                self._save_session_file()
                logger.info(f"Тег '{tag}' добавлен к сессии")

    def remove_tag_from_current(self, tag: str):
        """Удаляет тег из текущей сессии."""
        if self.current_session:
            if tag in self.current_session["tags"]:
                self.current_session["tags"].remove(tag)
                self._save_session_file()
                logger.info(f"Тег '{tag}' удалён из сессии")