import secrets
from config import BaseConfig as conf
from app.models import Account
from app.logger import log
from app import models

LOGIN_LEN = 6


def gen_mqtt_login() -> str:
    """Generation of a account mqtt_login

    Returns:
        str: login value
    """
    ALPHABET = conf.ALPHABET_UP_DIGITS
    while True:
        mqtt_login = "".join(secrets.choice(ALPHABET) for i in range(LOGIN_LEN))
        if (
            mqtt_login[0].isdigit()
            and sum(c.isalpha() for c in mqtt_login) >= 3
            and sum(c.isdigit() for c in mqtt_login) >= 3
        ):
            if not Account.query.filter(Account.mqtt_login == mqtt_login).first():
                return mqtt_login


def gen_password(pass_length=7) -> str:
    """Generation of a password

    Returns:
        str: password value
    """
    alphabet = conf.ALPHABET_FULL
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(pass_length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 1
        ):
            return password


def create_account(user: models.User, mqtt_login: str = None, mqtt_password: str = None) -> Account:
    from .mqtt import mqtt_set_user

    if mqtt_login is None:
        mqtt_login = gen_mqtt_login()

    if mqtt_password is None:
        mqtt_password = gen_password()

    err = mqtt_set_user(mqtt_login, mqtt_password)
    if err != 0:
        log(log.ERROR, f"mqtt account creation failed: {err}. {user.username}: {mqtt_login}")
        return None

    account = Account(
        user_id=user.id,
        mqtt_login=mqtt_login,
        mqtt_password=mqtt_password,
    ).save()
    # register on MQTT broker
    log(
        log.INFO,
        "Register broker account %s:%s",
        account.mqtt_login,
        account.mqtt_password,
    )
    return account


def remove_account(account: Account) -> Account:
    from .mqtt import mqtt_remove_user

    log(
        log.INFO,
        "Delete broker account %s",
        account.mqtt_login,
    )
    mqtt_remove_user(account.mqtt_login)
    account.deleted = True
    account.save()
    return account
