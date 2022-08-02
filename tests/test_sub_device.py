from app import models as m
from app.controllers.mqtt_client import BRIDGE_ITEMS
from app.models import Device, SubDevice
from .mqtt import MqttTestClient


def test_register_sub_device(mqtt: MqttTestClient):
    TEST_USER = "Test User Name"
    TEST_DEVICE_TYPE = "Test Type"
    TEST_DEVICE_NAME = "Test Device Name"
    TEST_SUB_DEVICE_NAME = "Test Sub Device Name"
    TEST_BRIDGE_ITEM = BRIDGE_ITEMS[0]

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
    assert not device.sub_devices
    device_id = device.id
    # publish sub device, but not publish bridge marker before
    mqtt.publish(
        topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}/{TEST_SUB_DEVICE_NAME}"
    )
    device: Device = Device.query.get(device_id)
    # check: sub device will be not registered
    assert not device.sub_devices
    # the device still not a bridge
    assert not device.is_bridge
    # publish bridge marker
    mqtt.publish(
        topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}/{TEST_BRIDGE_ITEM}"
    )
    device: Device = Device.query.get(device_id)
    # now device must be marked as bridge
    assert device.is_bridge
    # publish sub device
    mqtt.publish(
        topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}/{TEST_SUB_DEVICE_NAME}"
    )
    # ok - now device has sub device
    assert device.sub_devices
    sub_device: SubDevice = device.sub_devices[0]
    assert sub_device.name == TEST_SUB_DEVICE_NAME
