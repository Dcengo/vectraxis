"""Tests for chunking protocols and implementations."""

from vectraxis.models.retrieval import Document
from vectraxis.retrieval.chunking import Chunker, FixedSizeChunker, RecursiveChunker

# ---------- FixedSizeChunker ----------


class TestFixedSizeChunkerProtocol:
    def test_fixed_chunker_implements_protocol(self):
        chunker = FixedSizeChunker(chunk_size=50)
        assert isinstance(chunker, Chunker)


class TestFixedSizeChunker:
    def test_fixed_chunker_chunks_by_size(self):
        doc = Document(content="a" * 120)
        chunker = FixedSizeChunker(chunk_size=50)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 3
        assert len(chunks[0].content) == 50
        assert len(chunks[1].content) == 50
        assert len(chunks[2].content) == 20

    def test_fixed_chunker_single_chunk_if_small(self):
        doc = Document(content="short text")
        chunker = FixedSizeChunker(chunk_size=500)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].content == "short text"

    def test_fixed_chunker_sets_document_id(self):
        doc = Document(content="a" * 120)
        chunker = FixedSizeChunker(chunk_size=50)
        chunks = chunker.chunk(doc)
        for chunk in chunks:
            assert chunk.document_id == doc.id

    def test_fixed_chunker_sequential_indices(self):
        doc = Document(content="a" * 120)
        chunker = FixedSizeChunker(chunk_size=50)
        chunks = chunker.chunk(doc)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_fixed_chunker_preserves_content(self):
        content = "Hello world, this is a test of chunking functionality."
        doc = Document(content=content)
        chunker = FixedSizeChunker(chunk_size=20)
        chunks = chunker.chunk(doc)
        joined = "".join(c.content for c in chunks)
        assert joined == content

    def test_fixed_chunker_empty_content_returns_empty(self):
        doc = Document(content="")
        chunker = FixedSizeChunker(chunk_size=50)
        chunks = chunker.chunk(doc)
        assert chunks == []

    def test_fixed_chunker_propagates_source_id(self):
        doc = Document(content="hello world", source_id="src-1")
        chunker = FixedSizeChunker(chunk_size=500)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].metadata["source_id"] == "src-1"

    def test_fixed_chunker_no_source_id_empty_metadata(self):
        doc = Document(content="hello world")
        chunker = FixedSizeChunker(chunk_size=500)
        chunks = chunker.chunk(doc)
        assert "source_id" not in chunks[0].metadata


# ---------- RecursiveChunker ----------


class TestRecursiveChunkerProtocol:
    def test_recursive_chunker_implements_protocol(self):
        chunker = RecursiveChunker(max_size=500)
        assert isinstance(chunker, Chunker)


class TestRecursiveChunker:
    def test_recursive_chunker_splits_on_paragraphs(self):
        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        doc = Document(content=content)
        chunker = RecursiveChunker(max_size=500)
        chunks = chunker.chunk(doc)
        assert len(chunks) == 3
        assert chunks[0].content == "First paragraph."
        assert chunks[1].content == "Second paragraph."
        assert chunks[2].content == "Third paragraph."

    def test_recursive_chunker_respects_max_size(self):
        # A single paragraph that exceeds max_size should be split further
        long_paragraph = "word " * 100  # 500 chars
        content = f"Short.\n\n{long_paragraph.strip()}"
        doc = Document(content=content)
        chunker = RecursiveChunker(max_size=50)
        chunks = chunker.chunk(doc)
        for chunk in chunks:
            assert len(chunk.content) <= 50

    def test_recursive_chunker_sets_document_id(self):
        content = "First.\n\nSecond.\n\nThird."
        doc = Document(content=content)
        chunker = RecursiveChunker(max_size=500)
        chunks = chunker.chunk(doc)
        for chunk in chunks:
            assert chunk.document_id == doc.id

    def test_recursive_chunker_sequential_indices(self):
        content = "First.\n\nSecond.\n\nThird."
        doc = Document(content=content)
        chunker = RecursiveChunker(max_size=500)
        chunks = chunker.chunk(doc)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_recursive_chunker_empty_content_returns_empty(self):
        doc = Document(content="")
        chunker = RecursiveChunker(max_size=500)
        chunks = chunker.chunk(doc)
        assert chunks == []

    def test_recursive_chunker_propagates_source_id(self):
        doc = Document(content="First.\n\nSecond.", source_id="src-2")
        chunker = RecursiveChunker(max_size=500)
        chunks = chunker.chunk(doc)
        for chunk in chunks:
            assert chunk.metadata["source_id"] == "src-2"
