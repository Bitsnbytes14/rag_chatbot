# Instructions for AI coding agents

## Purpose

A small RAG chatbot that answers questions from .md and .txt files using ChromaDB, an OpenAI or Azure OpenAI model, and a Streamlit UI.
It must say "I could not find that in the documents." when the documents do not contain the answer.

## Folder map

1. ragbot/config.py: settings from environment variables
2. ragbot/llm.py: OpenAI or Azure client, embed() and chat()
3. ragbot/store.py: ChromaDB wrapper
4. ragbot/ingest.py: chunking and indexing, run as python -m ragbot.ingest docs
5. ragbot/rag.py: retrieval, prompt building and answer()
6. app.py: Streamlit chat UI
7. tests/test_rag.py: offline tests
8. docs/: sample documents
9. DECISIONS.md: decision log, DEPLOYMENT.md: deployment guide

## Setup and tests

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Coding rules

1. Keep it simple and readable. Do not add features that were not asked for.
2. Every change must keep pytest passing.
3. Tests must stay offline. No real API calls, ever.
4. Never commit secrets. Keys belong in .env, which is git ignored.

## Hard rules

1. Never run git commands that change history (no commit, push, branch, PR). The owner does all git work.
2. Do not use dashes in any prose written for the owner. Use numbered lists or commas instead.
3. End every task with a short summary of files changed, test output, and anything not verified.
