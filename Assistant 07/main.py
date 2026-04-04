# main.py
import tkinter as tk
import os
import sys
from data.psa_manager import PSAManager
from ui.floating_window import FloatingAssistant
from core.task_engine import TaskEngine
from core.session_manager import SessionManager
from core.branch_manager import BranchManager
from services.storage_service import StorageService
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Main")

if __name__ == "__main__":
    logger.info("=== ЗАПУСК AI ASSISTANT ===")
    
    # 1. Хранилище
    psa_manager = PSAManager()
    if not psa_manager.ensure_structure():
        logger.error("❌ Не удалось создать хранилище!")
        sys.exit(1)
    logger.info("Хранилище готово")
    
    # 2. Сервисы
    storage = StorageService()
    logger.info("StorageService инициализирован")
    
    # 3. Ядро
    task_engine = TaskEngine(storage)
    session_manager = SessionManager(storage)
    branch_manager = BranchManager(storage)
    logger.info("TaskEngine, SessionManager, BranchManager готовы")
    
    # 4. UI
    root = tk.Tk()
    app = FloatingAssistant(root, task_engine, session_manager, branch_manager)
    
    logger.info("UI запущен")
    root.mainloop()
    
    # 5. Очистка
    session_manager.stop_auto_save()
    logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ ===")