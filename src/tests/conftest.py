from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from app.main import app, socketio

if TYPE_CHECKING:
  from flask.testing import FlaskClient
  from flask_socketio import SocketIOTestClient


@pytest.fixture
def mock_session(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
  """Fixture to mock the Flask session object."""
  session: dict[str, str] = {}
  monkeypatch.setattr("app.main.session", session)
  return session


@pytest.fixture(scope="session")
def http_client() -> Iterator["FlaskClient"]:
  """Fixture to provide a Flask test client."""
  with app.test_client() as client:
    yield client


@pytest.fixture
def socket_client(
  mock_session: dict[str, str],  # noqa: ARG001
) -> Iterator["SocketIOTestClient"]:
  """Fixture to provide a Flask-SocketIO test client."""
  client = socketio.test_client(app)
  client.connect()
  yield client
  # in some tests we can disconnect the client explicitly
  if client.is_connected():
    client.disconnect()
