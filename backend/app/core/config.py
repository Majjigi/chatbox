"""
All app settings in one place.

`Settings` reads each value from an environment variable or from the `.env` file,
falling back to the default written here. The variable name is the field name in
UPPER CASE — e.g. `cors_origins` is read from `CORS_ORIGINS`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or a .env file."""

    app_name: str = "ChatBox API"
    version: str = "0.1.0"
    # Every URL starts with this, e.g. /api/health.
    api_prefix: str = "/api"
    # Websites allowed to call this API from the browser (the Angular dev server).
    cors_origins: list[str] = ["http://localhost:4200"]

    # --- AI models -------------------------------------------------------
    # A model with an empty API key still shows in the dropdown, greyed out.
    gemini_api_key: str = ""
    # "gemini-flash-latest" always points at Google's newest Flash model.
    gemini_model: str = "gemini-flash-latest"
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-5-5"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# One shared instance — other files do `from app.core.config import settings`.
settings = Settings()
