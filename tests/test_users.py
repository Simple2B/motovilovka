import pytest
from sqlalchemy import desc
from flask.testing import FlaskClient
from app import db, create_app
from app.controllers import init_db
from app.models import User
from .utils import login


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

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


def test_users_page(client: FlaskClient):
    response = client.get("/users")
    assert response.status_code == 302
    login(client)
    response = client.get("/users")
    assert response.status_code == 200
    assert b"Users" in response.data
    assert b"Role" in response.data
    assert b"Action" in response.data


def test_add_user(client: FlaskClient):
    login(client)
    TEST_USERNAME = "TEST_USERNAME"
    TEST_PASSWORD = "TEST_PASS"
    TEST_ROLE = 1

    res = client.post(
        "/user_add",
        data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            password_confirm=TEST_PASSWORD,
            role=TEST_ROLE,
        ),
        follow_redirects=True,
    )
    assert res.status_code == 200

    user: User = User.query.order_by(desc(User.id)).first()

    assert user.username == TEST_USERNAME


def test_user_delete(client: FlaskClient):
    login(client)
    response = client.get("/user_delete/10")
    assert response.status_code == 302
    user: User = User.query.get(10)
    assert user.deleted is True


def test_update_user(client: FlaskClient):
    login(client)
    TEST_USER_ID = 5
    TEST_USERNAME = "TEST_USERNAME"
    TEST_PASSWORD = "TEST_PASS"
    TEST_ROLE = 1

    res = client.post(
        f"/user_update/{TEST_USER_ID}",
        data=dict(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            password_confirm=TEST_PASSWORD,
            role=TEST_ROLE,
        ),
        follow_redirects=True,
    )
    assert res.status_code == 200

    user: User = User.query.filter_by(id=TEST_USER_ID).first()

    assert user.username == TEST_USERNAME
    assert user.role.value == TEST_ROLE


def test_user_search(client: FlaskClient):
    login(client)
    response = client.get("/user_search/r_2")
    assert b"r_2" in response.data

    response = client.get("/user_search/r_2, admin")
    assert b"r_2" in response.data
    assert b"admin" in response.data
