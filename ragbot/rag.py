from ragbot import config, llm
from ragbot.store import Store

FALLBACK = "I could not find that in the documents."

SYSTEM_PROMPT = (
    "You are a documentation assistant. Answer only from the context provided in "
    "the user message. Do not use outside knowledge. If the context does not contain "
    f'the answer, reply exactly: "{FALLBACK}"'
)


def get_store() -> Store:
    return Store(config.CHROMA_DIR, config.COLLECTION_NAME, llm.embed)


def retrieve(question: str, store: Store | None = None) -> list[dict]:
    """Top TOP_K chunks, minus any that are too far from the question."""
    store = store or get_store()
    hits = store.query(question, config.TOP_K)
    return [h for h in hits if h["distance"] <= config.MAX_DISTANCE]


def answer(
    question: str, history: list[dict], store: Store | None = None
) -> tuple[str, list[str]]:
    """Return (answer text, sources used). history is a list of chat messages."""
    chunks = retrieve(question, store)
    if not chunks:
        return FALLBACK, []

    context = "\n\n".join(f"[{c['source']}]\n{c['text']}" for c in chunks)
    recent = history[-config.HISTORY_TURNS * 2 :]  # one turn = user + assistant message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *recent,
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    sources = sorted({c["source"] for c in chunks})
    return llm.chat(messages), sources
