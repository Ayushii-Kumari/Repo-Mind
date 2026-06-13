"""
FAISS-based vector store for code chunks.
Uses sentence-transformers for local embeddings (no API cost).
"""
import os
import json
import pickle
from typing import Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db/faiss_index")
EMBED_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight, good quality


class CodeVectorStore:
    def __init__(self, index_path: str = VECTOR_DB_PATH):
        self.index_path = index_path
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.chunks: list[dict] = []  # {text, file, start_line}
        self.dim = 384  # MiniLM output dimension

    def chunk_code(self, content: str, file_path: str, chunk_size: int = 50) -> list[dict]:
        """Split code into overlapping chunks of lines."""
        lines = content.splitlines()
        chunks = []
        step = chunk_size // 2  # 50% overlap
        for i in range(0, len(lines), step):
            chunk_lines = lines[i : i + chunk_size]
            if not any(l.strip() for l in chunk_lines):
                continue
            chunks.append({
                "text": "\n".join(chunk_lines),
                "file": file_path,
                "start_line": i + 1,
            })
        return chunks

    def add_files(self, files: dict[str, str]):
        """Add a dict of {file_path: content} to the vector store."""
        all_chunks = []
        for path, content in files.items():
            all_chunks.extend(self.chunk_code(content, path))

        if not all_chunks:
            return

        texts = [c["text"] for c in all_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False, batch_size=32)
        embeddings = np.array(embeddings, dtype=np.float32)

        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dim)

        self.index.add(embeddings)
        self.chunks.extend(all_chunks)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant code chunks."""
        if self.index is None or self.index.ntotal == 0:
            return []

        q_emb = self.model.encode([query], show_progress_bar=False)
        q_emb = np.array(q_emb, dtype=np.float32)

        distances, indices = self.index.search(q_emb, min(top_k, self.index.ntotal))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["score"] = float(dist)
                results.append(chunk)
        return results

    def save(self):
        """Save index and metadata to disk."""
        os.makedirs(self.index_path, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, f"{self.index_path}/index.faiss")
        with open(f"{self.index_path}/chunks.pkl", "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        idx_file = f"{self.index_path}/index.faiss"
        chunks_file = f"{self.index_path}/chunks.pkl"
        if not (os.path.exists(idx_file) and os.path.exists(chunks_file)):
            return False
        self.index = faiss.read_index(idx_file)
        with open(chunks_file, "rb") as f:
            self.chunks = pickle.load(f)
        return True

    def clear(self):
        """Reset the store."""
        self.index = None
        self.chunks = []

    def format_context(self, results: list[dict]) -> str:
        """Format search results as a context string for the LLM."""
        if not results:
            return "No relevant code found."
        parts = []
        for r in results:
            parts.append(
                f"### File: {r['file']} (line {r['start_line']})\n```\n{r['text']}\n```"
            )
        return "\n\n".join(parts)
