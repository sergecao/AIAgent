# core/session_manager.py
from core.token_optimizer import TokenOptimizer
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
        self.token_optimizer = TokenOptimizer()  # ← ДОБАВЛЕНО
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
        # Добавляем в индекс
        index = self._load_index()
        index.append({"id": session_id, "title": title, "start": self.current_session["start_time"]})
        self._save_index(index)
        logger.info(f"Сессия начата: {session_id}")
        return self.current_session

    def end_session(self):
        """Завершает текущую сессию."""
        if not self.current_session:
            return
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["status"] = "closed"
        self._save_session_file()
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
        index = self._load_index()
        return sorted(index, key=lambda x: x.get("start", ""), reverse=True)[:limit]

    def restore_last_session(self) -> Optional[Dict]:
        """Пытается восстановить последнюю активную сессию."""
        # Упрощенная логика: ищем файл последней сессии
        files = self.storage.list_files(self.subfolder, ".json")
        if not files:
            return None
        # Берем последний по имени (так как там дата)
        files.sort(reverse=True)
        last_file = files[0]
        if last_file == "index.json":
            return None
        data = self.storage.read_json(self.subfolder, last_file)
        if data and data.get("status") == "active":
            self.current_session = data
            logger.info(f"Сессия восстановлена: {last_file}")
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