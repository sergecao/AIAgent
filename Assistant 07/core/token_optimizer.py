# core/token_optimizer.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("TokenOptimizer")

class TokenOptimizer:
    """Оптимизатор токенов для экономии при отправке в ИИ."""
    
    MAX_CONTEXT_ITEMS = 50
    MAX_TEXT_LENGTH = 5000
    COMPRESSION_RATIO = 0.7
    
    def __init__(self):
        self.stats = {
            "original_tokens": 0,
            "optimized_tokens": 0,
            "savings_percent": 0
        }
    
    def optimize_context(self, items: List[Dict], max_items: int = None) -> List[Dict]:
        """Сокращает список контекстных элементов."""
        limit = max_items or self.MAX_CONTEXT_ITEMS
        
        if len(items) <= limit:
            return items
        
        logger.info(f"Сокращение контекста: {len(items)} → {limit}")
        
        # Берём последние N элементов (самые свежие)
        optimized = items[-limit:]
        self._update_stats(len(items), len(optimized))
        
        return optimized
    
    def compress_text(self, text: str, max_length: int = None) -> str:
        """Сжимает текст до заданной длины."""
        limit = max_length or self.MAX_TEXT_LENGTH
        
        if len(text) <= limit:
            return text
        
        logger.info(f"Сжатие текста: {len(text)} → {limit} символов")
        
        # Оставляем начало и конец с маркером пропуска
        cut_point = int(limit * self.COMPRESSION_RATIO)
        compressed = (
            text[:cut_point] +
            f"\n\n[... сокращено {len(text) - limit} символов ...]\n\n" +
            text[-(limit - cut_point):]
        )
        
        self._update_stats(len(text), len(compressed))
        return compressed
    
    def summarize_for_prompt(self, session_data: Dict) -> str:
        """Создаёт компактную сводку сессии для промпта."""
        if not session_data:
            return "Нет активной сессии"
        
        lines = [
            f"📌 Сессия: {session_data.get('title', 'Без названия')}",
            f"🕐 Начата: {session_data.get('start_time', '?')[:16]}",
        ]
        
        # Добавляем теги
        tags = session_data.get('tags', [])
        if tags:
            lines.append(f"🏷 Теги: {', '.join(tags)}")
        
        # Контекст (сжатый)
        context = session_data.get('context', {})
        if context:
            lines.append(f"📄 Контекст: {len(context)} записей")
            for key, value in list(context.items())[:5]:
                val_str = str(value)[:100]
                if len(str(value)) > 100:
                    val_str += "..."
                lines.append(f"   • {key}: {val_str}")
            if len(context) > 5:
                lines.append(f"   ... и ещё {len(context) - 5} записей")
        
        return "\n".join(lines)
    
    def optimize_branch_context(self, items: List[Dict], category: str = None) -> str:
        """Оптимизирует контекст ветки для промпта."""
        if not items:
            return "Контекст пуст"
        
        # Фильтр по категории
        if category:
            items = [i for i in items if i.get('category') == category]
        
        # Ограничиваем количество
        items = self.optimize_context(items, max_items=20)
        
        lines = []
        for item in items:
            content = item.get('content', '')[:200]
            if len(item.get('content', '')) > 200:
                content += "..."
            ts = item.get('timestamp', '')[:16]
            cat = item.get('category', 'general')
            lines.append(f"[{cat}] {ts}: {content}")
        
        return "\n".join(lines)
    
    def estimate_tokens(self, text: str) -> int:
        """Оценивает количество токенов (приблизительно)."""
        # ~4 символа на токен для русского текста
        return len(text) // 4
    
    def _update_stats(self, original: int, optimized: int):
        """Обновляет статистику оптимизации."""
        self.stats["original_tokens"] += original
        self.stats["optimized_tokens"] += optimized
        
        if self.stats["original_tokens"] > 0:
            savings = (
                (self.stats["original_tokens"] - self.stats["optimized_tokens"]) /
                self.stats["original_tokens"] * 100
            )
            self.stats["savings_percent"] = round(savings, 2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику оптимизации."""
        return {
            **self.stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_stats(self):
        """Сбрасывает статистику."""
        self.stats = {
            "original_tokens": 0,
            "optimized_tokens": 0,
            "savings_percent": 0
        }
        logger.info("Статистика токенов сброшена")