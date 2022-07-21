import secrets
from config import BaseConfig as conf
from app.models import Account

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


def create_account(user_id: int) -> Account:
    account = Account(
        user_id=user_id,
        mqtt_login=gen_mqtt_login(),
        mqtt_password=gen_password(),
    ).save()
    # TODO: need register on broker!
    return account


def remove_account(account: Account) -> Account:
    account.deleted = True
    account.save()
    # TODO: provide solution for remove account from MQTT broker
    return account
