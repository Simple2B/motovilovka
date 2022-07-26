import pytest
from flask.testing import FlaskClient
from app import create_app, db
from app.controllers import init_db
from .mqtt import MqttTestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> FlaskClient:
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    def dummy(*args, **argv):
        error = 0
        return error

    from app.controllers import mqtt

    monkeypatch.setattr(mqtt, "mqtt_set_user", dummy)
    monkeypatch.setattr(mqtt, "mqtt_remove_user", dummy)

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        init_db(True)
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


@pytest.fixture
def mqtt(client: FlaskClient) -> MqttTestClient:
    mqtt_client = MqttTestClient()
    mqtt_client.http_client = client
    yield mqtt_client
