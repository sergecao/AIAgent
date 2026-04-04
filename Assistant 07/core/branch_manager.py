# core/branch_manager.py
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import PSA_ROOT
from services.storage_service import StorageService

logger = logging.getLogger("BranchManager")

class BranchManager:
    """Менеджер веток контекста (разные роли/проекты/задачи)."""
    
    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or StorageService()
        self.subfolder = "branches"
        self.index_file = "index.json"
        self.current_branch: Optional[str] = None
        self._ensure_index()
        self._load_current()

    def _ensure_index(self):
        """Создаёт индекс веток если нет."""
        if not self.storage.file_exists(self.subfolder, self.index_file):
            self.storage.write_json(self.subfolder, self.index_file, {
                "branches": [],
                "current": None
            })

    def _load_index(self) -> Dict:
        """Загружает индекс веток."""
        data = self.storage.read_json(self.subfolder, self.index_file)
        return data if data else {"branches": [], "current": None}

    def _save_index(self, data: Dict):
        """Сохраняет индекс веток."""
        self.storage.write_json(self.subfolder, self.index_file, data)

    def _load_current(self):
        """Загружает текущую ветку из индекса."""
        index = self._load_index()
        self.current_branch = index.get("current")

    def create_branch(self, name: str, description: str = "", role: str = "default") -> Dict:
        """Создаёт новую ветку контекста."""
        index = self._load_index()
        branch_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.lower().replace(' ', '_')}"
        branch = {
            "id": branch_id,
            "name": name,
            "description": description,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "context_items": 0,
            "path": f"{self.subfolder}/{branch_id}"
        }
        index["branches"].append(branch)
        self._save_index(index)
        # Создаём папку ветки
        self.storage.write_json(branch["path"], "meta.json", branch)
        self.storage.write_json(branch["path"], "context.json", {"items": []})
        logger.info(f"Ветка создана: {name}")
        return branch

    def switch_branch(self, branch_id: str) -> bool:
        """Переключается на другую ветку."""
        index = self._load_index()
        for b in index["branches"]:
            if b["id"] == branch_id:
                index["current"] = branch_id
                self.current_branch = branch_id
                self._save_index(index)
                logger.info(f"Переключено на ветку: {b['name']}")
                return True
        return False

    def get_current_branch(self) -> Optional[Dict]:
        """Получает данные текущей ветки."""
        if not self.current_branch:
            return None
        return self.storage.read_json(f"{self.subfolder}/{self.current_branch}", "meta.json")

    def get_all_branches(self) -> List[Dict]:
        """Получает список всех веток."""
        index = self._load_index()
        return index.get("branches", [])

    def add_context(self, branch_id: str, content: str, category: str = "general") -> bool:
        """Добавляет контекст в ветку."""
        path = f"{self.subfolder}/{branch_id}"
        context_file = self.storage.read_json(path, "context.json")
        if not context_file:
            return False
        item = {
            "id": len(context_file["items"]) + 1,
            "content": content,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        context_file["items"].append(item)
        self.storage.write_json(path, "context.json", context_file)
        # Обновляем счётчик
        meta = self.storage.read_json(path, "meta.json")
        if meta:
            meta["context_items"] = len(context_file["items"])
            meta["updated_at"] = datetime.now().isoformat()
            self.storage.write_json(path, "meta.json", meta)
        logger.info(f"Контекст добавлен в ветку: {branch_id}")
        return True

    def get_context(self, branch_id: str, category: str = None) -> List[Dict]:
        """Получает контекст ветки (можно фильтровать по категории)."""
        path = f"{self.subfolder}/{branch_id}"
        data = self.storage.read_json(path, "context.json")
        if not data:
            return []
        items = data.get("items", [])
        if category:
            items = [i for i in items if i.get("category") == category]
        return items

    def remove_context(self, branch_id: str, item_id: int) -> bool:
        """Удаляет элемент контекста из ветки."""
        path = f"{self.subfolder}/{branch_id}"
        data = self.storage.read_json(path, "context.json")
        if not data:
            return False
        original_len = len(data["items"])
        data["items"] = [i for i in data["items"] if i.get("id") != item_id]
        if len(data["items"]) < original_len:
            self.storage.write_json(path, "context.json", data)
            logger.info(f"Контекст удалён из ветки: {branch_id}")
            return True
        return False

    def delete_branch(self, branch_id: str) -> bool:
        """Удаляет ветку полностью."""
        index = self._load_index()
        index["branches"] = [b for b in index["branches"] if b["id"] != branch_id]
        if index["current"] == branch_id:
            index["current"] = None
            self.current_branch = None
        self._save_index(index)
        logger.info(f"Ветка удалена: {branch_id}")
        return True

    def get_branch_summary(self) -> str:
        """Генерирует сводку для промпта ИИ."""
        branches = self.get_all_branches()
        if not branches:
            return "Нет активных веток"
        lines = ["📊 Ветки контекста:"]
        for b in branches:
            current = "🟢" if b["id"] == self.current_branch else "⚪"
            lines.append(f"  {current} {b['name']} ({b['role']}) - {b['context_items']} записей")
        return "\n".join(lines)