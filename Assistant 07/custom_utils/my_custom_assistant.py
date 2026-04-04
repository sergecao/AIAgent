from services.storage_service import StorageService
from services.ai_service import AIService
from core.text_processor import TextProcessor

class MyWorkflowManager:
    def __init__(self):
        # Инициализируем сервисы
        self.storage = StorageService()
        self.ai = AIService()
        self.processor = TextProcessor()
        
        # РЕЕСТР КОМАНД: связываем имя команды с методом
        # Теперь вы можете вызывать их динамически!
        self.commands = {
            "save_note": self.save_note,
            "improve_text": self.improve_text,
            "summarize_session": self.summarize_session,
            "get_stats": self.get_stats
        }

    # --- Ваши пользовательские сценарии (Комбо) ---
    
    def save_note(self, folder, filename, text):
        """Сохранить заметку в хранилище"""
        return self.storage.write_json(folder, filename, {"content": text})

    def improve_text(self, text):
        """Улучшить текст через ИИ"""
        prompt = self.processor.get_prompt(text, "улучшить")
        return self.ai.generate_text(prompt)

    def summarize_session(self, session_id):
        """Сложное комбо: найти сессию -> прочитать -> сжать через ИИ"""
        data = self.storage.read_json("sessions", f"{session_id}.json")
        if not data:
            return "Сессия не найдена"
        
        text_content = str(data) # Упрощение
        prompt = self.processor.get_prompt(text_content, "кратко")
        return self.ai.generate_text(prompt)

    def get_stats(self):
        """Получить статистику хранилища"""
        return self.storage.get_storage_info()

    # --- Движок управления ---
    
    def run_command(self, command_name, *args, **kwargs):
        """
        Универсальный запуск любой команды по имени.
        Пример: manager.run_command("improve_text", "мой текст")
        """
        if command_name not in self.commands:
            return f"Ошибка: Команда '{command_name}' не найдена."
        
        func = self.commands[command_name]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Ошибка выполнения: {str(e)}"

    def list_available_commands(self):
        """Вернуть список доступных команд"""
        return list(self.commands.keys())

# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===
if __name__ == "__main__":
    manager = MyWorkflowManager()
    
    # 1. Смотрим, что умеет менеджер
    print("Доступные команды:", manager.list_available_commands())
    
    # 2. Вызываем команду по имени (можно получать имя из UI или конфига)
    result = manager.run_command("get_stats")
    print("Статистика:", result)
    
    # 3. Вызываем сложное комбо
    # text = "привет, это тестовый текст для проверки"
    # improved = manager.run_command("improve_text", text)
    # print("Улучшено:", improved)