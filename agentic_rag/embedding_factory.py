from enum import Enum
from langchain.embeddings import OpenAIEmbeddings

from agentic_rag.gemini_embedder import GeminiEmbeddings  # ✅ real working version

class EmbeddingProvider(str, Enum):
    OPENAI = "gpt"
    GEMINI = "gemini"

def get_embedding_model(provider: str):
    if provider == EmbeddingProvider.OPENAI:
        return OpenAIEmbeddings()
    elif provider == EmbeddingProvider.GEMINI:
        return GeminiEmbeddings()
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")
