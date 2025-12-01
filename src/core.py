import ollama
import json
from pathlib import Path
# Импортируем наш класс памяти из соседнего файла
from src.memory import MemoryEngine

class EidolonCore:
    def __init__(self, profile_name="core_persona.json"):
        print("⚙️ Инициализация Ядра...")
        self.memory = MemoryEngine()
        self.load_persona(profile_name)
        # Загружаем личность из JSON
        self.base_dir = Path(__file__).parent.parent
        profile_path = self.base_dir / "data" / "profiles" / profile_name
        
        with open(profile_path, "r", encoding="utf-8") as f:
            self.persona = json.load(f)
        print(f"👤 Личность загружена: {self.persona['name']}")

    def chat(self, user_input):
        print(f"\n🗣️ User: {user_input}")

        # 1. RAG: Ищем контекст
        found_memories = self.memory.search(user_input, limit=3)
        if found_memories:
            context_str = "\n".join([f"- {m}" for m in found_memories])
        else:
            context_str = "Нет релевантных воспоминаний."

        # 2. Промпт
        system_msg = f"""
        ИНСТРУКЦИЯ: {self.persona['system_prompt']}
        ТВОЙ ПРОФИЛЬ: Имя: {self.persona['name']}, Тон: {self.persona['tone']}
        ФАКТЫ ИЗ ПАМЯТИ: {context_str}
        """

        # 3. Отправляем в Ollama (ВКЛЮЧАЕМ ПОТОК stream=True)
        print("🦙 Генерирую поток...")
        stream = ollama.chat(
            model='eidolon-core', 
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_input},
            ],
            stream=True  # <--- ВАЖНО!
        )
        
        # 4. Собираем ответ по кусочкам и отдаем их сразу
        full_reply = ""
        for chunk in stream:
            part = chunk['message']['content']
            full_reply += part
            yield part  # Отдаем кусочек наружу (в интерфейс)

        # 5. Сохраняем в память только когда ответ полностью готов
        self.memory.save(f"User: {user_input}\nEidolon: {full_reply}", type="chat_history")
    def load_persona(self, profile_name):
        print(f"🔄 Загрузка профиля: {profile_name}...")
        
        # 1. Загружаем JSON
        self.base_dir = Path(__file__).parent.parent
        profile_path = self.base_dir / "data" / "profiles" / profile_name
        
        with open(profile_path, "r", encoding="utf-8") as f:
            self.persona = json.load(f)
        
        # 2. Получаем имя коллекции из JSON (или берем дефолтное)
        mem_name = self.persona.get("memory_collection", "core_memory")
        
        # 3. Инициализируем (или ПЕРЕинициализируем) память с нужной коллекцией
        self.memory = MemoryEngine(collection_name=mem_name)
        
        print(f"👤 Личность: {self.persona['name']}")
        print(f"📚 Активная память: {mem_name}")
# --- ТЕСТ ---
if __name__ == "__main__":
    bot = EidolonCore()
    
    # # Проверка: спросим то, что он должен знать из памяти
    # answer = bot.chat("Где я живу?")
    # print(f"\n🤖 Eidolon: {answer}")
    
    # # Проверка: просто болтовня
    # answer2 = bot.chat("Как твое настроение?")
    # print(f"\n🤖 Eidolon: {answer2}")