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


@pytest.fixture(scope="session")
def socket_client(http_client: "FlaskClient") -> "SocketIOTestClient":
  """Fixture to provide a Flask-SocketIO test client."""
  return socketio.test_client(app, flask_test_client=http_client)
