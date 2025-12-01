import chromadb
import chromadb.utils.embedding_functions as embedding_functions # <--- НОВОЕ
import uuid
from datetime import datetime
from pathlib import Path

class MemoryEngine:
    def __init__(self,collection_name="core_memory"):
        self.base_dir = Path(__file__).parent.parent
        self.db_path = self.base_dir / "data" / "memory"
        self.db_path.mkdir(parents=True, exist_ok=True)

        print(f"🔌 Подключаюсь к памяти по адресу: {self.db_path}")
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # --- ИЗМЕНЕНИЕ: Выбираем мульти-язычную модель ---
        # Она скачается один раз при первом запуске (около 400 МБ)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )

        # Передаем эту функцию в коллекцию
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn  # <--- ВАЖНО!
        )

    def save(self, text, type="chat"):
        mem_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.collection.add(
            documents=[text],
            metadatas=[{"type": type, "time": timestamp}],
            ids=[mem_id]
        )
        print(f"💾 Сохранено: '{text[:30]}...'")

    def search(self, query, limit=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        if results['documents']:
            return results['documents'][0]
        return []

# --- ТЕСТ ---
if __name__ == "__main__":
    mem = MemoryEngine()
    # mem.save("Eidolon - это мой проект ИИ с душой.")
    # mem.save("Меня зовут Лекс, я учусь в КПИ на прикладной математике.")
    # mem.save("Я разрабатываю проект Eidolon - локальный ИИ.")
    