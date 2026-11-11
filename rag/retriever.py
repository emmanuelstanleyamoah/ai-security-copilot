from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge_base"
MIN_SCORE = 0.08


@dataclass(frozen=True)
class Hit:
    source: str
    title: str
    text: str
    score: float


class TfidfKnowledgeBase:
    """Local retriever. No model download, so the demo and tests run offline."""

    def __init__(self, knowledge_dir: Path | None = None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_DIR
        self.docs = _load_docs(self.knowledge_dir)
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([doc["text"] for doc in self.docs])

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        if not query.strip() or not self.docs:
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        k = min(top_k, len(scores))
        order = np.argsort(scores)[::-1][:k]
        hits: list[Hit] = []
        for index in order:
            score = float(scores[int(index)])
            if score < MIN_SCORE:
                continue
            doc = self.docs[int(index)]
            hits.append(Hit(source=doc["source"], title=doc["title"], text=doc["text"], score=score))
        return hits


def _load_docs(knowledge_dir: Path) -> list[dict[str, str]]:
    docs = []
    for path in sorted(knowledge_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = next((line[2:].strip() for line in raw.splitlines() if line.startswith("# ")), path.stem)
        docs.append({"source": path.name, "title": title, "text": raw})
    if not docs:
        raise FileNotFoundError(f"No markdown knowledge in {knowledge_dir}")
    return docs


class ChromaKnowledgeBase:
    """Optional dense index. The default path stays lexical so CI does not need a vector service."""

    def __init__(self, persist_dir: str | None = None):
        if not persist_dir:
            raise RuntimeError("Set CHROMA_PATH to use the Chroma adapter.")
        import chromadb

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("security-knowledge")

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        result = self.collection.query(query_texts=[query], n_results=top_k)
        hits: list[Hit] = []
        documents = result.get("documents") or [[]]
        metadatas = result.get("metadatas") or [[]]
        distances = result.get("distances") or [[]]
        for text, meta, distance in zip(documents[0], metadatas[0], distances[0]):
            meta = meta or {}
            hits.append(
                Hit(
                    source=str(meta.get("source", "chroma")),
                    title=str(meta.get("title", "Knowledge")),
                    text=text,
                    score=float(1 - distance) if distance is not None else 0.0,
                )
            )
        return hits


def dump_index_manifest(retriever: TfidfKnowledgeBase, path: Path) -> None:
    path.write_text(
        json.dumps([{"source": doc["source"], "title": doc["title"]} for doc in retriever.docs], indent=2),
        encoding="utf-8",
    )
