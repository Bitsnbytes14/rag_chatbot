import sys
from pathlib import Path

from ragbot import config, llm
from ragbot.store import Store


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into character chunks; each chunk repeats the last `overlap` chars of the previous."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    step = size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break
    return chunks


def ingest_folder(folder: str, store: Store) -> tuple[int, int]:
    """Rebuild the index from every .md and .txt file in the folder. Returns (files, chunks)."""
    store.reset()  # full rebuild, so edited or deleted files leave no stale chunks
    files = sorted(p for p in Path(folder).iterdir() if p.suffix in (".md", ".txt"))
    total_chunks = 0
    for path in files:
        chunks = chunk_text(
            path.read_text(encoding="utf-8"), config.CHUNK_SIZE, config.CHUNK_OVERLAP
        )
        if not chunks:
            continue
        store.add(
            ids=[f"{path.name}:{i}" for i in range(len(chunks))],
            texts=chunks,
            sources=[path.name] * len(chunks),
        )
        total_chunks += len(chunks)
    return len(files), total_chunks


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "docs"
    store = Store(config.CHROMA_DIR, config.COLLECTION_NAME, llm.embed)
    n_files, n_chunks = ingest_folder(folder, store)
    print("Collection was reset before indexing")
    print(f"Indexed {n_files} files and {n_chunks} chunks from {folder}")
