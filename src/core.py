import ollama
import json
import yaml
from pathlib import Path
from src.memory import MemoryEngine

# Импорт инструментов
try:
    from src.tools import AVAILABLE_TOOLS, get_tools_description
except ImportError:
    AVAILABLE_TOOLS = {}
    def get_tools_description(tools): return ""

class EidolonCore:
    # ИЗМЕНЕНИЕ 1: Теперь принимаем profile_folder="Friend"
    def __init__(self, profile_folder="Friend"):
        print("⚙️ Инициализация Ядра...")
        self.load_persona(profile_folder)

    def load_persona(self, folder_name):
        print(f"🔄 Загрузка Персоны из папки: {folder_name}...")
        
        self.base_dir = Path(__file__).parent.parent
        
        # 1. Путь к папке конкретного персонажа
        persona_dir = self.base_dir / "profiles" / folder_name
        
        # 2. Ищем внутри config.yaml
        config_path = persona_dir / "core_persona.yaml"
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.persona = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Ошибка: Конфиг не найден в {config_path}")
            # Аварийная заглушка
            self.persona = {
                "name": "Error",
                "role": "System",
                "system_prompt": "Error loading profile.",
                "allowed_tools": []
            }

        # 3. Определяем Модель
        self.current_model = self.persona.get("model", "llama3.1")
        
        # 4. Инициализируем Память ВНУТРИ папки персонажа
        # Теперь база лежит в Eidolon/data/profiles/Friend/memory_db
        memory_path = persona_dir / "memory_db"
        self.memory = MemoryEngine(db_path=memory_path)

        # 5. Инструменты
        self.allowed_tools = self.persona.get("allowed_tools", [])

        print(f"👤 Личность: {self.persona.get('name')}")
        print(f"🧠 Ядро: {self.current_model}")
        print(f"📂 Папка данных: {persona_dir}")

    def chat(self, user_input):
        print(f"\n🗣️ User: {user_input}")

        # 1. RAG
        found_memories = self.memory.search(user_input, limit=2)
        context_str = "\n".join([f"- {m}" for m in found_memories]) if found_memories else "Нет данных."

        # 2. Промпт
        tools_instruction = get_tools_description(self.allowed_tools)

        system_msg = f"""
        ТЫ: {self.persona.get('system_prompt', '')}
        ПРОФИЛЬ: Имя: {self.persona.get('name')}, Тон: {self.persona.get('tone', 'Normal')}
        ФАКТЫ ИЗ ПАМЯТИ: 
        {context_str}
        
        {tools_instruction}
        """

        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_input},
        ]

        # 3. Первый запрос (без стрима для проверки JSON)
        print(f"🦙 Запрос к {self.current_model}...")
        try:
            response = ollama.chat(model=self.current_model, messages=messages, stream=False)
            reply = response['message']['content']
        except Exception as e:
            yield f"Ошибка связи с Ollama: {e}"
            return

        # 4. Проверка Tool Use
        if reply.strip().startswith('{') and '"tool":' in reply:
            try:
                print(f"🔧 Tool Call: {reply}")
                tool_data = json.loads(reply)
                tool_name = tool_data.get("tool")
                tool_args = tool_data.get("args")

                if tool_name in AVAILABLE_TOOLS and tool_name in self.allowed_tools:
                    tool_func = AVAILABLE_TOOLS[tool_name]
                    tool_result = tool_func(tool_args) if tool_args else tool_func()
                    print(f"✅ Result: {tool_result}")

                    messages.append({'role': 'assistant', 'content': reply})
                    messages.append({'role': 'user', 'content': f"SYSTEM: Результат: {tool_result}. Дай ответ."})

                    stream = ollama.chat(model=self.current_model, messages=messages, stream=True)
                    full_reply = ""
                    for chunk in stream:
                        part = chunk['message']['content']
                        full_reply += part
                        yield part
                    
                    self.memory.save(f"Q: {user_input}\nTool: {tool_name}\nA: {full_reply}", type="tool_chat")
                    return

            except Exception as e:
                print(f"❌ Tool Error: {e}")
                yield f"[Ошибка инструмента: {e}]"
                return

        # 5. Обычный ответ
        yield reply
        self.memory.save(f"User: {user_input}\nEidolon: {reply}", type="chat_history")