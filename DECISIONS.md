# Decision Log

## ChromaDB as the vector store

Decision: Use ChromaDB with local persistent storage.
Why: It runs in process, needs no server or account, and stores text and metadata next to the vectors.
Alternatives considered: FAISS (fast, but no built in storage of text and metadata), Pinecone (hosted, adds cost and setup that a small demo does not need).

## Full rebuild on every ingest

Decision: Reset the collection at the start of every ingest run, then index all files again.
Why: Edited or deleted documents never leave stale chunks behind. It is simple, and fine for a small document set where re-embedding is quick and cheap.
Alternatives considered: Deleting only the chunks of each changed file (cheaper for large sets, but needs change tracking and more code).

## Cosine distance

Decision: Create the collection with hnsw:space set to cosine.
Why: Text embeddings are compared by direction, and cosine distance gives a bounded score (0 to 2) that is easy to threshold.
Alternatives considered: Chroma default L2 distance, which is harder to reason about for a cutoff, and inner product.

## Chunk size 500 with overlap 80

Decision: Split text into 500 character chunks that overlap by 80 characters.
Why: Chunks are small enough to be specific and large enough to hold a full fact. The overlap keeps a fact from being cut in half at a boundary.
Alternatives considered: Larger chunks (1000 or more, which blur topics together), sentence or paragraph splitting (better quality, more code).
Status: Initial values, to be tuned after live testing.

## Top 4 retrieval

Decision: Fetch the 4 closest chunks per question.
Why: Enough context to answer most questions while keeping the prompt short and cheap.
Alternatives considered: Top 1 (misses facts spread over chunks), top 10 (more noise and cost).

## Distance cutoff 0.65

Decision: Drop retrieved chunks whose cosine distance is above 0.65.
Why: It stops weakly related text from reaching the model, which reduces made up answers.
Alternatives considered: No cutoff (always answers, even off topic), a rerank step (more complexity).
Status: Initial value, to be tuned after live testing.

## Fallback answer without calling the LLM

Decision: If no chunk passes the cutoff, return "I could not find that in the documents." directly.
Why: It is free, instant and cannot hallucinate.
Alternatives considered: Always call the LLM and rely on the prompt to refuse (costs tokens and is less reliable).

## Last 6 turns of history

Decision: Send only the last 6 turns (12 messages) of chat history to the model.
Why: It supports follow up questions while keeping the prompt size bounded.
Alternatives considered: Full history (grows without limit), no history (breaks follow up questions), summarizing old turns (extra complexity).

## Automatic Azure switch

Decision: Use Azure OpenAI whenever AZURE_OPENAI_ENDPOINT is set, otherwise use OpenAI.
Why: One setting switches providers, and no code change is needed.
Alternatives considered: A separate PROVIDER variable (one more thing to keep in sync), two separate code paths in the app.

## Streamlit for the UI

Decision: Build the chat UI with Streamlit.
Why: It has built in chat components, needs no frontend code, and deploys easily on Streamlit Community Cloud.
Alternatives considered: Gradio (similar), Flask or FastAPI with a JavaScript frontend (much more code).

## Fake embedder for offline tests

Decision: Tests use a hashed bag of words embedder and a temporary Chroma directory.
Why: Tests are fast, free, deterministic and need no keys or network.
Alternatives considered: Calling the real embedding API in tests (slow, costs money, flaky), mocking the whole store (would not test Chroma behavior).
