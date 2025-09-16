import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import Page, expect

from app.settings import settings

if TYPE_CHECKING:
  from flask.testing import FlaskClient
  from flask_socketio import SocketIOTestClient


def test_health(http_client: "FlaskClient") -> None:
  resp = http_client.get("/health")
  assert resp.status_code == HTTPStatus.NO_CONTENT
  assert resp.headers["x-status"] == "ok"


def assert_user_joined_room(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
  room: str,
) -> None:
  """Check if the user has successfully joined the specified room."""
  assert mock_session["room"] == room

  received = socket_client.get_received()

  # validate the 'status' event
  status_event = received[1]
  assert status_event["name"] == "status"
  assert status_event["args"][0]["type"] == "join"
  assert "timestamp" in status_event["args"][0]
  assert (
    f"{mock_session['username']} has joined the room."
    in status_event["args"][0]["text"]
  )

  # validate the 'chat_history' event
  chat_history_event = received[2]
  assert chat_history_event["name"] == "chat_history"
  assert chat_history_event["args"][0]["messages"] == []


def test_connect_to_chat(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  assert socket_client.is_connected()
  received = socket_client.get_received()[0]
  assert received["name"] == "online_users"
  assert "users" in received["args"][0]
  assert len(received["args"][0]["users"]) == 1
  assert mock_session["username"] in received["args"][0]["users"]
  assert mock_session["room"] == ""


def test_disconnect_from_chat(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  assert socket_client.is_connected()
  socket_client.disconnect()
  assert not socket_client.is_connected()
  assert not mock_session


def test_join_chat_room(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  assert socket_client.is_connected()
  room = settings.DEFAULT_CHAT_ROOM
  socket_client.emit("join", {"room": room})
  assert_user_joined_room(socket_client, mock_session, room)


def test_leave_chat_room(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  assert socket_client.is_connected()
  room = settings.DEFAULT_CHAT_ROOM
  socket_client.emit("join", {"room": room})
  assert_user_joined_room(socket_client, mock_session, room)
  socket_client.emit("leave", {"room": room})
  # make sure the current room was reset after leaving
  assert mock_session["room"] == ""


@pytest.mark.skip(reason="Not implemented")
def test_send_public_message(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  pass


@pytest.mark.skip(reason="Not implemented")
def test_send_private_message(
  socket_client: "SocketIOTestClient",
  mock_session: dict[str, str],
) -> None:
  pass


@pytest.mark.e2e
def test_open_index_page(page: Page) -> None:
  page.goto("/")
  expect(page).to_have_title(re.compile("Advanced Real-Time Chat"))
