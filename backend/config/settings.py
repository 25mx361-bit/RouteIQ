"""
settings.py — Application configuration loaded from environment / .env file.
All secrets and environment-specific values live in .env; never hard-code them.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from project root (two levels up: backend/config -> project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class BaseConfig:
    """Shared defaults across all environments."""

    # --- Application ---
    APP_NAME: str = "RouteIQ API"
    API_VERSION: str = "v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme-in-production")

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET", "changeme-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv("JWT_ACCESS_EXPIRES_MINUTES", "60"))  # minutes

    # --- MongoDB ---
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/routeiq")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "routeiq")

    # --- External APIs ---
    TOMTOM_API_KEY: str = os.getenv("TOMTOM_API_KEY", "")
    OPENROUTESERVICE_API_KEY: str = os.getenv("OPENROUTESERVICE_API_KEY", "")
    OPEN_METEO_BASE_URL: str = os.getenv(
        "OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast"
    )

    # --- CORS ---
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # --- ML model paths ---
    PATCHTST_MODEL_PATH: str = os.getenv(
        "PATCHTST_MODEL_PATH",
        str(PROJECT_ROOT / "ml" / "patchtst" / "models" / "patchtst_best.pt"),
    )
    CATBOOST_MODEL_PATH: str = os.getenv(
        "CATBOOST_MODEL_PATH",
        str(PROJECT_ROOT / "ml" / "catboost" / "models" / "catboost_best.cbm"),
    )

    # --- APScheduler ---
    SCHEDULER_API_ENABLED: bool = False
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kolkata")

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = PROJECT_ROOT / "logs"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(BaseConfig):
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/routeiq_test"
    MONGO_DB_NAME = "routeiq_test"
    LOG_LEVEL = "DEBUG"


# ---------------------------------------------------------------------------
# Factory — selects config class based on APP_ENV env variable
# ---------------------------------------------------------------------------
_config_map: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config() -> BaseConfig:
    """Return the appropriate config instance for the current APP_ENV."""
    env = os.getenv("APP_ENV", "development").lower()
    config_class = _config_map.get(env, DevelopmentConfig)
    return config_class()
