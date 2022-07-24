import os
from flask import current_app as app
from app import db, models as m
from app.logger import log
from .account import gen_mqtt_login, gen_password, create_account

TEST_USERS_NUMBER = int(os.environ.get("TEST_USERS_NUMBER", "10"))
TEST_NUMBER_DEVICE_PER_USER = int(os.environ.get("TEST_NUMBER_DEVICE_PER_USER", "10"))
TEST_PASS = "pass"


def init_db(add_test_data: bool = False):
    """fill database by initial data

    Args:
        add_test_data (bool, optional): will add test data if set True. Defaults to False.
    """
    # Create admin
    log(log.INFO, "Add admin account: %s", app.config["ADMIN_USER"])
    admin = m.User(
        username=app.config["ADMIN_USER"],
        password=app.config["ADMIN_PASS"],
        email=app.config["ADMIN_EMAIL"],
        role="admin",
    ).save()
    create_account(admin, "admin", app.config["MOSQUITTO_ADMIN_PASSWORD"])

    if add_test_data:
        log(log.INFO, "Generate test data")
        for i in range(TEST_USERS_NUMBER):
            user = m.User(
                username=f"user_{i+1}",
                password=TEST_PASS,
                email=f"user_{i+1}@test.com",
            ).save()
            account = m.Account(
                user_id=user.id,
                mqtt_login=gen_mqtt_login(),
                mqtt_password=gen_password(),
            ).save()
            for j in range(TEST_NUMBER_DEVICE_PER_USER):
                m.Device(
                    account_id=account.id,
                    type="test",
                    name=f"dev.{user.username}.{j}",
                ).save(False)

    db.session.commit()
