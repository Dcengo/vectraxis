"""TDD tests for vectraxis.config module.

Tests define the API contract for:
- Settings class with environment variable support
"""

from vectraxis.config import Settings


class TestSettingsDefaults:
    """Tests for Settings default values."""

    def test_app_name_default(self):
        settings = Settings()
        assert settings.app_name == "Vectraxis"

    def test_debug_default(self):
        settings = Settings()
        assert settings.debug is False

    def test_database_url_default(self):
        settings = Settings()
        assert (
            settings.database_url
            == "postgresql+asyncpg://vectraxis:vectraxis@localhost:4343/vectraxis"
        )

    def test_openai_api_key_default(self):
        settings = Settings()
        assert settings.openai_api_key == ""

    def test_embedding_model_default(self):
        settings = Settings()
        assert settings.embedding_model == "text-embedding-3-small"

    def test_embedding_dimension_default(self):
        settings = Settings()
        assert settings.embedding_dimension == 1536

    def test_log_level_default(self):
        settings = Settings()
        assert settings.log_level == "INFO"


class TestSettingsTypes:
    """Tests for Settings field types."""

    def test_app_name_is_str(self):
        settings = Settings()
        assert isinstance(settings.app_name, str)

    def test_debug_is_bool(self):
        settings = Settings()
        assert isinstance(settings.debug, bool)

    def test_database_url_is_str(self):
        settings = Settings()
        assert isinstance(settings.database_url, str)

    def test_openai_api_key_is_str(self):
        settings = Settings()
        assert isinstance(settings.openai_api_key, str)

    def test_embedding_model_is_str(self):
        settings = Settings()
        assert isinstance(settings.embedding_model, str)

    def test_embedding_dimension_is_int(self):
        settings = Settings()
        assert isinstance(settings.embedding_dimension, int)

    def test_log_level_is_str(self):
        settings = Settings()
        assert isinstance(settings.log_level, str)


class TestSettingsEnvOverride:
    """Tests that VECTRAXIS_ prefixed env vars override defaults."""

    def test_app_name_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_APP_NAME", "MyApp")
        settings = Settings()
        assert settings.app_name == "MyApp"

    def test_debug_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_DEBUG", "true")
        settings = Settings()
        assert settings.debug is True

    def test_database_url_from_env(self, monkeypatch):
        monkeypatch.setenv(
            "VECTRAXIS_DATABASE_URL",
            "postgresql+asyncpg://user:pass@db:5432/mydb",
        )
        settings = Settings()
        assert settings.database_url == "postgresql+asyncpg://user:pass@db:5432/mydb"

    def test_openai_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_OPENAI_API_KEY", "sk-test-key-123")
        settings = Settings()
        assert settings.openai_api_key == "sk-test-key-123"

    def test_embedding_model_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_EMBEDDING_MODEL", "text-embedding-ada-002")
        settings = Settings()
        assert settings.embedding_model == "text-embedding-ada-002"

    def test_embedding_dimension_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_EMBEDDING_DIMENSION", "768")
        settings = Settings()
        assert settings.embedding_dimension == 768

    def test_log_level_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.log_level == "DEBUG"

    def test_debug_false_from_env(self, monkeypatch):
        monkeypatch.setenv("VECTRAXIS_DEBUG", "false")
        settings = Settings()
        assert settings.debug is False

    def test_env_prefix_is_vectraxis(self):
        """Settings should use VECTRAXIS_ as the env prefix."""
        config = Settings.model_config
        assert config.get("env_prefix") == "VECTRAXIS_"


class TestSettingsModelConfig:
    """Tests for Settings model_config."""

    def test_has_env_prefix(self):
        assert "env_prefix" in Settings.model_config

    def test_env_prefix_value(self):
        assert Settings.model_config["env_prefix"] == "VECTRAXIS_"
