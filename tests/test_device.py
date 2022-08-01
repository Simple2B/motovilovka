from flask.testing import FlaskClient
from app import models as m
from .mqtt import MqttTestClient
from .utils import login, logout


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


def test_show_devices(mqtt: MqttTestClient):
    http: FlaskClient = mqtt.http_client
    TEST_USER = "Test_User_{i}"
    TEST_DEVICE_TYPE = "test_lamp"
    TEST_DEVICE_NAME = "Test Device Name {i}"

    TEST_USER_COUNT = 2
    TEST_DEVICE_COUNT = 5
    TEST_PASSWORD = "pass"
    TEST_ROLE = 2

    # login as admin
    login(http)

    # add users
    user_count_before = m.User.query.count()
    for user_i in range(TEST_USER_COUNT):
        username = TEST_USER.format(i=user_i)
        email = username + "@test.com"
        res = http.post(
            "/user_add",
            data=dict(
                username=username,
                email=email,
                password=TEST_PASSWORD,
                password_confirm=TEST_PASSWORD,
                role=TEST_ROLE,
            ),
            follow_redirects=True,
        )
        assert res.status_code == 200

    assert m.User.query.count() - user_count_before == TEST_USER_COUNT

    # logout by admin
    logout(http)

    device_count_before = m.Device.query.count()
    users: list[m.User] = m.User.query.all()[-TEST_USER_COUNT:]
    # add devices to users
    for user in users:
        user: m.User = user
        assert user.accounts
        account: m.Account = user.accounts[0]
        for device_i in range(TEST_DEVICE_COUNT):
            device_name = TEST_DEVICE_NAME.format(i=device_i)
            topic = f"{account.mqtt_login}/{TEST_DEVICE_TYPE}/{device_name}"
            mqtt.publish(topic=topic)

    assert (m.Device.query.count() - device_count_before) == (
        TEST_USER_COUNT * TEST_DEVICE_COUNT
    )

    # login user by user and show
    for user in users:
        login(http, user.username, TEST_PASSWORD)
        res = http.get("/devices")
        assert res.status_code == 200
        for device_i in range(TEST_DEVICE_COUNT):
            device_name = TEST_DEVICE_NAME.format(i=device_i)
            html_text = res.data.decode()
            assert device_name in html_text
            assert TEST_DEVICE_NAME.format(i=device_i) in html_text
        logout(http)

    # Be sure user does not see not him devices
    user: m.User = users[0]
    else_users: list[m.User] = users[1:]
    assert else_users

    login(http, user.username, TEST_PASSWORD)
    devices: list[m.Device] = (
        m.Device.query.join(m.Account).filter_by(user_id=user.id).all()
    )
    assert devices

    for device in devices:
        res = http.get(f"/device/{device.uid}")
        assert res.status_code == 200

    other_devices: list[m.Device] = (
        m.Device.query.join(m.Account).filter(m.Account.user_id != user.id).all()
    )
    assert other_devices

    for other_device in other_devices:
        res = http.get(f"/device/{other_device.uid}")
        assert res.status_code != 200


def test_rename_device(mqtt: MqttTestClient):
    TEST_USER = "Test User Name"
    TEST_PASS = "pa@@ss894891934@@!eqf%"
    TEST_DEVICE_TYPE = "Test Type"
    TEST_DEVICE_NAME = "Test Device Name"
    TEST_DEVICE_ALIAS = "Test Device Alias"

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
    account: m.Account = m.Account.query.get(account.id)
    assert account.devices
    device: m.Device = account.devices[0]
    assert device.name == TEST_DEVICE_NAME
    assert device.type == TEST_DEVICE_TYPE
    assert not device.alias
    http: FlaskClient = mqtt.http_client
    login(http, TEST_USER, TEST_PASS)
    res = http.get(f"/device_edit/{device.uid}")
    assert res.status_code == 200

    res = http.post(
        f"/device_edit/{device.uid}",
        data=dict(
            name=TEST_DEVICE_ALIAS,
            uid=device.uid,
        ),
        follow_redirects=True,
    )
    assert res.status_code == 200
    device: m.Device = account.devices[0]
    assert device.name == TEST_DEVICE_NAME
    assert device.alias == TEST_DEVICE_ALIAS
