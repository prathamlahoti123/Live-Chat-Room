from dataclasses import asdict

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from utils import generate_guest_username
from werkzeug.middleware.proxy_fix import ProxyFix

from app.logger import logger
from app.schemas import PrivateMessage, PublicMessage, StatusMessage, User
from app.settings import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Handle reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SocketIO with appropriate CORS settings
socketio = SocketIO(
  app,
  cors_allowed_origins=app.config["CORS_ORIGINS"],
  # logger=True,
  # engineio_logger=True,
)


@socketio.on_error_default
def default_error_handler(e: Exception) -> None:
  """Handle all namespaces without an explicit error handler."""
  logger.error("Websocket error: %s", str(e))


# In-memory storage
db: dict[str, dict] = {"users": {}, "rooms": [*app.config["CHAT_ROOMS"]]}


@app.route("/")
def index() -> str:
  if "username" not in session:
    session["username"] = generate_guest_username()
    logger.info("New user session created: %s", session["username"])
  return render_template("index.html", username=session["username"], rooms=db["rooms"])


@socketio.event
def connect() -> None:
  if "username" not in session:
    session["username"] = generate_guest_username()
  user = User(username=session["username"])
  db["users"][request.sid] = asdict(user)
  emit(
    "active_users",
    {"users": [user["username"] for user in db["users"].values()]},
    broadcast=True,
  )
  logger.info("User connected: %s", user.username)


@socketio.event
def disconnect(reason: str) -> None:
  if request.sid not in db["users"]:
    return
  username = db["users"][request.sid]["username"]
  del db["users"][request.sid]
  emit(
    "active_users",
    {"users": [user["username"] for user in db["users"].values()]},
    broadcast=True,
  )
  logger.info("User disconnected: %s. Reason: %s", username, reason)


@socketio.event
def join(data: dict) -> None:
  room = data["room"]
  if room not in db["rooms"]:
    logger.warning(f"Invalid room join attempt: {room}")
    return
  join_room(room)
  db["users"][request.sid]["room"] = room
  username = session["username"]
  message = StatusMessage(msg=f"{username} has joined the room.")
  emit("status", asdict(message), room=room)
  logger.info("User %s joined room: %s", username, room)


@socketio.event
def leave(data: dict) -> None:
  username = session["username"]
  room = data["room"]
  leave_room(room)
  if request.sid in db["users"]:
    db["users"][request.sid].pop("room", None)
  message = StatusMessage(msg=f"{username} has left the room.", type="leave")
  emit("status", asdict(message), room=room)
  logger.info("User %s left room: %s", username, room)


@socketio.on("message")
def handle_message(data: dict) -> None:
  message = data.get("msg", "").strip()
  if not message:
    return

  username = session["username"]
  msg_type = data.get("type", "message")

  if msg_type == "private":
    # Handle private messages
    target_user = data.get("target")
    if not target_user:
      return
    for sid, user_data in db["users"].items():
      if user_data["username"] == target_user:
        private_message = PrivateMessage(msg=message, from_=username, to=target_user)
        emit("private_message", asdict(private_message), room=sid)
        logger.info("Private message sent: %s -> %s", username, target_user)
        return
    logger.warning("Private message failed - user not found: %", target_user)

  else:
    # Regular room message
    room = data.get("room", "General")
    if room not in db["rooms"]:
      logger.warning("Message to invalid room: %s", room)
      return
    public_message = PublicMessage(msg=message, username=username, room=room)
    emit("message", asdict(public_message), room=room)
    logger.info("Message sent in %s by %s", room, username)


if __name__ == "__main__":
  # In production, use gunicorn or uwsgi instead
  socketio.run(
    app,
    host=app.config["HOST"],
    port=app.config["PORT"],
    debug=app.config["DEBUG"],
    use_reloader=app.config["DEBUG"],
  )
