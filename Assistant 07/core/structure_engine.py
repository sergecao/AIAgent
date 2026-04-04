# core/structure_engine.py
import os
import json
from datetime import datetime
from config import PSA_ROOT

class StructureEngine:
    """Движок структуры хранилища D:\\psa\\"""
    
    REGISTRY_FILE = "registry.json"
    
    def __init__(self):
        self.registry_path = os.path.join(PSA_ROOT, self.REGISTRY_FILE)
        self.registry = self._load_registry()
    
    def _load_registry(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"structure_last_scan": "", "tasks": []}
    
    def save_registry(self):
        os.makedirs(PSA_ROOT, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def get_tree_summary(self):
        """Генерирует компактное дерево для промпта."""
        if not os.path.exists(PSA_ROOT): return "Пусто"
        lines = ["Структура D:\\psa\\:"]
        for root, dirs, files in os.walk(PSA_ROOT):
            level = root.replace(PSA_ROOT, '').count(os.sep)
            if level > 3: continue
            indent = '  ' * level
            folder_name = os.path.basename(root) or "ROOT"
            count = len(files) + len(dirs)
            lines.append(f"{indent}📁 {folder_name} ({count})")
        return "\n".join(lines)
    
    def check_limits(self):
        """Возвращает dict с коэффициентами ограничений."""
        roots = [d for d in os.listdir(PSA_ROOT) 
                 if os.path.isdir(os.path.join(PSA_ROOT, d))] if os.path.exists(PSA_ROOT) else []
        root_factor = 0.5 if len(roots) > 10 else 1.0
        
        max_sub = 0
        for r, dirs, _ in os.walk(PSA_ROOT):
            if len(dirs) > max_sub: max_sub = len(dirs)
        sub_factor = 0.5 if max_sub > 5 else 1.0
        
        return {"root_factor": root_factor, "sub_factor": sub_factor}
    
    def add_task(self, title: str):
        task = {
            "id": len(self.registry["tasks"]) + 1,
            "title": title,
            "status": "new",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.registry["tasks"].append(task)
        self.save_registry()
        return task
    
    def get_tasks(self, status="new"):
        return [t for t in self.registry["tasks"] if t["status"] == status]
    
    def complete_task(self, task_id: int):
        for t in self.registry["tasks"]:
            if t["id"] == task_id:
                t["status"] = "done"
                break
        self.save_registry()
    
    def archive_tasks(self):
        for t in self.registry["tasks"]:
            if t["status"] == "done": t["status"] = "archived"
        self.save_registry()