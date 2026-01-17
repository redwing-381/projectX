"""Configuration management for ProjectX."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import time


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

    # Database
    database_url: str = ""  # PostgreSQL connection string

    # Railway
    railway_public_url: str = ""  # Railway public URL for webhooks

    # App settings
    debug: bool = False
    app_name: str = "ProjectX"
    monitoring_paused: bool = False  # Pause email monitoring
    
    # API Authentication
    api_key: str = ""  # Secret key for CLI authentication

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# =============================================================================
# Simple In-Memory Cache for Database Queries
# =============================================================================

class SimpleCache:
    """Simple TTL cache for reducing database queries."""
    
    def __init__(self, default_ttl: int = 30):
        self._cache: dict = {}
        self._timestamps: dict = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
        if time.time() - self._timestamps.get(key, 0) > self._default_ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        return self._cache[key]
    
    def set(self, key: str, value: any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def invalidate(self, key: str) -> None:
        """Remove key from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._timestamps.clear()


# Global cache instance (30 second TTL for dashboard stats)
cache = SimpleCache(default_ttl=30)
