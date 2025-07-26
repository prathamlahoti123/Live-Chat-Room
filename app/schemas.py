from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class User:
  """Schema to represent info about user."""

  username: str
  connected_at: str = datetime.now().isoformat()


@dataclass
class StatusMessage:
  """Schema to represent a chat join status message."""

  msg: str
  type: Literal["join", "leave"] = "join"
  timestamp: str = datetime.now().isoformat()


@dataclass
class PrivateMessage:
  """Schema to represent info about private message."""

  msg: str
  from_: str
  to: str
  timestamp: str = datetime.now().isoformat()
