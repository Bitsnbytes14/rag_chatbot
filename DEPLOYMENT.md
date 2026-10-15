# Deployment

Status: live API calls not yet verified.

## Run locally

1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (macOS or Linux: `source .venv/bin/activate`)
3. Install packages: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your keys
5. Index the sample docs: `python -m ragbot.ingest docs`
6. Start the app: `streamlit run app.py`

## Set up Azure OpenAI

1. In the Azure portal, create an Azure OpenAI resource.
2. In Azure AI Foundry (or Azure OpenAI Studio), deploy a chat model, for example gpt-4o-mini. Note the deployment name.
3. Deploy an embedding model, for example text-embedding-3-small. Note the deployment name.
4. From the resource, copy the endpoint and a key.
5. Fill these variables in `.env`:
   1. AZURE_OPENAI_ENDPOINT: the resource endpoint, for example https://my-resource.openai.azure.com/
   2. AZURE_OPENAI_API_KEY: the key
   3. AZURE_OPENAI_API_VERSION: a supported API version, for example 2024-06-01
   4. AZURE_CHAT_DEPLOYMENT: the chat deployment name
   5. AZURE_EMBED_DEPLOYMENT: the embedding deployment name

Setting the endpoint switches the app to Azure. The deployment names are passed as the model argument.

## Deploy on Streamlit Community Cloud

1. Push the repo to GitHub.
2. On Streamlit Community Cloud, create a new app from the repo with app.py as the main file.
3. Open the app settings, go to Secrets, and add the same variables as in `.env`, in TOML form, for example `OPENAI_API_KEY = "sk-..."`. Streamlit exposes top level secrets as environment variables, so config.py reads them without changes.
4. Make the app index the docs on startup if the collection is empty. Add this near the top of app.py, after the store is created:

```python
if store.count() == 0:
    from ragbot.ingest import ingest_folder
    ingest_folder("docs", store)
```

5. Deploy. The first start will embed the docs, which needs the keys to be valid.

## Known limits

1. Chroma data is stored on local disk, so it resets on every redeploy or restart of the hosted app. The startup ingest rebuilds it.
2. There is no authentication. Anyone with the link can use the app and spend your API credits.
3. Only the sample documents are included.
4. Live OpenAI and Azure calls have not been tested yet. Only the offline tests have run.
