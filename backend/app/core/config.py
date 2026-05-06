from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8139
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_fleet"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
