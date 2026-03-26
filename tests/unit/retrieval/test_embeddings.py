"""Tests for embedding protocols and implementations."""

from vectraxis.retrieval.embeddings import (
    EmbeddingProvider,
    FakeEmbeddingProvider,
    LangChainEmbeddingProvider,
    OpenAIEmbeddingProvider,
)

# ---------- FakeEmbeddingProvider ----------


class TestFakeEmbeddingProviderProtocol:
    def test_fake_provider_implements_protocol(self):
        provider = FakeEmbeddingProvider(dimension=384)
        assert isinstance(provider, EmbeddingProvider)


class TestFakeEmbeddingProvider:
    def test_fake_provider_returns_correct_dimension(self):
        provider = FakeEmbeddingProvider(dimension=384)
        vectors = provider.embed(["hello", "world"])
        for vec in vectors:
            assert len(vec) == 384

    def test_fake_provider_returns_one_vector_per_text(self):
        provider = FakeEmbeddingProvider(dimension=128)
        texts = ["one", "two", "three"]
        vectors = provider.embed(texts)
        assert len(vectors) == 3

    def test_fake_provider_returns_deterministic_for_same_input(self):
        provider = FakeEmbeddingProvider(dimension=128)
        v1 = provider.embed(["hello"])
        v2 = provider.embed(["hello"])
        assert v1 == v2

    def test_fake_provider_different_texts_different_vectors(self):
        provider = FakeEmbeddingProvider(dimension=128)
        vectors = provider.embed(["hello", "world"])
        assert vectors[0] != vectors[1]

    def test_fake_provider_empty_list_returns_empty(self):
        provider = FakeEmbeddingProvider(dimension=128)
        vectors = provider.embed([])
        assert vectors == []

    def test_fake_provider_dimension_property(self):
        provider = FakeEmbeddingProvider(dimension=384)
        assert provider.dimension == 384


# ---------- OpenAIEmbeddingProvider ----------


class TestOpenAIEmbeddingProviderProtocol:
    def test_openai_provider_implements_protocol(self):
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert isinstance(provider, EmbeddingProvider)


class TestOpenAIEmbeddingProvider:
    def test_openai_provider_has_dimension(self):
        provider = OpenAIEmbeddingProvider(api_key="test-key", dimension=768)
        assert provider.dimension == 768

    def test_openai_provider_stores_model_name(self):
        provider = OpenAIEmbeddingProvider(
            api_key="test-key", model="text-embedding-3-large"
        )
        assert provider.model == "text-embedding-3-large"


# ---------- LangChainEmbeddingProvider ----------


class TestLangChainEmbeddingProvider:
    def test_langchain_provider_implements_protocol(self):
        provider = LangChainEmbeddingProvider(api_key="test-key")
        assert isinstance(provider, EmbeddingProvider)

    def test_langchain_provider_has_dimension(self):
        provider = LangChainEmbeddingProvider(api_key="test-key", dimension=768)
        assert provider.dimension == 768

    def test_langchain_provider_default_dimension(self):
        provider = LangChainEmbeddingProvider(api_key="test-key")
        assert provider.dimension == 1536
