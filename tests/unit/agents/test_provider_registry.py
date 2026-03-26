"""Tests for the provider registry."""

from vectraxis.agents.provider_registry import (
    MODEL_CATALOG,
    PROVIDER_KEY_FIELDS,
    list_available_models,
    list_model_ids,
    list_providers,
)
from vectraxis.config import Settings


class TestModelCatalog:
    """Tests for the model catalog constants."""

    def test_has_openai_provider(self):
        assert "openai" in MODEL_CATALOG

    def test_has_anthropic_provider(self):
        assert "anthropic" in MODEL_CATALOG

    def test_has_xai_provider(self):
        assert "xai" in MODEL_CATALOG

    def test_openai_has_gpt4o(self):
        assert "gpt-4o" in MODEL_CATALOG["openai"]

    def test_openai_has_gpt4o_mini(self):
        assert "gpt-4o-mini" in MODEL_CATALOG["openai"]

    def test_anthropic_has_claude_sonnet(self):
        assert "claude-sonnet-4-20250514" in MODEL_CATALOG["anthropic"]

    def test_xai_has_grok2(self):
        assert "grok-2" in MODEL_CATALOG["xai"]


class TestProviderKeyFields:
    """Tests for provider key field mapping."""

    def test_openai_key_field(self):
        assert PROVIDER_KEY_FIELDS["openai"] == "openai_api_key"

    def test_anthropic_key_field(self):
        assert PROVIDER_KEY_FIELDS["anthropic"] == "anthropic_api_key"

    def test_xai_key_field(self):
        assert PROVIDER_KEY_FIELDS["xai"] == "xai_api_key"


class TestListModelIds:
    """Tests for list_model_ids."""

    def test_returns_list(self):
        assert isinstance(list_model_ids(), list)

    def test_contains_all_models(self):
        ids = list_model_ids()
        total = sum(len(models) for models in MODEL_CATALOG.values())
        assert len(ids) == total

    def test_contains_gpt4o(self):
        assert "gpt-4o" in list_model_ids()


class TestListAvailableModels:
    """Tests for list_available_models."""

    def test_returns_all_models(self):
        settings = Settings()
        models = list_available_models(settings)
        total = sum(len(m) for m in MODEL_CATALOG.values())
        assert len(models) == total

    def test_all_disabled_without_keys(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_XAI_API_KEY", "")
        settings = Settings()
        models = list_available_models(settings)
        assert all(m.status == "disabled" for m in models)

    def test_openai_active_with_key(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_XAI_API_KEY", "")
        settings = Settings()
        models = list_available_models(settings)
        openai_models = [m for m in models if m.provider == "openai"]
        assert all(m.status == "active" for m in openai_models)

    def test_other_providers_still_disabled(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_XAI_API_KEY", "")
        settings = Settings()
        models = list_available_models(settings)
        non_openai = [m for m in models if m.provider != "openai"]
        assert all(m.status == "disabled" for m in non_openai)

    def test_model_has_provider_field(self):
        settings = Settings()
        models = list_available_models(settings)
        for m in models:
            assert m.provider in MODEL_CATALOG

    def test_model_has_model_field(self):
        settings = Settings()
        models = list_available_models(settings)
        for m in models:
            assert m.model in list_model_ids()


class TestListProviders:
    """Tests for list_providers."""

    def test_returns_three_providers(self):
        settings = Settings()
        providers = list_providers(settings)
        assert len(providers) == 3

    def test_provider_names(self):
        settings = Settings()
        providers = list_providers(settings)
        names = {p.name for p in providers}
        assert names == {"openai", "anthropic", "xai"}

    def test_all_disabled_without_keys(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "")
        monkeypatch.setenv("VECTRAXIS_XAI_API_KEY", "")
        settings = Settings()
        providers = list_providers(settings)
        assert all(p.status == "disabled" for p in providers)

    def test_provider_active_with_key(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_ANTHROPIC_API_KEY", "sk-ant-test")
        settings = Settings()
        providers = list_providers(settings)
        anthropic = next(p for p in providers if p.name == "anthropic")
        assert anthropic.status == "active"

    def test_provider_has_models(self):
        settings = Settings()
        providers = list_providers(settings)
        for p in providers:
            assert len(p.models) > 0
            assert p.models == MODEL_CATALOG[p.name]


class TestGetProviderForModel:
    """Tests for get_provider_for_model."""

    def test_unknown_model_raises(self):
        import pytest

        from vectraxis.agents.provider_registry import get_provider_for_model

        settings = Settings()
        with pytest.raises(ValueError, match="Unknown model"):
            get_provider_for_model("nonexistent-model", settings)

    def test_missing_key_raises(self):
        import pytest

        from vectraxis.agents.provider_registry import get_provider_for_model

        settings = Settings()
        with pytest.raises(ValueError, match="API key not configured"):
            get_provider_for_model("gpt-4o", settings)
