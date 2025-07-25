import os
import secrets


class Config:
  """Application configuration"""

  SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(24))
  DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
  CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
  HOST: str = os.getenv("HOST", "0.0.0.0")
  PORT: int = int(os.getenv("PORT", "5000"))

  # Available chat rooms - stored as constant for now, could be moved to database
  CHAT_ROOMS = ["General", "Zero to Knowing", "Code with Josh", "The Nerd Nook"]
