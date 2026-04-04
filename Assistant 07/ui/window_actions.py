# ui/window_actions.py
"""
Window Actions — действия главного окна.

Отвечает за:
- Поиск в CSV
- Обработку текста через ИИ
- Открытие ссылок
- Обработку предложений ИИ
"""

import threading
import json
import tkinter as tk  # ← ДОБАВЛЕНО
from services.ai_service import AIService
from services.csv_service import CSVService
from core.text_processor import TextProcessor
from core.prompt_builder import PromptBuilder
from utils.link_opener import LinkOpener


class WindowActions:
    """Класс действий главного окна."""
    
    def __init__(self, main_window):
        self.main = main_window
        self.ai_service = None
        self.csv_service = None
        self.text_processor = None
        self.prompt_builder = None

    def setup_services(self):
        """Инициализация сервисов."""
        self.ai_service = AIService()
        self.csv_service = CSVService()
        self.text_processor = TextProcessor()
        self.prompt_builder = PromptBuilder()

    def run_search(self):
        """Запустить поиск по запросу."""
        query = self.main.entry_query.get().strip()
        if not query:
            return
        self.main.txt_result.delete(1.0, tk.END)
        self.main.suggestion_bar.hide()
        threading.Thread(target=self._process_search_logic, args=(query,), daemon=True).start()

    def _process_search_logic(self, query: str):
        """Логика поиска (в потоке)."""
        csv_results = self.csv_service.search(query)
        self.main._log("📊 НАЙДЕНО В РЕЕСТРЕ:")
        for line in csv_results:
            self.main._log(line)
        
        context = "\n".join(csv_results)
        branch_context = ""
        if self.main.branch_manager:
            branch_context = self.main.branch_manager.get_branch_summary()
        
        if "Ошибка" not in context and "не найдено" not in context:
            self.main._set_status("🤖 Опрос нейросети...")
            prompt = self.prompt_builder.build_system_prompt(
                f"Контекст: {context}\nВопрос: {query}", branch_context=branch_context)
            self.ai_service.generate_structured_json_async(prompt, self._handle_ai_suggestions)
        else:
            self.main._log("Нет данных для анализа.")
            self.main._set_status("Готово")

    def _handle_ai_suggestions(self, task_id: int, text: str):
        """Обработка ответа ИИ с предложениями."""
        self.main._log(f"\n🤖 ОТВЕТ ИИ:\n{text}")
        try:
            data = json.loads(text)
            self.main.suggestion_bar.show(data.get("suggestions", []))
        except:
            pass
        self.main._set_status("Готово")

    def process_text(self, mode: str):
        """Обработать текст в указанном режиме."""
        text = self.main.entry_query.get().strip()
        if not text:
            return self.main._log("⚠ Введите текст!")
        self.main.txt_result.delete(1.0, tk.END)
        threading.Thread(target=self._process_text_logic, args=(text, mode), daemon=True).start()

    def _process_text_logic(self, text: str, mode: str):
        """Логика обработки текста (в потоке)."""
        prompt = self.text_processor.get_prompt(text, mode)
        self.ai_service.generate_text_async(prompt, callback=lambda id, r: self.main._log(r))
        self.main._set_status("Готово")

    def open_links(self):
        """Открыть ссылки из текста."""
        text = self.main.entry_query.get().strip() or self.main.txt_result.get(1.0, tk.END)
        links = LinkOpener.extract_links(text)
        if links:
            for s, m in LinkOpener.open_all_links(links):
                self.main._log(f"{s}: {m}")
        else:
            self.main._set_status("⚠ Ссылки не найдены")

    def handle_suggestion(self, data: dict):
        """Обработка клика по предложению ИИ."""
        action_type = data.get('type')
        
        if action_type == 'create_task':
            if self.main.task_engine:
                self.main.task_engine.create_task(data.get('task_title', 'Новая задача'))
            else:
                from core.structure_engine import StructureEngine
                StructureEngine().add_task(data.get('task_title', 'Новая задача'))
            self.main._log("Задача создана!")
            
        elif action_type == 'save_to_branch' and self.main.branch_manager:
            self.main.branch_manager.add_context(
                self.main.branch_manager.current_branch,
                data.get('content', ''), 
                data.get('category', 'general')
            )
            self.main._log("✅ Сохранено в ветку!")
            
        elif action_type == 'create_branch' and self.main.branch_manager:
            self.main.branch_manager.create_branch(data.get('branch_name', 'Новая ветка'))
            self.main._log("✅ Ветка создана!")

    def get_ai_service(self):
        """Получить сервис ИИ."""
        return self.ai_service

    def get_csv_service(self):
        """Получить CSV сервис."""
        return self.csv_service