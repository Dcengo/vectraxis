"""Vector store protocols and implementations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

from vectraxis.models.retrieval import Chunk, SearchResult


@runtime_checkable
class VectorStore(Protocol):
    """Protocol for vector stores."""

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        source_ids: list[str] | None = None,
    ) -> list[SearchResult]: ...


class InMemoryVectorStore:
    """In-memory vector store using cosine similarity via numpy."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: list[list[float]] = []

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        self._chunks.extend(chunks)
        self._vectors.extend(vectors)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        source_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        if not self._vectors:
            return []

        # Pre-filter by source_ids if provided
        if source_ids is not None:
            source_set = set(source_ids)
            indices = [
                i
                for i, chunk in enumerate(self._chunks)
                if chunk.metadata.get("source_id") in source_set
            ]
            if not indices:
                return []
            filtered_chunks = [self._chunks[i] for i in indices]
            filtered_vectors = [self._vectors[i] for i in indices]
        else:
            filtered_chunks = self._chunks
            filtered_vectors = self._vectors

        matrix = np.array(filtered_vectors)
        query = np.array(query_vector)

        # Cosine similarity
        norms = np.linalg.norm(matrix, axis=1)
        query_norm = np.linalg.norm(query)

        # Avoid division by zero
        denom = norms * query_norm
        denom = np.where(denom == 0, 1e-10, denom)

        similarities = matrix @ query / denom

        # Get top-k indices sorted by descending similarity
        k = min(top_k, len(filtered_chunks))
        top_indices = np.argsort(similarities)[::-1][:k]

        return [
            SearchResult(
                chunk=filtered_chunks[int(idx)],
                score=float(similarities[int(idx)]),
            )
            for idx in top_indices
        ]
