import requests


def mqtt_set_user(username: str, password: str):
    """add client to MQTT broker. If client already exists - reset password

    Args:
        username (str): client username
        password (str): client password

    Returns:
        _type_: None
    """
    from flask import current_app as app

    BASE_URL = (
        f"http://{app.config['MOSQUITTO_API_HOST']}:{app.config['MOSQUITTO_API_PORT']}"
    )
    res = requests.post(
        f"{BASE_URL}/user", json={"login": username, "password": password}
    )
    res.raise_for_status()


def mqtt_remove_user(username: str):
    """delete MQTT broker client account by username

    Args:
        username (str): client username
    """

    from flask import current_app as app

    BASE_URL = (
        f"http://{app.config['MOSQUITTO_API_HOST']}:{app.config['MOSQUITTO_API_PORT']}"
    )
    res = requests.delete(f"{BASE_URL}/user/{username}")
    res.raise_for_status()
