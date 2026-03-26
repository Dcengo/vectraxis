"""Models and providers router."""

from fastapi import APIRouter
from pydantic import BaseModel

from vectraxis.agents.provider_registry import list_available_models, list_providers
from vectraxis.api.dependencies import get_settings

router = APIRouter()


class ModelResponse(BaseModel):
    """Response model for a single model entry."""

    model: str
    provider: str
    status: str


class ProviderResponse(BaseModel):
    """Response model for a single provider entry."""

    name: str
    status: str
    models: list[str]


@router.get(
    "/",
    response_model=list[ModelResponse],
    summary="List all models",
    description="Returns all known models with their provider and status "
    "(active if API key is configured, disabled otherwise).",
)
async def get_models() -> list[ModelResponse]:
    """List all available models."""
    settings = get_settings()
    models = list_available_models(settings)
    return [
        ModelResponse(model=m.model, provider=m.provider, status=m.status)
        for m in models
    ]


providers_router = APIRouter()


@providers_router.get(
    "/",
    response_model=list[ProviderResponse],
    summary="List all providers",
    description="Returns all LLM providers with their status and available models.",
)
async def get_providers() -> list[ProviderResponse]:
    """List all providers."""
    settings = get_settings()
    providers = list_providers(settings)
    return [
        ProviderResponse(name=p.name, status=p.status, models=p.models)
        for p in providers
    ]
