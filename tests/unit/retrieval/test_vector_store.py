"""Tests for vector store protocols and implementations."""

from vectraxis.models.retrieval import Chunk
from vectraxis.retrieval.vector_store import InMemoryVectorStore, VectorStore


class TestInMemoryVectorStoreProtocol:
    def test_in_memory_store_implements_protocol(self):
        store = InMemoryVectorStore()
        assert isinstance(store, VectorStore)


class TestInMemoryVectorStore:
    def _make_chunk(self, content: str, index: int = 0, doc_id: str = "doc-1") -> Chunk:
        return Chunk(document_id=doc_id, content=content, index=index)

    def test_add_and_search(self):
        store = InMemoryVectorStore()
        chunks = [
            self._make_chunk("about cats", index=0),
            self._make_chunk("about dogs", index=1),
            self._make_chunk("about birds", index=2),
        ]
        # Vectors designed so that query is most similar to first chunk
        vectors = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
        store.add(chunks, vectors)

        query_vector = [0.9, 0.1, 0.0]  # Most similar to first vector
        results = store.search(query_vector, top_k=3)
        assert len(results) == 3
        assert results[0].chunk.content == "about cats"

    def test_search_returns_top_k(self):
        store = InMemoryVectorStore()
        chunks = [self._make_chunk(f"chunk-{i}", index=i) for i in range(10)]
        # Each vector is a one-hot in 10 dimensions
        vectors = [[1.0 if j == i else 0.0 for j in range(10)] for i in range(10)]
        store.add(chunks, vectors)

        query_vector = [1.0] * 10  # Similar to all
        results = store.search(query_vector, top_k=3)
        assert len(results) == 3

    def test_search_empty_store_returns_empty(self):
        store = InMemoryVectorStore()
        results = store.search([1.0, 0.0, 0.0], top_k=5)
        assert results == []

    def test_search_results_have_scores(self):
        store = InMemoryVectorStore()
        chunks = [self._make_chunk("test", index=0)]
        vectors = [[1.0, 0.0]]
        store.add(chunks, vectors)

        results = store.search([1.0, 0.0], top_k=1)
        assert len(results) == 1
        assert isinstance(results[0].score, float)

    def test_search_results_ordered_by_score_descending(self):
        store = InMemoryVectorStore()
        chunks = [
            self._make_chunk("a", index=0),
            self._make_chunk("b", index=1),
            self._make_chunk("c", index=2),
        ]
        vectors = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.5, 0.5, 0.0],
        ]
        store.add(chunks, vectors)

        query_vector = [1.0, 0.0, 0.0]
        results = store.search(query_vector, top_k=3)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_add_multiple_times(self):
        store = InMemoryVectorStore()

        chunks1 = [self._make_chunk("first", index=0)]
        vectors1 = [[1.0, 0.0]]
        store.add(chunks1, vectors1)

        chunks2 = [self._make_chunk("second", index=1)]
        vectors2 = [[0.0, 1.0]]
        store.add(chunks2, vectors2)

        results = store.search([1.0, 0.0], top_k=5)
        assert len(results) == 2
        assert results[0].chunk.content == "first"

    def test_search_with_source_ids_filters(self):
        store = InMemoryVectorStore()
        chunks = [
            Chunk(document_id="d1", content="a", index=0, metadata={"source_id": "s1"}),
            Chunk(document_id="d2", content="b", index=0, metadata={"source_id": "s2"}),
            Chunk(document_id="d3", content="c", index=0, metadata={"source_id": "s3"}),
        ]
        vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        store.add(chunks, vectors)

        results = store.search([1.0, 0.0, 0.0], top_k=5, source_ids=["s1"])
        assert len(results) == 1
        assert results[0].chunk.content == "a"

    def test_search_with_multiple_source_ids(self):
        store = InMemoryVectorStore()
        chunks = [
            Chunk(document_id="d1", content="a", index=0, metadata={"source_id": "s1"}),
            Chunk(document_id="d2", content="b", index=0, metadata={"source_id": "s2"}),
            Chunk(document_id="d3", content="c", index=0, metadata={"source_id": "s3"}),
        ]
        vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        store.add(chunks, vectors)

        results = store.search([1.0, 1.0, 1.0], top_k=5, source_ids=["s1", "s3"])
        assert len(results) == 2
        contents = {r.chunk.content for r in results}
        assert contents == {"a", "c"}

    def test_search_source_ids_no_match_returns_empty(self):
        store = InMemoryVectorStore()
        chunks = [
            Chunk(document_id="d1", content="a", index=0, metadata={"source_id": "s1"}),
        ]
        vectors = [[1.0, 0.0]]
        store.add(chunks, vectors)

        results = store.search([1.0, 0.0], top_k=5, source_ids=["nonexistent"])
        assert results == []

    def test_search_source_ids_none_returns_all(self):
        store = InMemoryVectorStore()
        chunks = [
            Chunk(document_id="d1", content="a", index=0, metadata={"source_id": "s1"}),
            Chunk(document_id="d2", content="b", index=0, metadata={"source_id": "s2"}),
        ]
        vectors = [[1.0, 0.0], [0.0, 1.0]]
        store.add(chunks, vectors)

        results = store.search([1.0, 1.0], top_k=5, source_ids=None)
        assert len(results) == 2
