from tests.utils import login, logout


def test_auth_pages(client):
    response = client.get("/login")
    assert response.status_code == 200
    response = client.get("/logout")
    assert response.status_code == 302


def test_login_and_logout(client):
    # Access to logout view before login should fail.
    response = logout(client)
    assert b"Please log in to access this page." in response.data
    response = login(client)
    assert b"Users" in response.data
    # Should successfully logout the currently logged in user.
    response = logout(client)
    assert b"Please log in to access this page." in response.data
    # Correct credentials should login
    response = login(client)
    assert b"You are successfully logged in!" in response.data
