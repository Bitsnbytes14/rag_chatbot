from functools import lru_cache

from openai import AzureOpenAI, OpenAI

from ragbot import config


@lru_cache(maxsize=1)
def _client():
    """Build the client on first use, so importing this module needs no keys."""
    if config.USE_AZURE:
        return AzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
        )
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _model(azure_name: str, openai_name: str) -> str:
    # On Azure the "model" argument is the deployment name.
    return azure_name if config.USE_AZURE else openai_name


def embed(texts: list[str]) -> list[list[float]]:
    model = _model(config.AZURE_EMBED_DEPLOYMENT, config.OPENAI_EMBED_MODEL)
    response = _client().embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def chat(messages: list[dict]) -> str:
    model = _model(config.AZURE_CHAT_DEPLOYMENT, config.OPENAI_CHAT_MODEL)
    response = _client().chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content
