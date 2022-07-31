from sqlalchemy import desc
from flask.testing import FlaskClient
from app.models import User, Account
from .utils import login


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
    TEST_EMAIL = "email@test.com"
    TEST_ROLE = 1

    res = client.post(
        "/user_add",
        data=dict(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            password_confirm=TEST_PASSWORD,
            role=TEST_ROLE,
        ),
        follow_redirects=True,
    )
    assert res.status_code == 200

    user: User = User.query.order_by(desc(User.id)).first()

    assert user.username == TEST_USERNAME

    # check if created account for this user
    account: Account = Account.query.filter_by(user_id=user.id).first()
    assert account
    assert account.user.username == TEST_USERNAME
    assert account.mqtt_login
    assert account.mqtt_password


def test_user_delete(client: FlaskClient):
    login(client)
    TEST_USER_ID = 2
    user: User = User.query.get(TEST_USER_ID)
    assert user
    assert user.deleted is False
    response = client.get(f"/user_delete/{TEST_USER_ID}")
    assert response.status_code == 302
    user: User = User.query.get(TEST_USER_ID)
    assert user.deleted is True
    accounts: list[Account] = Account.query.filter_by(user_id=TEST_USER_ID).all()
    for acc in accounts:
        assert acc.deleted


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


def test_update_user_empty_pass(client: FlaskClient):
    login(client)
    TEST_USER_ID = 5
    TEST_USERNAME = "TEST_USERNAME"
    TEST_ROLE = 1

    res = client.post(
        f"/user_update/{TEST_USER_ID}",
        data=dict(
            username=TEST_USERNAME,
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
