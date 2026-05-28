"""
memory/long_term.py
ChromaDB-backed vector memory — semantic search over all past interactions.
"""
import time
import chromadb
from chromadb.config import Settings


class OllamaEmbeddingFunction(chromadb.EmbeddingFunction):
    """Embedding via Ollama's nomic-embed-text model."""

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def __call__(self, input: list[str]) -> list[list[float]]:
        import requests
        embeddings = []
        for text in input:
            resp = requests.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings.append(data["embeddings"][0])
        return embeddings


class LongTermMemory:
    def __init__(self, config: dict = None):
        cfg = config or {}
        mem_cfg = cfg.get("memory", {}).get("long_term", {})
        ollama_cfg = cfg.get("ollama", {})

        self.chromadb_path = mem_cfg.get("chromadb_path", "data/chromadb")
        self.collection_name = mem_cfg.get("collection_name", "jane_memory")
        self.max_results = mem_cfg.get("max_results", 5)
        embedding_model = ollama_cfg.get("models", {}).get("embedding", "nomic-embed-text")
        ollama_url = ollama_cfg.get("base_url", "http://localhost:11434")

        self.embed_fn = OllamaEmbeddingFunction(model=embedding_model, base_url=ollama_url)

        self.client = chromadb.PersistentClient(
            path=self.chromadb_path,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(self, text: str, metadata: dict = None):
        if not text.strip():
            return
        doc_id = f"mem_{int(time.time() * 1000)}"
        self.collection.add(
            documents=[text],
            ids=[doc_id],
            metadatas=[metadata or {"timestamp": time.time()}],
        )

    def add_interaction(self, user_msg: str, assistant_msg: str):
        text = f"User: {user_msg}\nJane: {assistant_msg}"
        self.add_document(text, metadata={"type": "interaction", "timestamp": time.time()})

    def retrieve(self, query: str, n_results: int = None) -> list[str]:
        n = n_results or self.max_results
        count = self.collection.count()
        if count == 0:
            return []
        n = min(n, count)
        results = self.collection.query(query_texts=[query], n_results=n)
        return results.get("documents", [[]])[0]

    def format_for_prompt(self, query: str, n_results: int = None) -> str:
        docs = self.retrieve(query, n_results)
        if not docs:
            return ""
        return "\n---\n".join(docs)

    def count(self) -> int:
        return self.collection.count()
