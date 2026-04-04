# core/task_engine.py
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from services.storage_service import StorageService
from config import PSA_ROOT

logger = logging.getLogger("TaskEngine")

class TaskEngine:
    """Движок управления задачами (Хранение: tasks/index.json)."""
    
    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or StorageService()
        self.index_file = "index.json"
        self.subfolder = "tasks"
        self._ensure_index()

    def _ensure_index(self):
        """Создает индекс задач, если нет."""
        if not self.storage.file_exists(self.subfolder, self.index_file):
            self.storage.write_json(self.subfolder, self.index_file, {"tasks": []})

    def _load_tasks(self) -> List[Dict]:
        """Загружает список задач."""
        data = self.storage.read_json(self.subfolder, self.index_file)
        return data.get("tasks", []) if data else []

    def _save_tasks(self, tasks: List[Dict]):
        """Сохраняет список задач."""
        self.storage.write_json(self.subfolder, self.index_file, {"tasks": tasks})

    def create_task(self, title: str, description: str = "", status: str = "new") -> Dict:
        """Создает новую задачу."""
        tasks = self._load_tasks()
        new_id = max([t.get("id", 0) for t in tasks], default=0) + 1
        task = {
            "id": new_id,
            "title": title,
            "description": description,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        tasks.append(task)
        self._save_tasks(tasks)
        logger.info(f"Задача создана: {title}")
        return task

    def get_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """Получает задачи (фильтр по статусу)."""
        tasks = self._load_tasks()
        if status:
            return [t for t in tasks if t.get("status") == status]
        return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Находит задачу по ID."""
        tasks = self._load_tasks()
        for t in tasks:
            if t.get("id") == task_id:
                return t
        return None

    def update_status(self, task_id: int, status: str) -> bool:
        """Обновляет статус задачи."""
        tasks = self._load_tasks()
        for t in tasks:
            if t.get("id") == task_id:
                t["status"] = status
                t["updated_at"] = datetime.now().isoformat()
                self._save_tasks(tasks)
                logger.info(f"Задача {task_id} -> {status}")
                return True
        return False

    def archive_completed(self) -> int:
        """Архивирует все завершенные задачи (status=done -> archived)."""
        tasks = self._load_tasks()
        count = 0
        for t in tasks:
            if t.get("status") == "done":
                t["status"] = "archived"
                count += 1
        if count > 0:
            self._save_tasks(tasks)
            logger.info(f"Архивировано задач: {count}")
        return count

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID."""
        tasks = self._load_tasks()
        original_len = len(tasks)
        tasks = [t for t in tasks if t.get("id") != task_id]
        if len(tasks) < original_len:
            self._save_tasks(tasks)
            logger.info(f"Задача удалена: {task_id}")
            return True
        return False