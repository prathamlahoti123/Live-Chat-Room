from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from app.main import app, socketio

if TYPE_CHECKING:
  from flask.testing import FlaskClient
  from flask_socketio import SocketIOTestClient


@pytest.fixture(scope="session")
def http_client() -> Iterator["FlaskClient"]:
  """Fixture to provide a Flask test client."""
  with app.test_client() as client:
    yield client


@pytest.fixture
def socket_client() -> "SocketIOTestClient":
  """Fixture to provide a Flask-SocketIO test client."""
  return socketio.test_client(app)


# @pytest.fixture(scope="session")
# def mock_session() -> Iterator[dict[str, str]]:
#   """Fixture to mock the Flask session."""
#   with patch("app.main.session", {}) as session:
#     yield session


# @pytest.fixture(scope="session")
# def monkeysession() -> Iterator[pytest.MonkeyPatch]:
#   """Session-scoped MonkeyPatch fixture."""
#   with pytest.MonkeyPatch.context() as mp:
#     yield mp


# @pytest.fixture(scope="session")
# def mock_session(monkeysession: pytest.MonkeyPatch) -> dict[str, str]:
#   """Fixture to mock the Flask session."""
#   session: dict[str, str] = {}
#   monkeysession.setattr("app.main.session", session)
#   return session


@pytest.fixture
def mock_session(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
  """Fixture to mock the Flask session."""
  session: dict[str, str] = {}
  monkeypatch.setattr("app.main.session", session)
  return session
