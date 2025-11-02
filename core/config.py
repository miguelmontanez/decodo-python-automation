from dataclasses import dataclass, asdict
from typing import Any, Dict

from config_supabase import load_remote_config


@dataclass
class Settings:
    """Runtime settings for the bot.

    Keep lightweight; users can extend as needed.
    """

    max_parallel_loaders: int = 4
    default_encoding: str = "utf-8"
    http_timeout_seconds: float = 30.0
    enable_quality_filter: bool = True


def _apply_overrides(settings: Settings, overrides: Dict[str, Any]) -> None:
    for key, value in overrides.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


settings = Settings()

# Optional: overlay remote config from Supabase if available
_overrides = load_remote_config()
if _overrides:
    _apply_overrides(settings, _overrides)


