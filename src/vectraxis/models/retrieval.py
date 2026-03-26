from __future__ import annotations

from typing import Any

from pydantic import Field

from vectraxis.models.common import VectraxisModel, generate_id


class Document(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_id: str | None = None


class Chunk(VectraxisModel):
    id: str = Field(default_factory=generate_id)
    document_id: str
    content: str
    index: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingResult(VectraxisModel):
    chunk_id: str
    vector: list[float]
    model_name: str


class SearchResult(VectraxisModel):
    chunk: Chunk
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)
