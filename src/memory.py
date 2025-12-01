import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import uuid
from datetime import datetime
from pathlib import Path

class MemoryEngine:
    # ТЕПЕРЬ МЫ ПРИНИМАЕМ ПУТЬ К ПАПКЕ, А НЕ ИМЯ
    def __init__(self, db_path): 
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # print(f"🔌 Подключаюсь к памяти: {self.db_path}")
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )

        # Имя коллекции теперь может быть одинаковым ("main"), 
        # так как сами базы физически лежат в разных папках!
        self.collection = self.client.get_or_create_collection(
            name="persona_memory", 
            embedding_function=self.embed_fn
        )

    def save(self, text, type="chat"):
        mem_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.collection.add(
            documents=[text],
            metadatas=[{"type": type, "time": timestamp}],
            ids=[mem_id]
        )

    def search(self, query, limit=3):
        results = self.collection.query(query_texts=[query], n_results=limit)
        if results['documents']:
            return results['documents'][0]
        return []