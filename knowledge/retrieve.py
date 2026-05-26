"""
knowledge/retrieve.py
Semantic search over your personal knowledge base stored in ChromaDB.
"""
import chromadb
from chromadb.config import Settings


class KnowledgeRetriever:
    def __init__(self, config: dict = None):
        cfg = config or {}
        k_cfg = cfg.get("knowledge", {})
        o_cfg = cfg.get("ollama", {})

        self.chromadb_path = k_cfg.get("chromadb_path", "data/chromadb")
        self.collection_name = k_cfg.get("collection_name", "jane_knowledge")
        self.max_results = k_cfg.get("max_results", 5)
        embedding_model = o_cfg.get("models", {}).get("embedding", "nomic-embed-text")
        ollama_url = o_cfg.get("base_url", "http://localhost:11434")

        from memory.long_term import OllamaEmbeddingFunction
        self.embed_fn = OllamaEmbeddingFunction(model=embedding_model, base_url=ollama_url)

        self.client = chromadb.PersistentClient(
            path=self.chromadb_path,
            settings=Settings(anonymized_telemetry=False),
        )
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embed_fn,
            )
        except Exception:
            self.collection = None

    def search(self, query: str, n_results: int = None) -> list[dict]:
        """Semantic search — returns list of {text, source, score} dicts."""
        if not self.collection:
            return []
        n = n_results or self.max_results
        count = self.collection.count()
        if count == 0:
            return []
        n = min(n, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        output = []
        for doc, meta, dist in zip(docs, metas, distances):
            output.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "relevance": round(1 - dist, 3),
            })
        return output

    def format_for_prompt(self, query: str, n_results: int = None) -> str:
        """Return search results formatted for LLM prompt injection."""
        results = self.search(query, n_results)
        if not results:
            return ""
        lines = ["[Relevant Knowledge]:"]
        for r in results:
            lines.append(f"Source: {r['source']} (relevance: {r['relevance']})")
            lines.append(r["text"])
            lines.append("---")
        return "\n".join(lines)

    def count(self) -> int:
        if not self.collection:
            return 0
        return self.collection.count()
