from flask import FlaskClient
from .utils import login


def test_device_page(client: FlaskClient):
    client.post()