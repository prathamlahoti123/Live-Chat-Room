from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from flask.testing import FlaskClient


def test_health(http_client: "FlaskClient") -> None:
  resp = http_client.get("/health")
  assert resp.status_code == HTTPStatus.NO_CONTENT
  assert resp.headers["x-status"] == "ok"
