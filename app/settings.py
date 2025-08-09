import os
import secrets


class Config:
  """Application configuration"""

  APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
  APP_PORT: int = int(os.getenv("APP_PORT", "5000"))
  SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(24))
  DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
  CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

  # Available chat rooms - stored as constant for now, could be moved to database
  CHAT_ROOMS = ["General", "News", "Sport", "Engineering"]
