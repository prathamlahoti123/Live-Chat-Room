from dataclasses import asdict
from typing import TYPE_CHECKING, TypedDict, cast

from flask import Flask, render_template, session
from flask import request as _request
from flask_socketio import SocketIO, emit, join_room, leave_room

from app.logger import logger
from app.schemas import PrivateMessage, PublicMessage, StatusMessage, User
from app.settings import Config
from app.utils import generate_guest_username

if TYPE_CHECKING:
  from flask import Request

  class SocketIORequest(Request):
    """Wrapper for flask.Request to provide sid attribute for type checking.

    See: https://github.com/miguelgrinberg/Flask-SocketIO/discussions/2085
    """

    sid: str


request = cast("SocketIORequest", _request)


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(
  app,
  cors_allowed_origins=app.config["CORS_ORIGINS"],
  logger=app.config["DEBUG"],
  engineio_logger=app.config["DEBUG"],
)


@socketio.on_error_default
def default_error_handler(e: BaseException) -> None:
  """Handle all namespaces without an explicit error handler."""
  logger.error("Websocket error: %s", str(e))


class DbType(TypedDict):
  """Data type specifying the application's database."""

  users: dict[str, User]
  rooms: list[str]


# In-memory storage
db: DbType = {"users": {}, "rooms": [*app.config["CHAT_ROOMS"]]}


@app.route("/")
def index() -> str:
  """Render index page, placing a random name of the user into session."""
  if "username" not in session:
    session["username"] = generate_guest_username()
    logger.info("New user session created: %s", session["username"])
  return render_template("index.html", username=session["username"], rooms=db["rooms"])


@socketio.event
def connect() -> None:
  """Handle websocket connect event."""
  if "username" not in session:
    session["username"] = generate_guest_username()
  if "room" not in session:
    session["room"] = app.config["CHAT_ROOMS"][0]
  user = User(session["username"])
  db["users"][request.sid] = user
  emit(
    "active_users",
    {"users": [user.username for user in db["users"].values()]},
    broadcast=True,
  )
  logger.info("User connected: %s", user.username)


@socketio.event
def disconnect(reason: str) -> None:
  """Handle websocket disconnect event."""
  if request.sid not in db["users"]:
    return
  username = db["users"][request.sid].username
  del db["users"][request.sid]
  emit(
    "active_users",
    {"users": [user.username for user in db["users"].values()]},
    broadcast=True,
  )
  logger.info("User disconnected: %s. Reason: %s", username, reason)


@socketio.event
def join(data: dict[str, str]) -> None:
  """Handle websocket room join event."""
  room = data["room"]
  if room not in db["rooms"]:
    logger.warning("Invalid room join attempt: %s", room)
    return
  username = session["username"]
  if room == session["room"]:
    logger.info("User %s room is already in %s room", username, room)
    return
  join_room(room)
  session["room"] = room
  message = StatusMessage(text=f"{username} has joined the room.")
  emit("status", asdict(message), to=room)
  logger.info("User %s joined room: %s", username, room)


@socketio.event
def leave(data: dict[str, str]) -> None:
  """Handle websocket room leave event."""
  username = session["username"]
  room = data["room"]
  leave_room(room)
  message = StatusMessage(text=f"{username} has left the room.", type="leave")
  emit("status", asdict(message), to=room)
  logger.info("User %s left room: %s", username, room)


@socketio.on("message")
def handle_message(data: dict[str, str]) -> None:
  """Handle custom websocket event of sending messages."""
  message = data.get("text", "").strip()
  if not message:
    return

  username = session["username"]
  msg_type = data.get("type", "message")

  if msg_type == "private":
    # Handle private messages
    target_user = data.get("receiver")
    if not target_user:
      return
    for sid, user in db["users"].items():
      if user.username == target_user:
        private_message = PrivateMessage(message, sender=username, receiver=target_user)
        emit("private_message", asdict(private_message), to=sid)
        logger.info("Private message sent: %s -> %s", username, target_user)
        return
    logger.warning("Private message failed - user not found: %", target_user)

  else:
    # Regular room message
    room = data.get("room", app.config["DEFAULT_CHAT_ROOM"])
    if room not in db["rooms"]:
      logger.warning("Message to invalid room: %s", room)
      return
    public_message = PublicMessage(message, username, room)
    emit("message", asdict(public_message), to=room)
    logger.info("Message sent in %s by %s", room, username)


if __name__ == "__main__":
  socketio.run(
    app,
    host=app.config["APP_HOST"],
    port=app.config["APP_PORT"],
    debug=app.config["DEBUG"],
    use_reloader=app.config["DEBUG"],
  )
