from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://ccam:ccam_dev@localhost:5432/ccam"
    redis_url: str = "redis://localhost:6379/0"
    hmac_secret: str = "dev-secret-change-in-production"
    setup_token: str = "dev-setup-token-change-in-production"
    environment: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
