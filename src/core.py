import ollama
import json
from pathlib import Path
from src.memory import MemoryEngine
# Импортируем наш реестр инструментов и генератор описания
# (Убедитесь, что файл src/tools/__init__.py создан, как мы обсуждали ранее)
try:
    from src.tools import AVAILABLE_TOOLS, get_tools_description
except ImportError:
    # Заглушка, если вы еще не создали tools.py
    AVAILABLE_TOOLS = {}
    def get_tools_description(tools): return ""

class EidolonCore:
    def __init__(self, profile_name="core_persona.json"):
        print("⚙️ Инициализация Ядра...")
        # Вся загрузка происходит в одном месте
        self.load_persona(profile_name)

    def load_persona(self, profile_name):
        print(f"🔄 Загрузка профиля: {profile_name}...")
        
        self.base_dir = Path(__file__).parent.parent
        profile_path = self.base_dir / "data" / "profiles" / profile_name
        
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                self.persona = json.load(f)
        except FileNotFoundError:
            print(f"❌ Ошибка: Профиль {profile_name} не найден. Грузим дефолт.")
            return

        # 1. Определяем Модель (Ядро)
        self.current_model = self.persona.get("model", "llama3.1")
        
        # 2. Определяем Коллекцию Памяти (RAG)
        mem_name = self.persona.get("memory_collection", "core_memory")
        self.memory = MemoryEngine(collection_name=mem_name)

        # 3. Определяем Доступные Инструменты
        self.allowed_tools = self.persona.get("allowed_tools", [])

        print(f"👤 Личность: {self.persona['name']}")
        print(f"🧠 Активное ядро: {self.current_model}")
        print(f"📚 Активная память: {mem_name}")
        print(f"🛠️ Инструменты: {len(self.allowed_tools)} шт.")

    def chat(self, user_input):
        print(f"\n🗣️ User: {user_input}")

        # --- ЭТАП 1: RAG (Память) ---
        found_memories = self.memory.search(user_input, limit=2)
        if found_memories:
            context_str = "\n".join([f"- {m}" for m in found_memories])
        else:
            context_str = "Нет релевантных воспоминаний."

        # --- ЭТАП 2: Формирование Промпта с Инструментами ---
        tools_instruction = get_tools_description(self.allowed_tools)

        system_msg = f"""
        ТЫ: {self.persona['system_prompt']}
        ТВОЙ ПРОФИЛЬ: Имя: {self.persona['name']}, Тон: {self.persona['tone']}
        ФАКТЫ ИЗ ПАМЯТИ: 
        {context_str}
        
        {tools_instruction}
        """

        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_input},
        ]

        # --- ЭТАП 3: Первый запрос (Check for Tools) ---
        # stream=False, чтобы мы могли проверить ответ на наличие JSON
        print(f"🦙 Анализирую запрос на {self.current_model}...")
        response = ollama.chat(
            model=self.current_model, 
            messages=messages, 
            stream=False
        )
        reply = response['message']['content']

        # --- ЭТАП 4: Проверка на вызов Инструмента ---
        # Если ответ начинается с {, значит модель хочет вызвать функцию
        if reply.strip().startswith('{') and '"tool":' in reply:
            try:
                print(f"🔧 Вызов инструмента: {reply}")
                tool_data = json.loads(reply)
                tool_name = tool_data.get("tool")
                tool_args = tool_data.get("args")

                if tool_name in AVAILABLE_TOOLS and tool_name in self.allowed_tools:
                    # Выполняем функцию
                    tool_func = AVAILABLE_TOOLS[tool_name]
                    # Поддержка аргументов или без них
                    tool_result = tool_func(tool_args) if tool_args else tool_func()
                    
                    print(f"✅ Результат: {tool_result}")

                    # Добавляем результат в историю для ЛЛМ
                    messages.append({'role': 'assistant', 'content': reply})
                    messages.append({'role': 'user', 'content': f"SYSTEM: Результат инструмента: {tool_result}. Теперь дай финальный ответ пользователю."})

                    # Второй запрос (Финальный ответ) - уже со стримингом
                    stream = ollama.chat(
                        model=self.current_model, 
                        messages=messages, 
                        stream=True
                    )
                    
                    full_final_reply = ""
                    for chunk in stream:
                        part = chunk['message']['content']
                        full_final_reply += part
                        yield part
                    
                    # Сохраняем итог в память
                    self.memory.save(f"Q: {user_input}\nTool: {tool_name}\nA: {full_final_reply}", type="tool_chat")
                    return

            except Exception as e:
                print(f"❌ Ошибка инструмента: {e}")
                # Если ошибка JSON, просто отдаем текст как есть
                yield f"[Ошибка инструмента: {e}]"
                return

        # --- ЭТАП 5: Обычный ответ (если инструментов не было) ---
        # Так как мы уже получили ответ в step 3 без стрима, мы его просто отдаем.
        # (Можно переделать на стрим, но для простоты MVP пока так)
        yield reply
        self.memory.save(f"User: {user_input}\nEidolon: {reply}", type="chat_history")

# --- ТЕСТ ---
if __name__ == "__main__":
    bot = EidolonCore()