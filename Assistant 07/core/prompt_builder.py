# core/prompt_builder.py
from core.structure_engine import StructureEngine
from config import PSA_ROOT

class PromptBuilder:
    """Сборщик промптов для ИИ с учётом контекста системы."""
    
    def __init__(self):
        self.engine = StructureEngine()
    
    def build_system_prompt(self, user_input: str, branch_context: str = "") -> str:
        """Собирает промпт с учётом ветки контекста."""
        tree_summary = self.engine.get_tree_summary()
        limits = self.engine.check_limits()
        
        # Добавляем контекст текущей ветки
        branch_info = f"\n# ТЕКУЩАЯ ВЕТКА КОНТЕКСТА\n{branch_context}" if branch_context else ""
        
        prompt = f"""
# РОЛЬ
Ты — Архитектор Личной Эффективности. Работаешь с хранилищем {PSA_ROOT}.
Твоя цель: Анализировать входные данные и сортировать их по appropriate папкам/веткам.

# КОНТЕКСТ (Структура хранилища)
{tree_summary}
{branch_info}

# РЕГЛАМЕНТ
1. Определи тип деятельности пользователя (договоры, управление, разработка и т.д.)
2. Предложи сохранить в соответствующую ветку или папку
3. Если ветки нет — предложи создать новую
4. Всегда предлагай 3 варианта в JSON формате

# ФОРМАТ ОТВЕТА (JSON)
{{
  "analysis": "Краткий анализ деятельности",
  "suggested_branch": "название_ветки",
  "suggested_path": "путь/к/папке",
  "suggestions": [
    {{"id": 1, "type": "save_to_branch", "label": "Сохранить в ветку...", "branch": "..."}},
    {{"id": 2, "type": "create_task", "label": "В задачи", "task_title": "..."}},
    {{"id": 3, "type": "create_branch", "label": "Новая ветка", "branch_name": "..."}}
  ]
}}

# ЗАПРОС ПОЛЬЗОВАТЕЛЯ
{user_input}
"""
        return prompt