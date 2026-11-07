import os
from typing import List
from google import genai
from emporio_agent.config import settings


class GeminiEmbedder:
    """Handles embedding generation using the official Google GenAI SDK."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set it in your environment or .env file."
            )
        self.client = genai.Client(api_key=self.api_key)
        self.dimension = 3072  # Dimension for gemini-embedding-001

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        response = self.client.models.embed_content(
            model=self.model,
            contents=text.strip(),
        )
        return response.embeddings[0].values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings."""
        if not texts:
            return []

        embeddings = []
        for t in texts:
            embeddings.append(self.embed_text(t))
        return embeddings


# Singleton instance
_embedder = None


def get_embedder() -> GeminiEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = GeminiEmbedder()
    return _embedder
