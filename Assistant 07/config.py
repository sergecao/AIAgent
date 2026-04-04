# config.py
import os

# =============================================================================
# ПУТИ К ФАЙЛАМ
# =============================================================================
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH") or r"./DigitalOffice.csv"

# =============================================================================
# ХРАНИЛИЩЕ (с проверкой диска D:)
# =============================================================================
def _get_psa_root():
    """Проверяет наличие диска D:, иначе использует локальную папку."""
    env_path = os.getenv("PSA_ROOT")
    if env_path:
        return env_path
    if os.path.exists("D:\\"):
        return r"D:\psa"
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "psa_storage")
    print(f"⚠ Диск D: не найден. Используем: {local_path}")
    return local_path

PSA_ROOT = _get_psa_root()

PSA_SUBFOLDERS = [
    "sessions", "tasks", "Words", "Plans", "Works", "Locks", "Files", "Templates"
]

# =============================================================================
# НАСТРОЙКИ ИИ
# =============================================================================
AI_CONFIG = {
    "url": "http://phosmindtest.int.corp.phosagro.ru/vllm-proxy/v1/completions",
    "default_model": "Qwen3-Coder-480B-AWQ",
    "max_tokens": 512,
    "timeout": 30
}

# =============================================================================
# НАСТРОЙКИ СЕССИЙ
# =============================================================================
SESSION_CONFIG = {
    "auto_save_enabled": True,
    "auto_save_interval_minutes": 5,
    "max_history_sessions": 100
}

# =============================================================================
# ЦВЕТОВАЯ СХЕМА
# =============================================================================
COLORS = {
    "bg": "#2b2b2b",
    "header": "#1f1f1f",
    "fg": "#ffffff",
    "input_bg": "#1e1e1e",
    "success": "#00ff00",
    "warning": "#ff6b6b"
}
# config.py (добавить в конец)
# =============================================================================
# НАСТРОЙКИ ВЕТОК КОНТЕКСТА
# =============================================================================
BRANCH_CONFIG = {
    "default_roles": ["default", "contracts", "management", "development", "personal"],
    "auto_categorize": True,
    "max_context_items": 100
}