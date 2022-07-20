import datetime

from .utils import login

# from app.models import Account


def test_accounts_pages(client):
    response = client.get("/accounts")
    assert response.status_code == 302
    login(client, "user_2", "pass")
    response = client.get("/accounts")
    assert response.status_code == 200


def test_account_info(client):
    login(client, "user_2", "pass")
    response = client.get("/account_info/3")
    assert response.status_code == 200
    response = client.get("/account_info/3")
    assert b"Account Info" in response.data


def test_account_search(client):
    login(client)
    TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
    TEST_ACCOUNT_SEARCH_DATE = f"/account_search/{TODAY}"
    response = client.get(TEST_ACCOUNT_SEARCH_DATE)
    assert f"{TODAY}" in response.data.decode()
    response = client.get(f"/account_search/r_2, r_3, {TODAY}")
    assert "r_2" in response.data.decode()
    assert "r_3" in response.data.decode()
    assert f"{TODAY}" in response.data.decode()


def test_account_pagination(client):
    login(client)
    response = client.get("/account_search/8?page=2")
    assert b"8" in response.data
    response = client.get("/account_search/user_?page=7")
    assert b"user" in response.data
    response = client.get("/accounts?page=2")
    assert b"Accounts" in response.data
