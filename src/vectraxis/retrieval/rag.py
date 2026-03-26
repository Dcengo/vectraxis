"""RAG retriever that combines chunking, embedding, and vector search."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectraxis.models.retrieval import Document, SearchResult
    from vectraxis.retrieval.chunking import Chunker
    from vectraxis.retrieval.embeddings import EmbeddingProvider
    from vectraxis.retrieval.vector_store import VectorStore


class RAGRetriever:
    """Retrieval-Augmented Generation retriever.

    Combines a chunker, embedding provider, and vector store to index
    documents and retrieve relevant chunks for a given query.
    """

    def __init__(
        self,
        chunker: Chunker,
        embedder: EmbeddingProvider,
        store: VectorStore,
    ) -> None:
        self.chunker = chunker
        self.embedder = embedder
        self.store = store

    def index(self, documents: list[Document]) -> None:
        """Chunk, embed, and store documents."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)

        if not all_chunks:
            return

        texts = [chunk.content for chunk in all_chunks]
        vectors = self.embedder.embed(texts)
        self.store.add(all_chunks, vectors)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        source_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        """Embed the query and search the vector store."""
        query_vector = self.embedder.embed([query])[0]
        return self.store.search(query_vector, top_k=top_k, source_ids=source_ids)
