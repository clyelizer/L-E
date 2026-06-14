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

    # ── AI — LLM Providers ──────────────────────────────────────
    enable_ai: bool = False

    # LLM provider priority chain (comma-separated)
    llm_providers: str = "deepseek,gemini"
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.7

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # Gemini
    gemini_api_key: str = ""
    gemini_llm_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash"

    # ── AI — Image Providers ────────────────────────────────────
    # Image provider priority chain (comma-separated)
    image_providers: str = "gemini,flux"
    image_output_dir: str = ""

    # Flux Schnell (via Together AI)
    together_api_key: str = ""
    flux_model: str = "flux-schnell"

    # ── Feature flags ───────────────────────────────────────────
    cache_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"

    # Paths
    project_root: Path = Path(__file__).resolve().parent.parent.parent

    @property
    def image_dir(self) -> Path:
        return Path(self.image_output_dir) if self.image_output_dir else self.project_root / "images"

    @property
    def llm_provider_list(self) -> list[str]:
        return [p.strip() for p in self.llm_providers.split(",") if p.strip()]

    @property
    def image_provider_list(self) -> list[str]:
        return [p.strip() for p in self.image_providers.split(",") if p.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
