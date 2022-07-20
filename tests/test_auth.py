from flask.testing import FlaskClient
from tests.utils import login, logout
from app import mail
from app.models import User


def test_auth_pages(client):
    response = client.get("/register")
    assert response.status_code == 200
    response = client.get("/login")
    assert response.status_code == 200
    response = client.get("/logout")
    assert response.status_code == 302


def test_register(client: FlaskClient):
    EMAIL = "sam@test.com"
    with mail.record_messages() as outbox:
        response = client.post(
            "/register",
            data=dict(username="sam", email=EMAIL),
            follow_redirects=True,
        )
        assert (
            b"Registration successful. For reset password please check your e-mail."
            in response.data
        )
        # check email
        assert len(outbox) == 1
        letter = outbox[0]
        assert letter.subject == "New password"
        user: User = User.query.filter(User.email == EMAIL).first()
        assert user
        assert user.reset_password_uid
        PASS_URL = f"/password/{user.reset_password_uid}"
        assert PASS_URL in letter.html
        response = client.post(
            PASS_URL,
            data=dict(
                password="password",
                password_confirmation="password",
            ),
            follow_redirects=True,
        )
        assert b"Login successful." in response.data

    user: User = User.query.filter_by(email=EMAIL).first()
    assert user
    assert user.accounts


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
