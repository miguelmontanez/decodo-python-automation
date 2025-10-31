import contextlib
import logging
from typing import Optional


def get_logger(name: str = "training_data_bot") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class LogContext(contextlib.AbstractContextManager):
    """Lightweight logging context to enrich messages with operation info."""

    def __init__(self, operation: str, **fields):
        self.operation = operation
        self.fields = fields
        self._logger: Optional[logging.Logger] = None

    def __enter__(self):
        self._logger = get_logger()
        self._logger.debug(f"enter {self.operation} | {self.fields}")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._logger:
            if exc:
                self._logger.error(
                    f"error {self.operation} | {self.fields} | {exc}")
            else:
                self._logger.debug(f"exit {self.operation} | {self.fields}")
        return False


