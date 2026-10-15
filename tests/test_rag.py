import hashlib
import math
import re

import pytest

from ragbot import config, ingest, rag
from ragbot.store import Store

DIM = 256


def fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic offline embedder: hashed bag of words, normalized."""
    vectors = []
    for text in texts:
        vec = [0.0] * DIM
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vectors.append([v / norm for v in vec])
    return vectors


@pytest.fixture
def store(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "hostel.md").write_text("Hostel gate closing time is 10 pm every night.")
    (docs / "library.md").write_text("Library fine for late books is 5 rupees per day.")
    s = Store(str(tmp_path / "chroma"), "test", fake_embed)
    ingest.ingest_folder(str(docs), s)
    return s


def test_chunk_text_overlap_and_coverage():
    text = "abcdefghijklmnopqrstuvwxyz" * 4  # 104 chars
    chunks = ingest.chunk_text(text, size=30, overlap=10)
    assert all(len(c) <= 30 for c in chunks)
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev[-10:] == nxt[:10]
    rebuilt = chunks[0] + "".join(c[10:] for c in chunks[1:])
    assert rebuilt == text


def test_ingest_then_query_finds_right_document(store):
    assert store.count() == 2
    hits = store.query("What time does the hostel gate close?", k=1)
    assert hits[0]["source"] == "hostel.md"
    assert "10 pm" in hits[0]["text"]


def test_unrelated_question_gets_fallback_without_llm(store, monkeypatch):
    def fail(messages):
        raise AssertionError("chat must not be called")

    monkeypatch.setattr(rag.llm, "chat", fail)
    text, sources = rag.answer("Explain quantum chromodynamics gluons", [], store)
    assert text == rag.FALLBACK
    assert sources == []


def test_relevant_question_calls_chat_once_with_context(store, monkeypatch):
    calls = []
    monkeypatch.setattr(rag.llm, "chat", lambda m: calls.append(m) or "10 pm")
    text, sources = rag.answer("What time does the hostel gate close?", [], store)
    assert text == "10 pm"
    assert sources == ["hostel.md"]
    assert len(calls) == 1
    assert "Hostel gate closing time is 10 pm" in calls[0][-1]["content"]


def test_history_is_trimmed_to_last_turns(store, monkeypatch):
    history = []
    for i in range(config.HISTORY_TURNS + 4):
        history.append({"role": "user", "content": f"q{i}"})
        history.append({"role": "assistant", "content": f"a{i}"})
    calls = []
    monkeypatch.setattr(rag.llm, "chat", lambda m: calls.append(m) or "ok")
    rag.answer("What time does the hostel gate close?", history, store)
    sent = calls[0]
    kept = sent[1:-1]  # drop system prompt and final question
    assert len(kept) == config.HISTORY_TURNS * 2
    assert kept[0]["content"] == "q4"
    assert kept[-1]["content"] == f"a{config.HISTORY_TURNS + 3}"
