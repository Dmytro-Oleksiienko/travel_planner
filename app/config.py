"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Travel Planner API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./travel_planner.db"

    # Art Institute of Chicago API
    ARTIC_API_BASE_URL: str = "https://api.artic.edu/api/v1"
    ARTIC_API_TIMEOUT: int = 10  # seconds

    # Cache
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 100

    # Pagination
    DEFAULT_PAGE: int = 1
    DEFAULT_PER_PAGE: int = 10
    MAX_PER_PAGE: int = 100

    # Limits
    MAX_PLACES_PER_PROJECT: int = 10

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
