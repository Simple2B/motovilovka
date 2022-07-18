from app.models import User
from config import BaseConfig as conf

from app.controllers.database import TEST_PASS


def register(username, password=TEST_PASS):
    user = User(username=username, password=password)
    user.save()
    return user.id


def login(client, user_name=conf.ADMIN_USER, password=conf.ADMIN_PASS):
    res = client.post(
        "/login",
        data=dict(username=user_name, password=password),
        follow_redirects=True,
    )
    assert res.status_code == 200
    return res


def logout(client):
    return client.get("/logout", follow_redirects=True)
