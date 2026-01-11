"""Configuration management for ProjectX."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider (OpenRouter or OpenAI)
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"  # OpenRouter by default
    llm_model: str = "openai/gpt-4o-mini"  # OpenRouter model format
    
    # CrewAI model format (prefix with openrouter/ for CrewAI compatibility)
    crewai_model: str = "openrouter/openai/gpt-4o-mini"

    # CrewAI settings
    crewai_verbose: bool = False  # Set True for debugging agent execution
    crewai_max_retries: int = 3  # Max retries for agent failures

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

    # Telegram Bot
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""  # Optional secret for webhook verification

    # Database
    database_url: str = ""  # PostgreSQL connection string

    # Railway
    railway_public_url: str = ""  # Railway public URL for webhooks

    # App settings
    debug: bool = False
    app_name: str = "ProjectX"
    monitoring_paused: bool = False  # Pause email monitoring

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
