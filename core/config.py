from dataclasses import dataclass


@dataclass
class Settings:
    """Runtime settings for the bot.

    Keep lightweight; users can extend as needed.
    """

    max_parallel_loaders: int = 4
    default_encoding: str = "utf-8"
    http_timeout_seconds: float = 30.0
    enable_quality_filter: bool = True


settings = Settings()


