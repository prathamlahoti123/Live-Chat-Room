import logging
import os
import secrets
from functools import lru_cache
from typing import ClassVar, TypedDict


class LoggingKwargs(TypedDict):
  """Kwargs for logger config."""

  level: int
  format: str
  datefmt: str


class SocketIOServerKwargs(TypedDict):
  """Kwargs for running SocketIO server."""

  host: str
  port: int
  debug: bool
  use_reloader: bool


class Settings:
  """Application configuration."""

  # Flask + SocketIO  settings
  DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
  CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
  FLASK_HOST: str = os.getenv("FLASK_HOST", "localhost")
  FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
  SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(24))

  # Logging settings
  LOG_NAME: str = "chat"
  LOG_LEVEL: int = logging.DEBUG if DEBUG else logging.WARNING
  LOG_FORMAT: str = "%(levelname)s - %(name)s - %(asctime)s - %(message)s"
  LOG_DATEFMT: str = "%Y-%m-%d %H:%M:%S"

  # Chat settings
  DEFAULT_CHAT_ROOM: str = "General"
  CHAT_ROOMS: ClassVar[list[str]] = [DEFAULT_CHAT_ROOM, "News", "Sport", "Engineering"]

  @property
  def logging_kwargs(self) -> LoggingKwargs:
    """Kwargs for logger config."""
    return LoggingKwargs(
      level=self.LOG_LEVEL,
      format=self.LOG_FORMAT,
      datefmt=self.LOG_DATEFMT,
    )

  @property
  def socketio_server_kwargs(self) -> SocketIOServerKwargs:
    """Kwargs for running SocketIO server."""
    return SocketIOServerKwargs(
      host=self.FLASK_HOST,
      port=self.FLASK_PORT,
      debug=self.DEBUG,
      use_reloader=self.DEBUG,
    )


@lru_cache
def get_settings() -> Settings:
  """Return cached project settings."""
  return Settings()


settings = get_settings()
