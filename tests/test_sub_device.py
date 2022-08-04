from flask.testing import FlaskClient
from app import models as m
from app.controllers.mqtt_client import BRIDGE_ITEMS
from app.models import Device, SubDevice
from .mqtt import MqttTestClient
from .utils import login


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


def test_rename_sub_device(mqtt: MqttTestClient):
    TEST_USER = "Test User Name"
    TEST_PASS = "pa@@ss894891934@@!eqf%"
    TEST_DEVICE_TYPE = "Test Type"
    TEST_DEVICE_NAME = "Test Device Name"
    TEST_SUB_DEVICE_ALIAS = "Test Device Alias"
    TEST_SUB_DEVICE_NAME = "Test Sub Device Name"
    TEST_BRIDGE_ITEM = BRIDGE_ITEMS[0]

    user = m.User(
        username=TEST_USER,
        email="simple2b@test.com",
        activated=True,
        password=TEST_PASS,
    ).save()
    account = m.Account(
        user_id=user.id,
        mqtt_login=TEST_USER,
        mqtt_password="no matter",
    ).save()

    mqtt.publish(topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}")
    # publish bridge marker
    mqtt.publish(
        topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}/{TEST_BRIDGE_ITEM}"
    )
    # publish sub device
    mqtt.publish(
        topic=f"{TEST_USER}/{TEST_DEVICE_TYPE}/{TEST_DEVICE_NAME}/{TEST_SUB_DEVICE_NAME}"
    )

    account: m.Account = m.Account.query.get(account.id)
    assert account.devices
    device: m.Device = account.devices[0]
    assert device.sub_devices
    sub_device: SubDevice = device.sub_devices[0]
    assert not sub_device.alias
    http: FlaskClient = mqtt.http_client
    login(http, TEST_USER, TEST_PASS)
    res = http.get(f"/sub_device_edit/{sub_device.uid}")
    assert res.status_code == 200

    res = http.post(
        f"/sub_device_edit/{sub_device.uid}",
        data=dict(
            name=TEST_SUB_DEVICE_ALIAS,
            uid=sub_device.uid,
            device_uid=device.id,
        ),
        follow_redirects=True,
    )
    assert res.status_code == 200
    device: m.Device = account.devices[0]
    assert device.sub_devices
    sub_device: SubDevice = device.sub_devices[0]
    assert sub_device.name == TEST_SUB_DEVICE_NAME
    assert sub_device.alias == TEST_SUB_DEVICE_ALIAS
