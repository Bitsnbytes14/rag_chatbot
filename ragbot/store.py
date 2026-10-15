from typing import Callable

import chromadb

EmbedFn = Callable[[list[str]], list[list[float]]]


class Store:
    """Thin wrapper around one Chroma collection that uses cosine distance."""

    def __init__(self, path: str, name: str, embed_fn: EmbedFn):
        self._embed = embed_fn
        self._name = name
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._open()

    def _open(self):
        return self._client.get_or_create_collection(
            name=self._name, metadata={"hnsw:space": "cosine"}
        )

    def add(self, ids: list[str], texts: list[str], sources: list[str]) -> None:
        self._collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=self._embed(texts),
            metadatas=[{"source": s} for s in sources],
        )

    def query(self, question: str, k: int) -> list[dict]:
        if self.count() == 0:
            return []
        result = self._collection.query(
            query_embeddings=self._embed([question]), n_results=k
        )
        return [
            {"text": text, "source": meta["source"], "distance": dist}
            for text, meta, dist in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
        ]

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(self._name)
        self._collection = self._open()
