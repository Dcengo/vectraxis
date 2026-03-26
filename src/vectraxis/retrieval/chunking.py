"""Chunking protocols and implementations for splitting documents into chunks."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from vectraxis.models.retrieval import Chunk, Document


@runtime_checkable
class Chunker(Protocol):
    """Protocol for document chunkers."""

    def chunk(self, document: Document) -> list[Chunk]: ...


class FixedSizeChunker:
    """Splits document text into fixed-size character chunks."""

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, document: Document) -> list[Chunk]:
        content = document.content
        if not content:
            return []

        pieces: list[str] = []
        for i in range(0, len(content), self.chunk_size):
            pieces.append(content[i : i + self.chunk_size])

        metadata = {"source_id": document.source_id} if document.source_id else {}
        return [
            Chunk(document_id=document.id, content=piece, index=idx, metadata=metadata)
            for idx, piece in enumerate(pieces)
        ]


class RecursiveChunker:
    """Splits document text recursively using a hierarchy of separators."""

    def __init__(
        self,
        max_size: int = 500,
        separators: list[str] | None = None,
    ) -> None:
        self.max_size = max_size
        self.separators = (
            separators if separators is not None else ["\n\n", "\n", ". ", " "]
        )

    def chunk(self, document: Document) -> list[Chunk]:
        content = document.content
        if not content:
            return []

        pieces = self._split_recursive(content, self.separators)

        metadata = {"source_id": document.source_id} if document.source_id else {}
        return [
            Chunk(document_id=document.id, content=piece, index=idx, metadata=metadata)
            for idx, piece in enumerate(pieces)
        ]

    def _split_recursive(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using the separator hierarchy."""
        if not separators:
            if len(text) <= self.max_size:
                return [text]
            # No more separators; force-split by max_size
            return [
                text[i : i + self.max_size] for i in range(0, len(text), self.max_size)
            ]

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep)
        # Filter out empty strings from split
        parts = [p for p in parts if p]

        if len(parts) == 1:
            # This separator didn't help; try the next one
            return self._split_recursive(text, remaining_seps)

        result: list[str] = []
        for part in parts:
            if len(part) <= self.max_size:
                result.append(part)
            else:
                result.extend(self._split_recursive(part, remaining_seps))

        return result
