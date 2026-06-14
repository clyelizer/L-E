"""Application configuration via Pydantic Settings."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "learnEnglish"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2
    log_level: str = "info"

    # Database
    database_url: str = "postgresql+asyncpg://learnenglish:learnenglish@localhost:5432/learnenglish"

    # JWT
    secret_key: str = "change-me-to-a-long-random-string-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_max_tokens: int = 500
    llm_temperature: float = 0.7

    # Image API
    image_api_provider: str = "openai"
    image_api_key: str = ""
    image_api_model: str = "dall-e-3"
    image_output_dir: str = ""

    # Feature flags
    enable_ai: bool = False
    cache_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent.parent

    @property
    def image_dir(self) -> Path:
        return Path(self.image_output_dir) if self.image_output_dir else self.project_root / "images"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
