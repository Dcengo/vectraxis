"""Provider registry: model catalog, provider info, and factory functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from vectraxis.agents.llm_providers import LangChainLLMProvider

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel

    from vectraxis.config import Settings


@dataclass
class ModelInfo:
    """Information about a single model."""

    model: str
    provider: str
    status: str  # "active" or "disabled"


@dataclass
class ProviderInfo:
    """Information about a provider and its models."""

    name: str
    status: str  # "active" or "disabled"
    models: list[str] = field(default_factory=list)


# Model catalog: provider -> list of model IDs
MODEL_CATALOG: dict[str, list[str]] = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o3-mini"],
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-haiku-4-20250514",
    ],
    "xai": ["grok-2", "grok-2-mini"],
}

# Maps provider name to the Settings field for its API key
PROVIDER_KEY_FIELDS: dict[str, str] = {
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
    "xai": "xai_api_key",
}


def _provider_for_model(model: str) -> str | None:
    """Return the provider name for a given model ID, or None."""
    for provider, models in MODEL_CATALOG.items():
        if model in models:
            return provider
    return None


def _is_provider_active(provider: str, settings: Settings) -> bool:
    """Check if a provider has an API key configured."""
    key_field = PROVIDER_KEY_FIELDS.get(provider, "")
    return bool(getattr(settings, key_field, ""))


def get_provider_for_model(model: str, settings: Settings) -> LangChainLLMProvider:
    """Create a LangChainLLMProvider for the given model name.

    Raises ValueError if the model is unknown or the provider's API key is not set.
    """
    provider = _provider_for_model(model)
    if provider is None:
        msg = f"Unknown model: {model}. Available models: {list_model_ids()}"
        raise ValueError(msg)

    key_field = PROVIDER_KEY_FIELDS[provider]
    api_key = getattr(settings, key_field, "")
    if not api_key:
        env_var = f"VECTRAXIS_{key_field.upper()}"
        msg = f"API key not configured for provider '{provider}'. Set {env_var} in .env"
        raise ValueError(msg)

    chat_model: BaseChatModel
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        chat_model = ChatOpenAI(model=model, api_key=api_key)
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        chat_model = ChatAnthropic(model=model, api_key=api_key)
    elif provider == "xai":
        from langchain_xai import ChatXAI

        chat_model = ChatXAI(model=model, api_key=api_key)
    else:
        msg = f"Unsupported provider: {provider}"
        raise ValueError(msg)

    return LangChainLLMProvider(chat_model=chat_model, model_name=model)


def list_model_ids() -> list[str]:
    """Return a flat list of all known model IDs."""
    return [model for models in MODEL_CATALOG.values() for model in models]


def list_available_models(settings: Settings) -> list[ModelInfo]:
    """Return all models with their provider and status (active if key set)."""
    result: list[ModelInfo] = []
    for provider, models in MODEL_CATALOG.items():
        active = _is_provider_active(provider, settings)
        status = "active" if active else "disabled"
        for model in models:
            result.append(ModelInfo(model=model, provider=provider, status=status))
    return result


def list_providers(settings: Settings) -> list[ProviderInfo]:
    """Return all providers with status and their model list."""
    result: list[ProviderInfo] = []
    for provider, models in MODEL_CATALOG.items():
        active = _is_provider_active(provider, settings)
        status = "active" if active else "disabled"
        result.append(ProviderInfo(name=provider, status=status, models=list(models)))
    return result
