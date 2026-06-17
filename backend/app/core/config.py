from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DClaw App"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_app"

    # Connection pool sizing. Defaults are tuned for a single backend process
    # serving ~1000 concurrent users while staying under Postgres' default
    # max_connections (100). pool_size persistent + max_overflow burst = 30 max.
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Response cache for GET endpoints. In-process TTL cache that shields the
    # database from agents re-querying the same list/detail endpoints.
    cache_enabled: bool = True
    cache_ttl_seconds: int = 30
    # Hard cap on cached responses held in memory (LRU eviction beyond this).
    cache_max_entries: int = 1000

    # Per-IP rate limiting. Strict limit on /api/v1/auth (brute-force / re-auth
    # protection), looser limit for the rest of /api/v1. /health is exempt.
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100
    auth_rate_limit_per_minute: int = 5
    # Hard cap on distinct clients tracked at once (LRU eviction beyond this).
    rate_limit_max_clients: int = 10000

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
