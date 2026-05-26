"""
knowledge/ingest.py
Document ingestion pipeline — feeds PDFs, markdown, and text files into ChromaDB.
"""
import time
import hashlib
from pathlib import Path
from typing import Iterator

import chromadb
from chromadb.config import Settings


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_pdf(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except ImportError:
        return f"[PDF Error] PyMuPDF not installed. Run: pip install pymupdf\nFile: {path}"
    except Exception as e:
        return f"[PDF Error] Could not read {path}: {e}"


def ingest_directory(
    sources_dir: str = "knowledge/sources",
    chromadb_path: str = "data/chromadb",
    collection_name: str = "jane_knowledge",
    ollama_url: str = "http://localhost:11434",
    embedding_model: str = "nomic-embed-text",
    chunk_size: int = 500,
    overlap: int = 50,
) -> dict:
    """Ingest all supported files from sources_dir into ChromaDB."""
    from memory.long_term import OllamaEmbeddingFunction

    sources = Path(sources_dir)
    if not sources.exists():
        return {"error": f"Sources directory not found: {sources_dir}"}

    embed_fn = OllamaEmbeddingFunction(model=embedding_model, base_url=ollama_url)
    client = chromadb.PersistentClient(
        path=chromadb_path,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    stats = {"files_processed": 0, "chunks_added": 0, "errors": []}
    readers = {".txt": _read_txt, ".md": _read_txt, ".pdf": _read_pdf}

    for filepath in sources.rglob("*"):
        if not filepath.is_file():
            continue
        suffix = filepath.suffix.lower()
        reader = readers.get(suffix)
        if not reader:
            continue

        print(f"📄 Ingesting: {filepath.name}...")
        try:
            text = reader(filepath)
            if not text.strip():
                continue
            chunks = _chunk_text(text, chunk_size, overlap)
            ids, documents, metadatas = [], [], []
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(f"{filepath.name}:{i}:{chunk[:50]}".encode()).hexdigest()
                # Skip if already exists
                existing = collection.get(ids=[chunk_id])
                if existing["ids"]:
                    continue
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "source": filepath.name,
                    "chunk_index": i,
                    "timestamp": time.time(),
                })
            if ids:
                collection.add(documents=documents, ids=ids, metadatas=metadatas)
                stats["chunks_added"] += len(ids)
            stats["files_processed"] += 1
        except Exception as e:
            stats["errors"].append(f"{filepath.name}: {e}")

    return stats


if __name__ == "__main__":
    import yaml
    config_path = Path("config.yaml")
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    k = config.get("knowledge", {})
    o = config.get("ollama", {})
    result = ingest_directory(
        sources_dir=k.get("sources_dir", "knowledge/sources"),
        chromadb_path=k.get("chromadb_path", "data/chromadb"),
        collection_name=k.get("collection_name", "jane_knowledge"),
        ollama_url=o.get("base_url", "http://localhost:11434"),
        embedding_model=o.get("models", {}).get("embedding", "nomic-embed-text"),
        chunk_size=k.get("chunk_size", 500),
        overlap=k.get("chunk_overlap", 50),
    )
    print(f"✅ Done! {result}")
