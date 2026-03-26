"""Dependency injection for API layer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectraxis.agents.base import Agent, FakeLLMProvider, LLMProvider
from vectraxis.agents.pipeline import Pipeline
from vectraxis.agents.router import TaskRouter
from vectraxis.agents.specialized.analysis import AnalysisAgent
from vectraxis.agents.specialized.recommendation import RecommendationAgent
from vectraxis.agents.specialized.summarization import SummarizationAgent
from vectraxis.config import Settings
from vectraxis.db.repositories.data_source import (
    DataSourceRepository,
    InMemoryDataSourceRepository,
)
from vectraxis.db.repositories.prompt import (
    InMemoryPromptRepository,
    PromptRepository,
)
from vectraxis.db.repositories.workflow import (
    InMemoryWorkflowRepository,
    WorkflowRepository,
)
from vectraxis.models.agent import AgentType
from vectraxis.retrieval.chunking import RecursiveChunker
from vectraxis.retrieval.embeddings import FakeEmbeddingProvider
from vectraxis.retrieval.rag import RAGRetriever
from vectraxis.retrieval.vector_store import InMemoryVectorStore

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from vectraxis.retrieval.embeddings import EmbeddingProvider

# Shared singleton RAGRetriever (persists indexed data across requests)
_shared_retriever: RAGRetriever | None = None

# Shared singleton DataSourceRegistry (kept for backward compat during transition)
_shared_data_source_registry = None

# DB session factory (initialized on app startup)
_session_factory: async_sessionmaker[AsyncSession] | None = None

# In-memory repo singletons (used when no DB is available)
_shared_data_source_repo: InMemoryDataSourceRepository | None = None
_shared_prompt_repo: InMemoryPromptRepository | None = None
_shared_workflow_repo: InMemoryWorkflowRepository | None = None


def set_session_factory(factory: async_sessionmaker[AsyncSession]) -> None:
    """Set the DB session factory (called from app lifespan)."""
    global _session_factory  # noqa: PLW0603
    _session_factory = factory


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()


def get_llm_provider() -> LLMProvider:
    """Return an LLM provider instance."""
    return FakeLLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    """Return an embedding provider. Uses real OpenAI when key is available."""
    settings = get_settings()
    if settings.openai_api_key:
        from vectraxis.retrieval.embeddings import LangChainEmbeddingProvider

        return LangChainEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    return FakeEmbeddingProvider()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session."""
    if _session_factory is None:
        raise RuntimeError("DB session factory not initialized")
    async with _session_factory() as session:
        yield session


def get_data_source_registry() -> object:
    """Return the shared DataSourceRegistry singleton (legacy)."""
    from vectraxis.api.data_source_registry import DataSourceRegistry

    global _shared_data_source_registry  # noqa: PLW0603
    if _shared_data_source_registry is None:
        _shared_data_source_registry = DataSourceRegistry()
    return _shared_data_source_registry


def get_data_source_repo() -> DataSourceRepository:
    """Return a DataSourceRepository (in-memory fallback)."""
    if _session_factory is not None:
        # Will be overridden per-request via Depends(get_db_session)
        # For now, return in-memory as fallback
        pass
    global _shared_data_source_repo  # noqa: PLW0603
    if _shared_data_source_repo is None:
        _shared_data_source_repo = InMemoryDataSourceRepository()
    return _shared_data_source_repo


def get_prompt_repo() -> PromptRepository:
    """Return a PromptRepository."""
    global _shared_prompt_repo  # noqa: PLW0603
    if _shared_prompt_repo is None:
        _shared_prompt_repo = InMemoryPromptRepository()
    return _shared_prompt_repo


def get_workflow_repo() -> WorkflowRepository:
    """Return a WorkflowRepository."""
    global _shared_workflow_repo  # noqa: PLW0603
    if _shared_workflow_repo is None:
        _shared_workflow_repo = InMemoryWorkflowRepository()
    return _shared_workflow_repo


def get_retriever() -> RAGRetriever:
    """Return the shared RAGRetriever singleton."""
    global _shared_retriever  # noqa: PLW0603
    if _shared_retriever is None:
        chunker = RecursiveChunker()
        embedder = get_embedding_provider()
        store = InMemoryVectorStore()
        _shared_retriever = RAGRetriever(
            chunker=chunker, embedder=embedder, store=store
        )
    return _shared_retriever


def get_pipeline(llm: LLMProvider | None = None) -> Pipeline:
    """Build and return a Pipeline with all agents wired up.

    If llm is provided, uses it; otherwise falls back to FakeLLMProvider.
    """
    if llm is None:
        llm = get_llm_provider()
    agents: dict[AgentType, Agent] = {
        AgentType.ANALYSIS: AnalysisAgent(llm),
        AgentType.SUMMARIZATION: SummarizationAgent(llm),
        AgentType.RECOMMENDATION: RecommendationAgent(llm),
    }
    router = TaskRouter(agents)
    retriever = get_retriever()
    return Pipeline(router=router, retriever=retriever)
