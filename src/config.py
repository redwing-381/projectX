"""Configuration management for ProjectX."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider (OpenRouter or OpenAI)
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"  # OpenRouter by default
    llm_model: str = "openai/gpt-4o-mini"  # OpenRouter model format

    # Gmail OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_credentials_path: str = "credentials.json"
    google_token_path: str = "token.json"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Alert destination (keypad phone)
    alert_phone_number: str = ""

    # App settings
    debug: bool = False
    app_name: str = "ProjectX"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
