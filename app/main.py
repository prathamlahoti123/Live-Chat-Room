from datetime import datetime

from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix

from app.logging import logger
from app.settings import Config
from app.utils import generate_guest_username

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Handle reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SocketIO with appropriate CORS settings
socketio = SocketIO(
  app,
  cors_allowed_origins=app.config["CORS_ORIGINS"],
  logger=True,
  engineio_logger=True,
)

# In-memory storage for active users
# In production, consider using Redis or another distributed storage
active_users: dict[str, dict] = {}


@app.route("/")
def index():
  if "username" not in session:
    session["username"] = generate_guest_username()
    logger.info(f"New user session created: {session['username']}")

  return render_template(
    "index.html", username=session["username"], rooms=app.config["CHAT_ROOMS"]
  )


@socketio.event
def connect():
  try:
    if "username" not in session:
      session["username"] = generate_guest_username()

    active_users[request.sid] = {
      "username": session["username"],
      "connected_at": datetime.now().isoformat(),
    }

    emit(
      "active_users",
      {"users": [user["username"] for user in active_users.values()]},
      broadcast=True,
    )

    logger.info(f"User connected: {session['username']}")

  except Exception as e:
    logger.error(f"Connection error: {str(e)}")
    return False


@socketio.event
def disconnect():
  try:
    if request.sid in active_users:
      username = active_users[request.sid]["username"]
      del active_users[request.sid]

      emit(
        "active_users",
        {"users": [user["username"] for user in active_users.values()]},
        broadcast=True,
      )

      logger.info(f"User disconnected: {username}")

  except Exception as e:
    logger.error(f"Disconnection error: {str(e)}")


@socketio.on("join")
def on_join(data: dict):
  try:
    username = session["username"]
    room = data["room"]

    if room not in app.config["CHAT_ROOMS"]:
      logger.warning(f"Invalid room join attempt: {room}")
      return

    join_room(room)
    active_users[request.sid]["room"] = room

    emit(
      "status",
      {
        "msg": f"{username} has joined the room.",
        "type": "join",
        "timestamp": datetime.now().isoformat(),
      },
      room=room,
    )

    logger.info(f"User {username} joined room: {room}")

  except Exception as e:
    logger.error(f"Join room error: {str(e)}")


@socketio.on("leave")
def on_leave(data: dict):
  try:
    username = session["username"]
    room = data["room"]

    leave_room(room)
    if request.sid in active_users:
      active_users[request.sid].pop("room", None)

    emit(
      "status",
      {
        "msg": f"{username} has left the room.",
        "type": "leave",
        "timestamp": datetime.now().isoformat(),
      },
      room=room,
    )

    logger.info(f"User {username} left room: {room}")

  except Exception as e:
    logger.error(f"Leave room error: {str(e)}")


@socketio.on("message")
def handle_message(data: dict):
  try:
    username = session["username"]
    room = data.get("room", "General")
    msg_type = data.get("type", "message")
    message = data.get("msg", "").strip()

    if not message:
      return

    timestamp = datetime.now().isoformat()

    if msg_type == "private":
      # Handle private messages
      target_user = data.get("target")
      if not target_user:
        return

      for sid, user_data in active_users.items():
        if user_data["username"] == target_user:
          emit(
            "private_message",
            {
              "msg": message,
              "from": username,
              "to": target_user,
              "timestamp": timestamp,
            },
            room=sid,
          )
          logger.info(f"Private message sent: {username} -> {target_user}")
          return

      logger.warning(f"Private message failed - user not found: {target_user}")

    else:
      # Regular room message
      if room not in app.config["CHAT_ROOMS"]:
        logger.warning(f"Message to invalid room: {room}")
        return

      emit(
        "message",
        {"msg": message, "username": username, "room": room, "timestamp": timestamp},
        room=room,
      )

      logger.info(f"Message sent in {room} by {username}")

  except Exception as e:
    logger.error(f"Message handling error: {str(e)}")


if __name__ == "__main__":
  # In production, use gunicorn or uwsgi instead
  socketio.run(
    app,
    host=app.config["HOST"],
    port=app.config["PORT"],
    debug=app.config["DEBUG"],
    use_reloader=app.config["DEBUG"],
  )
