# RAG Docs Chatbot

A small chatbot that answers questions from your own .md and .txt files, and says so when the answer is not in them.

## How it works

1. Ingest reads each file in a folder and splits it into overlapping chunks of 500 characters.
2. Each chunk is turned into an embedding vector and stored in ChromaDB with its file name.
3. A question is embedded and the 4 closest chunks are fetched, using cosine distance.
4. Chunks that are too far away (distance above 0.65) are dropped. If none are left, the bot replies "I could not find that in the documents." without calling the LLM.
5. Otherwise the LLM gets the system prompt, recent chat history, the chunks and the question, and answers only from that context. The sources are shown under the answer.

## Setup

```
python -m venv .venv
.venv\Scripts\activate        # on macOS or Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # on macOS or Linux: cp .env.example .env
```

Then put your key in `.env` as `OPENAI_API_KEY`.

## Switch to Azure OpenAI

Fill in `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION`, `AZURE_CHAT_DEPLOYMENT` and `AZURE_EMBED_DEPLOYMENT` in `.env`. As soon as the endpoint is set, the app uses Azure. Leave it empty to use OpenAI. See DEPLOYMENT.md for details.

## Ingest

```
python -m ragbot.ingest docs
```

## Run

```
streamlit run app.py
```

## Test

```
pytest
```

The tests are offline. They use a fake embedder and never call a real API.
