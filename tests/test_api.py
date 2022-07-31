from flask.testing import FlaskClient
from http import HTTPStatus
from .utils import login, register
from app.models import User
from app.controllers.account import create_account


TEST_CREDS = ("test_user", "test_password")
PAGE_AMOUNT = 4
ADDITIONAL_ACCOUNT_AMOUNT = 3


def test_get_accounts(client: FlaskClient):
    total_accounts_amount = client.application.config["PAGE_SIZE"] * PAGE_AMOUNT

    # test get page without login
    resp = client.get("/api/accounts")
    assert resp.status_code == HTTPStatus.FOUND.value

    # create new test user
    test_user_id = register(*TEST_CREDS)
    login(client, *TEST_CREDS)
    test_user = User.query.get(test_user_id)

    # no accounts test
    resp = client.get("/api/accounts")
    assert resp.status_code == HTTPStatus.OK.value
    assert resp.json
    assert "accounts" in resp.json
    assert "total" in resp.json
    assert not resp.json["accounts"]
    assert resp.json["total"] == 0

    # create accounts
    for i in range(total_accounts_amount):
        create_account(test_user)

    # create additional accounts for pagination test
    for i in range(ADDITIONAL_ACCOUNT_AMOUNT):
        create_account(test_user)

    # test pagination
    accounts_count = {}
    for page in range(1, PAGE_AMOUNT + 2):
        resp = client.get(f"/api/accounts?page={page}")
        assert resp.json["accounts"]
        print(len(resp.json["accounts"]))
        accounts_count |= resp.json["accounts"]

    assert len(accounts_count) == total_accounts_amount + ADDITIONAL_ACCOUNT_AMOUNT
    assert resp.json["total"] == total_accounts_amount + ADDITIONAL_ACCOUNT_AMOUNT
    resp = client.get(f"/api/accounts?page={PAGE_AMOUNT + 2}")
    assert resp.status_code == HTTPStatus.NOT_FOUND.value


def test_borker_info(client: FlaskClient):
    # login admin
    login(client)
    resp = client.get("/api/broker/info")
    assert resp.status_code == HTTPStatus.OK.value
    data = resp.json
    assert data

    assert "info" in data
    assert data["info"]

    assert "port" in data["info"]
    assert data["info"]["port"]
