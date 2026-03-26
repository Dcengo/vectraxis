# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Dev Commands

```bash
# Package manager: uv (not pip)
uv sync --all-extras              # Install all deps including dev
uv run pytest tests/unit -v       # Run unit tests
uv run pytest tests/unit/agents/test_base.py -v          # Single test file
uv run pytest tests/unit/agents/test_base.py::TestClass::test_method  # Single test
uv run pytest tests/integration -m integration           # Integration tests (needs DB)
uv run ruff check .               # Lint
uv run ruff format .              # Format
uv run mypy src/                  # Type check (strict mode, pydantic plugin)

# Docker
docker compose -f docker/docker-compose.yml up -d --build   # Start backend + DB
docker compose -f docker/docker-compose.yml down             # Stop

# Frontend (pnpm)
cd frontend && pnpm install && pnpm dev   # Dev server on :3000, proxies /api to :8000
```

## Architecture

**Protocol-driven design**: All major components define `@runtime_checkable` Protocol classes with fake implementations for testing. Real implementations use LangChain wrappers.

### Request Flow

```
POST /api/v1/query/ → dependencies.get_pipeline(llm)
  → Pipeline.run(query, agent_type)
    1. TaskRouter.route(task) → specialized Agent
    2. RAGRetriever.retrieve(query) → context chunks
    3. Agent.execute(task, context) → AgentResult
    4. Optional: Validator.validate(result, context)
```

### Key Protocols & Their Implementations

| Protocol | Fake (tests) | Real |
|----------|-------------|------|
| `LLMProvider` (agents/base.py) | `FakeLLMProvider` | `LangChainLLMProvider` (agents/llm_providers.py) |
| `EmbeddingProvider` (retrieval/embeddings.py) | `FakeEmbeddingProvider` | `LangChainEmbeddingProvider` |
| `Agent` (agents/base.py) | — | `AnalysisAgent`, `SummarizationAgent`, `RecommendationAgent` |
| `Chunker` (retrieval/chunking.py) | — | `FixedSizeChunker`, `RecursiveChunker` |
| `VectorStore` (retrieval/vector_store.py) | `InMemoryVectorStore` | — |
| `Validator` (validation/validators.py) | — | `StructureValidator`, `FaithfulnessValidator` |
| `Loader` (ingestion/loaders.py) | — | `CSVLoader`, `JSONLoader`, `TextDocumentLoader` |

### Multi-Provider LLM Support

`agents/provider_registry.py` manages a model catalog (OpenAI, Anthropic, xAI). `get_provider_for_model(model, settings)` creates the right LangChain wrapper based on model name. Falls back to `FakeLLMProvider` when no API keys are set — all tests run without keys.

### Dependency Injection

`api/dependencies.py` wires everything. Key pattern: `_shared_retriever` singleton persists indexed documents across requests. `get_pipeline(llm=None)` accepts optional LLM; defaults to fake.

### Ingestion Pipeline

Upload → temp file → `LoaderRegistry` detects type by extension → `Loader.load()` → `WorkflowNormalizer.normalize()` → `Document` objects → `RAGRetriever.index()` (chunk → embed → store)

## Configuration

`config.py` uses pydantic-settings with `VECTRAXIS_` env prefix and `.env` file loading. Key fields: `openai_api_key`, `anthropic_api_key`, `xai_api_key`, `default_model`. All default to empty/fake — no keys required for tests.

## Database

PostgreSQL 16 + pgvector. Docker maps host port **4343** → container 5432. Internal docker-compose URLs use `@db:5432` (container network). Alembic for migrations.

## Security

- **NEVER read, print, log, or display the contents of `.env` files** — they contain API keys and secrets.
- **NEVER commit `.env` files** to version control.
- When debugging configuration issues, check environment variable names, not their values.

## Code Style

- Ruff rules: E, F, I, N, UP, B, SIM, TCH. Line length 88. Double quotes.
- MyPy strict mode with pydantic plugin.
- All models extend `VectraxisModel` (Pydantic BaseModel with `from_attributes=True`).
- `from __future__ import annotations` used in modules with circular TYPE_CHECKING imports.
