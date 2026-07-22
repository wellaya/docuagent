from openai import AzureOpenAI
from app.config import settings, credential
from azure.identity import get_bearer_token_provider

token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint=settings.foundry_endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2025-04-01-preview",
)


def chunk_text(text: str, max_tokens: int = 400) -> list[str]:
    words = text.split()
    step = max_tokens
    return [" ".join(words[i:i + step]) for i in range(0, len(words), step)]

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model="text-embedding-3-small", input=chunks)
    return [d.embedding for d in resp.data]