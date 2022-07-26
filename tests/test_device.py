from app import models as m
from .mqtt import MqttTestClient


def test_register_device(mqtt: MqttTestClient):
    TEST_USER = "Test User Name"
    TEST_DEVICE_TYPE = "Test Type"
    TEST_DEVICE_NAME = "Test Device Name"

    user = m.User(
        username=TEST_USER,
        email="simple2b@test.com",
    ).save()
    account = m.Account(
        user_id=user.id,
        mqtt_login=TEST_USER,
        mqtt_password="no matter",
    ).save()

    mqtt.publish(topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}")
    account: m.Account = m.Account.query.get(account.id)
    assert account.devices
    device: m.Device = account.devices[0]
    assert device.name == TEST_DEVICE_NAME
    assert device.type == TEST_DEVICE_TYPE
