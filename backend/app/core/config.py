from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DClaw App"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_app"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    # Fleet Copilot LLM. Leave ollama_url blank to fall back to the deterministic
    # template responder (used by tests and when Ollama is unreachable).
    ollama_url: str = ""
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 30.0

    # Demo mode — when True, exposes public /api/v1/demo/* endpoints that
    # seed and tear down DEMO-* sample data for the landing page.
    # Leave False in production. Reset is scoped to records carrying the
    # DEMO- marker so real data cannot be touched even if the flag is on.
    enable_demo_mode: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
