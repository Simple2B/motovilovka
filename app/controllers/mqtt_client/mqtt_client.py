from typing import Any
from uuid import uuid4
from paho.mqtt import client as mqtt
from paho.mqtt.client import MQTTMessage
from app.logger import log
from app.models import Device, Account, SubDevice


BRIDGE_ITEMS = ("bridge",)


class MqttClient:
    def __init__(self, account: Account = None, client_id: str = "client"):
        from flask import current_app as app

        HOST, PORT = app.config["MOSQUITTO_HOST"], app.config["MOSQUITTO_PORT"]

        if account is None:
            mqtt_login = app.config["MOSQUITTO_ADMIN_USER"]
            mqtt_password = app.config["MOSQUITTO_ADMIN_PASSWORD"]
        else:
            mqtt_login = account.mqtt_login
            mqtt_password = account.mqtt_password

        self.client = mqtt.Client(
            client_id=f"{client_id}-{uuid4()}",
            reconnect_on_failure=False,
            clean_session=False,
        )

        # set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_failed
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        # self.client.on_message = self.on_message

        self.client.username_pw_set(mqtt_login, mqtt_password)
        log(log.INFO, "connect... %s %s", HOST, PORT)
        self.client.connect(HOST, PORT)

    @staticmethod
    def handle_error(err_message: str, message: mqtt.MQTTMessage):
        log(log.ERROR, "Error: %s, [%s]", message.topic, err_message)

    @staticmethod
    def on_device_message(device: Device, message: mqtt.MQTTMessage):
        if message.payload:
            msg_text = message.payload.decode("utf-8")
            log(log.INFO, "Device [%s]: [%s]", device.name, msg_text)

    @staticmethod
    def on_message(client: mqtt.Client, user_data: Any, message: MQTTMessage):
        # Check for topic length
        backslash_count = message.topic.count("/")
        if backslash_count < 2:
            MqttClient.handle_error("Invalid topic name", message)
            return

        # Get device data
        # TODO critical code! Need to optimize. Make device data getting in topic length check "code above"
        # TODO best way limit topics subpath on MQTT broker layer
        topic_path = message.topic.split("/")
        device_user, device_type, device_name = topic_path[:3]
        for topic_part in (device_type, device_name):
            if not topic_part:
                MqttClient.handle_error("Invalid topic name", message)
                return

        # Check if topic for transmit data
        # TODO try to disable rx topic on MQTT broker layer
        # if io != "tx":
        #     return

        account = Account.query.filter_by(mqtt_login=device_user).first()
        if not account:
            log(log.WARNING, "Account [%s] not found!", device_user)
            return

        # Search device in DB
        device = Device.query.filter_by(
            account_id=account.id,
            name=device_name,
            type=device_type,
        ).first()

        # Create device if device does not in DB
        if not device:
            device = Device(account_id=account.id, type=device_type, name=device_name)
            device.save()
            log(log.INFO, "New device created: %s", device)
        else:
            MqttClient.process_bridge_device(device, topic_path)

        MqttClient.on_device_message(device, message)

    @staticmethod
    def on_connect(client: mqtt.Client, user_data: Any, flags: dict, rc: int):
        log(log.INFO, "Connected. rc: %i", rc)
        client.subscribe("#")
        client.on_message = MqttClient.on_message

    @staticmethod
    def on_connect_failed(client: mqtt.Client):
        log(log.ERROR, "Connect failed: %s", client)

    @staticmethod
    def on_disconnect(client: mqtt.Client, userdata, rc):
        log(log.INFO, "Disconnected: %s", client)
        log(log.INFO, "User data: %s", userdata)
        log(log.INFO, "rc: %s", rc)
        pass

    @staticmethod
    def on_log(client: mqtt.Client, userdata, level, buf):
        log(log.INFO, "[%s] %s:%s", level, buf, userdata)

    def loop_forever(self):
        self.client.loop_forever(timeout=10)

    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        return self.client.publish(topic, payload, qos, retain, properties)

    @staticmethod
    def process_bridge_device(device: Device, topic_path: list[str]):
        if len(topic_path) < 4:
            return
        sub_item = topic_path[3]
        if not sub_item:
            return

        if sub_item in BRIDGE_ITEMS:
            if not device.is_bridge:
                device.is_bridge = True
                device.save()
            return

        if device.is_bridge:
            sub_device = SubDevice.query.filter_by(
                device_id=device.id,
                name=sub_item,
            ).first()
            if not sub_device:
                sub_device = SubDevice(
                    name=sub_item,
                    device_id=device.id,
                ).save()
