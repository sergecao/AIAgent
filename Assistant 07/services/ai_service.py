# services/ai_service.py
import requests
import threading
import queue
import time
from config import AI_CONFIG

class AIService:
    def __init__(self):
        self.url = AI_CONFIG["url"]
        self.default_model = AI_CONFIG["default_model"]
        self.timeout = AI_CONFIG["timeout"]
        self.request_queue = queue.Queue()
        self.lock = threading.Lock()
        self.results = {}
        self.result_id_counter = 0
        
        self.worker_thread = threading.Thread(target=self._api_worker, daemon=True)
        self.worker_thread.start()
    
    def _api_worker(self):
        while True:
            try:
                task_id, prompt, max_tokens, callback = self.request_queue.get()
                if task_id is None: break
                result = self._send_request_sync(prompt, max_tokens)
                with self.lock:
                    self.results[task_id] = result
                if callback: callback(task_id, result)
                self.request_queue.task_done()
            except Exception as e:
                print(f"Ошибка воркера API: {e}")
                time.sleep(1)
    
    def _send_request_sync(self, prompt: str, max_tokens: int):
        if len(prompt) > 100000: prompt = prompt[:95000] + "...[cut]..."
        payload = {
            "model": self.default_model, "prompt": prompt,
            "max_tokens": max_tokens, "temperature": 0.3
        }
        try:
            response = requests.post(self.url, json=payload, headers={"Content-Type": "application/json"}, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()['choices'][0]['text'].strip()
            return f"❌ Ошибка API (HTTP {response.status_code})"
        except Exception as e:
            return f"❌ Ошибка соединения: {str(e)}"
    
    def generate_text_async(self, prompt: str, max_tokens=512, callback=None):
        task_id = self.result_id_counter
        self.result_id_counter += 1
        self.request_queue.put((task_id, prompt, max_tokens, callback))
        return task_id
    
    def generate_structured_json_async(self, prompt: str, callback=None):
        full_prompt = prompt + "\nВАЖНО: Отвечай ТОЛЬКО валидным JSON объектом. Без markdown."
        return self.generate_text_async(full_prompt, max_tokens=1000, callback=callback)
    
    def get_result(self, task_id: int):
        with self.lock: return self.results.get(task_id)