from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal


@dataclass
class User:
  """Schema to represent info about user."""

  username: str


@dataclass
class Message:
  """Base message interface."""

  text: str
  timestamp: float = field(
    default_factory=datetime.now(tz=UTC).timestamp,
    init=False,
  )


@dataclass
class StatusMessage(Message):
  """Schema to represent a chat join status message."""

  type: Literal["join", "leave"] = "join"


@dataclass
class PrivateMessage(Message):
  """Schema to represent info about private message."""

  sender: str
  receiver: str


@dataclass
class PublicMessage(Message):
  """Schema to represent info about public message."""

  username: str
  room: str
