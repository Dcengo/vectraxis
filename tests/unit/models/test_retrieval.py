"""TDD tests for vectraxis.models.retrieval module.

Tests define the API contract for:
- Document model
- Chunk model
- EmbeddingResult model
- SearchResult model
"""

import pytest
from pydantic import ValidationError

from vectraxis.models.common import VectraxisModel, generate_id
from vectraxis.models.retrieval import (
    Chunk,
    Document,
    EmbeddingResult,
    SearchResult,
)

# --- Document ---


class TestDocument:
    """Tests for the Document model."""

    def test_create_with_required_fields(self):
        doc = Document(
            id=generate_id(),
            content="This is the document content.",
        )
        assert doc.content == "This is the document content."

    def test_metadata_defaults_to_empty_dict(self):
        doc = Document(id=generate_id(), content="content")
        assert doc.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"author": "test", "pages": 10}
        doc = Document(id=generate_id(), content="content", metadata=meta)
        assert doc.metadata == meta

    def test_source_id_is_optional(self):
        doc = Document(id=generate_id(), content="content")
        assert doc.source_id is None

    def test_source_id_can_be_set(self):
        doc = Document(id=generate_id(), content="content", source_id="src-123")
        assert doc.source_id == "src-123"

    def test_requires_content(self):
        with pytest.raises(ValidationError):
            Document(id=generate_id())

    def test_serialization(self):
        doc = Document(
            id="doc-1",
            content="hello",
            metadata={"k": "v"},
            source_id="src-1",
        )
        data = doc.model_dump()
        assert data["id"] == "doc-1"
        assert data["content"] == "hello"
        assert data["metadata"] == {"k": "v"}
        assert data["source_id"] == "src-1"

    def test_is_vectraxis_model(self):
        assert issubclass(Document, VectraxisModel)


# --- Chunk ---


class TestChunk:
    """Tests for the Chunk model."""

    def test_create_with_required_fields(self):
        chunk = Chunk(
            id=generate_id(),
            document_id="doc-1",
            content="chunk content",
            index=0,
        )
        assert chunk.document_id == "doc-1"
        assert chunk.content == "chunk content"
        assert chunk.index == 0

    def test_metadata_defaults_to_empty_dict(self):
        chunk = Chunk(
            id=generate_id(),
            document_id="doc-1",
            content="content",
            index=0,
        )
        assert chunk.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"start_char": 0, "end_char": 100}
        chunk = Chunk(
            id=generate_id(),
            document_id="doc-1",
            content="content",
            index=0,
            metadata=meta,
        )
        assert chunk.metadata == meta

    def test_requires_document_id(self):
        with pytest.raises(ValidationError):
            Chunk(id=generate_id(), content="content", index=0)

    def test_requires_content(self):
        with pytest.raises(ValidationError):
            Chunk(id=generate_id(), document_id="doc-1", index=0)

    def test_requires_index(self):
        with pytest.raises(ValidationError):
            Chunk(id=generate_id(), document_id="doc-1", content="content")

    def test_index_is_int(self):
        chunk = Chunk(
            id=generate_id(),
            document_id="doc-1",
            content="content",
            index=5,
        )
        assert isinstance(chunk.index, int)

    def test_serialization(self):
        chunk = Chunk(
            id="ch-1",
            document_id="doc-1",
            content="text",
            index=3,
            metadata={"key": "val"},
        )
        data = chunk.model_dump()
        assert data["document_id"] == "doc-1"
        assert data["index"] == 3

    def test_is_vectraxis_model(self):
        assert issubclass(Chunk, VectraxisModel)


# --- EmbeddingResult ---


class TestEmbeddingResult:
    """Tests for the EmbeddingResult model."""

    def test_create_with_required_fields(self):
        er = EmbeddingResult(
            chunk_id="ch-1",
            vector=[0.1, 0.2, 0.3],
            model_name="text-embedding-3-small",
        )
        assert er.chunk_id == "ch-1"
        assert er.vector == [0.1, 0.2, 0.3]
        assert er.model_name == "text-embedding-3-small"

    def test_vector_is_list_of_floats(self):
        er = EmbeddingResult(
            chunk_id="ch-1",
            vector=[1.0, 2.0, 3.0],
            model_name="model",
        )
        assert isinstance(er.vector, list)
        assert all(isinstance(v, float) for v in er.vector)

    def test_vector_can_be_empty(self):
        er = EmbeddingResult(
            chunk_id="ch-1",
            vector=[],
            model_name="model",
        )
        assert er.vector == []

    def test_vector_with_high_dimensions(self):
        vec = [0.01 * i for i in range(1536)]
        er = EmbeddingResult(
            chunk_id="ch-1",
            vector=vec,
            model_name="text-embedding-3-small",
        )
        assert len(er.vector) == 1536

    def test_requires_chunk_id(self):
        with pytest.raises(ValidationError):
            EmbeddingResult(vector=[0.1], model_name="model")

    def test_requires_vector(self):
        with pytest.raises(ValidationError):
            EmbeddingResult(chunk_id="ch-1", model_name="model")

    def test_requires_model_name(self):
        with pytest.raises(ValidationError):
            EmbeddingResult(chunk_id="ch-1", vector=[0.1])

    def test_serialization(self):
        er = EmbeddingResult(
            chunk_id="ch-1",
            vector=[0.5, 0.6],
            model_name="test-model",
        )
        data = er.model_dump()
        assert data["chunk_id"] == "ch-1"
        assert data["vector"] == [0.5, 0.6]
        assert data["model_name"] == "test-model"

    def test_is_vectraxis_model(self):
        assert issubclass(EmbeddingResult, VectraxisModel)


# --- SearchResult ---


class TestSearchResult:
    """Tests for the SearchResult model."""

    def _make_chunk(self) -> Chunk:
        return Chunk(
            id=generate_id(),
            document_id="doc-1",
            content="relevant content",
            index=0,
        )

    def test_create_with_required_fields(self):
        chunk = self._make_chunk()
        sr = SearchResult(chunk=chunk, score=0.95)
        assert sr.chunk == chunk
        assert sr.score == 0.95

    def test_metadata_defaults_to_empty_dict(self):
        sr = SearchResult(chunk=self._make_chunk(), score=0.5)
        assert sr.metadata == {}

    def test_metadata_can_be_set(self):
        meta = {"search_method": "cosine"}
        sr = SearchResult(chunk=self._make_chunk(), score=0.8, metadata=meta)
        assert sr.metadata == meta

    def test_score_is_float(self):
        sr = SearchResult(chunk=self._make_chunk(), score=0.75)
        assert isinstance(sr.score, float)

    def test_requires_chunk(self):
        with pytest.raises(ValidationError):
            SearchResult(score=0.5)

    def test_requires_score(self):
        with pytest.raises(ValidationError):
            SearchResult(chunk=self._make_chunk())

    def test_serialization(self):
        chunk = self._make_chunk()
        sr = SearchResult(chunk=chunk, score=0.9, metadata={"method": "vector"})
        data = sr.model_dump()
        assert data["score"] == 0.9
        assert data["metadata"] == {"method": "vector"}
        assert "chunk" in data

    def test_is_vectraxis_model(self):
        assert issubclass(SearchResult, VectraxisModel)
