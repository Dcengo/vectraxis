"""Tests for RAGRetriever."""

from vectraxis.models.retrieval import Document
from vectraxis.retrieval.chunking import FixedSizeChunker
from vectraxis.retrieval.embeddings import FakeEmbeddingProvider
from vectraxis.retrieval.rag import RAGRetriever
from vectraxis.retrieval.vector_store import InMemoryVectorStore


class TestRAGRetriever:
    def _make_retriever(
        self, chunk_size: int = 100, dimension: int = 64
    ) -> RAGRetriever:
        chunker = FixedSizeChunker(chunk_size=chunk_size)
        embedder = FakeEmbeddingProvider(dimension=dimension)
        store = InMemoryVectorStore()
        return RAGRetriever(chunker=chunker, embedder=embedder, store=store)

    def test_rag_retriever_index_and_retrieve(self):
        retriever = self._make_retriever(chunk_size=50, dimension=64)
        docs = [
            Document(content="Cats are wonderful pets that love to play."),
            Document(content="Dogs are loyal companions and great friends."),
        ]
        retriever.index(docs)
        results = retriever.retrieve("pets", top_k=5)
        assert len(results) > 0
        # Each result should have a chunk and a score
        for result in results:
            assert result.chunk.content
            assert isinstance(result.score, float)

    def test_rag_retriever_empty_index_returns_empty(self):
        retriever = self._make_retriever()
        results = retriever.retrieve("anything", top_k=5)
        assert results == []

    def test_rag_retriever_respects_top_k(self):
        retriever = self._make_retriever(chunk_size=20, dimension=64)
        docs = [
            Document(content="a" * 100),  # Will produce 5 chunks
            Document(content="b" * 100),  # Will produce 5 chunks
        ]
        retriever.index(docs)
        results = retriever.retrieve("query", top_k=3)
        assert len(results) == 3

    def test_rag_retriever_filters_by_source_ids(self):
        retriever = self._make_retriever(chunk_size=500, dimension=64)
        docs = [
            Document(content="Cats are wonderful pets.", source_id="src-a"),
            Document(content="Dogs are loyal companions.", source_id="src-b"),
        ]
        retriever.index(docs)
        results = retriever.retrieve("pets", top_k=10, source_ids=["src-a"])
        assert len(results) > 0
        for r in results:
            assert r.chunk.metadata.get("source_id") == "src-a"
