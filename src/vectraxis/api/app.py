"""FastAPI application factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from vectraxis.api.routers import (
    chat,
    data_sources,
    evaluation,
    health,
    ingestion,
    models,
    pipelines,
    prompts,
    query,
    workflows,
)

logger = logging.getLogger(__name__)

SCALAR_HTML = """<!doctype html>
<html>
<head>
    <title>Vectraxis API - Scalar</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
    <script id="api-reference" data-url="{openapi_url}"></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialize DB session factory on startup."""
    try:
        from vectraxis.api.dependencies import set_session_factory
        from vectraxis.config import Settings
        from vectraxis.db.session import create_session_factory

        settings = Settings()
        factory = create_session_factory(settings)
        set_session_factory(factory)
        logger.info("DB session factory initialized")
    except Exception:
        logger.warning("DB session factory not initialized (DB may be unavailable)")
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Vectraxis API",
        version="0.1.0",
        description=(
            "Observable agentic AI pipelines for workflow "
            "intelligence and automation.\n\n"
            "## Documentation UIs\n"
            "- [Swagger UI](/docs) - Interactive API explorer\n"
            "- [Scalar](/scalar) - Modern API reference\n"
            "- [ReDoc](/redoc) - API documentation\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
    app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])
    app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["Pipelines"])
    app.include_router(
        evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"]
    )
    app.include_router(
        data_sources.router, prefix="/api/v1/data-sources", tags=["Data Sources"]
    )
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    app.include_router(models.router, prefix="/api/v1/models", tags=["Models"])
    app.include_router(
        models.providers_router, prefix="/api/v1/providers", tags=["Providers"]
    )
    app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["Prompts"])
    app.include_router(
        workflows.router, prefix="/api/v1/workflows", tags=["Workflows"]
    )

    @app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
    async def scalar_docs() -> str:
        return SCALAR_HTML.format(openapi_url=app.openapi_url)

    return app
