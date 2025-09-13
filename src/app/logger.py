import logging
from functools import lru_cache

from app.settings import settings


@lru_cache
def configure_logging() -> logging.Logger:
  """Configure the root logger."""
  logging.basicConfig(**settings.logging_kwargs)
  return logging.getLogger(settings.LOG_NAME)


logger = configure_logging()
