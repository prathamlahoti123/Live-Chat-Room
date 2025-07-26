from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
  """Schema to represent info about user."""

  username: str
  connected_at: str = datetime.now().isoformat()
