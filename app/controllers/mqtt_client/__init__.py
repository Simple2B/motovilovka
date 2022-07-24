from paho.mqtt import client as mqtt
from app.logger import log
from app.models import Device, Account


class MqttClient:
    def __init__(self, account: Account = None):
        from flask import current_app as app

        HOST, PORT = app.config["MOSQUITTO_HOST"], app.config["MOSQUITTO_PORT"]

        if account is None:
            mqtt_login = app.config["MOSQUITTO_ADMIN_USER"]
            mqtt_password = app.config["MOSQUITTO_ADMIN_PASSWORD"]
        else:
            mqtt_login = account.mqtt_login
            mqtt_password = account.mqtt_password

        self.client = mqtt.Client(
            client_id=f"client-{mqtt_login}",
            reconnect_on_failure=False,
        )

        # set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_failed
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log

        self.client.username_pw_set(mqtt_login, mqtt_password)
        log(log.INFO, "connect... %s %s", HOST, PORT)
        self.client.connect(HOST, PORT)

    @staticmethod
    def handle_error(err_message: str, message: mqtt.MQTTMessage):
        log(log.ERROR, f"Error: {message.topic}, {err_message}")

    @staticmethod
    def on_device_message(device: Device, message: mqtt.MQTTMessage):
        msg_text = message.payload.decode("utf-8")
        log(log.INFO, f"Device {device.name}: {msg_text}")

    @staticmethod
    def on_message(client, user_data, message):
        # Check for topic length
        backslash_count = 0
        for ch in message.topic:
            if ch == "/":
                backslash_count += 1
                if backslash_count > 3:
                    break

        if backslash_count != 3:
            MqttClient.handle_error("Invalid topic name", message)
            return

        # Get device data
        # TODO critical code! Need to optimize. Make device data getting in topic length check "code above"
        # TODO best way limit topics subpath on MQTT broker layer
        device_user, device_type, device_name, io = message.topic.split("/")
        for topic_path in (device_type, device_name, io):
            if not topic_path:
                MqttClient.handle_error("Invalid topic name", message)
                return

        # Check if topic for transmit data
        # TODO try to disable rx topic on MQTT broker layer
        if io != "tx":
            return

        # Search device in DB
        device = (
            Device.query.filter(Device.name == device_name)
            .join(Device.account)
            .filter(Account.mqtt_login == device_user)
            .first()
        )

        # Create device if device does not in DB
        if not device:
            account = Account.query.filter(Account.mqtt_login == device_user).first()
            if not account:
                MqttClient.handle_error("Account not found", message)
                return
            device = Device(account_id=account.id, type=device_type, name=device_name)
            device.save()
            log(log.INFO, f"New device created: {device.name}")

        # Update device type
        elif device.type != device_type:
            device.type = device_type
            device.save()

        MqttClient.on_device_message(device, message)

    @staticmethod
    def on_connect(client, user_data, flags, rc):
        log(log.INFO, "Connected. rc: %i", rc)
        client.subscribe("#")
        client.on_message = MqttClient.on_message

    @staticmethod
    def on_connect_failed(client):
        log(log.ERROR, "Connect failed: %s", client)

    @staticmethod
    def on_disconnect(client, userdata, rc):
        log(log.INFO, "Disconnected: %s", client)
        log(log.INFO, "User data: %s", userdata)
        log(log.INFO, "rc: %s", rc)
        pass

    @staticmethod
    def on_log(client, userdata, level, buf):
        log(log.INFO, "[%s] %s:%s", level, buf, userdata)

    def loop_forever(self):
        self.client.loop_forever(timeout=10)
