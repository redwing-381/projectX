"""Configuration management for ProjectX CLI."""

import json
from pathlib import Path
from pydantic import BaseModel, Field


CONFIG_DIR = Path.home() / ".projectx"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_SERVER_URL = "https://projectx-production-0eeb.up.railway.app"


class CLIConfig(BaseModel):
    """CLI configuration model."""
    server_url: str = Field(default=DEFAULT_SERVER_URL)


def load_config() -> CLIConfig:
    """Load configuration from file or return defaults."""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return CLIConfig(**data)
        except (json.JSONDecodeError, ValueError):
            return CLIConfig()
    return CLIConfig()


def save_config(config: CLIConfig) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(config.model_dump_json(indent=2))


def get_server_url() -> str:
    """Get the configured server URL."""
    return load_config().server_url


def set_server_url(url: str) -> None:
    """Set the server URL in configuration."""
    config = load_config()
    config.server_url = url.rstrip("/")
    save_config(config)
