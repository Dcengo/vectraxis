"""Embedding provider protocols and implementations."""

from __future__ import annotations

import hashlib
import random
from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @property
    def dimension(self) -> int: ...


class FakeEmbeddingProvider:
    """Deterministic fake embedding provider for testing.

    Uses a hash of the input text to seed a random number generator,
    producing reproducible vectors.
    """

    def __init__(self, dimension: int = 1536) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_single(text) for text in texts]

    def _embed_single(self, text: str) -> list[float]:
        seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        return [rng.gauss(0, 1) for _ in range(self._dimension)]


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider. Stores configuration for API calls."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            "OpenAI embedding requires an API call. "
            "Use FakeEmbeddingProvider for testing."
        )


class LangChainEmbeddingProvider:
    """Embedding provider using LangChain's OpenAIEmbeddings for real API calls."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
    ) -> None:
        from langchain_openai import OpenAIEmbeddings

        self._embeddings = OpenAIEmbeddings(
            model=model,
            api_key=api_key,  # type: ignore[call-arg]
            dimensions=dimension,
        )
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._embeddings.embed_documents(texts)
