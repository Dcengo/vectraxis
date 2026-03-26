from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Vectraxis"
    debug: bool = False
    database_url: str = (
        "postgresql+asyncpg://vectraxis:vectraxis@localhost:4343/vectraxis"
    )
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    xai_api_key: str = ""
    default_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    log_level: str = "INFO"

    model_config = {
        "env_prefix": "VECTRAXIS_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }
