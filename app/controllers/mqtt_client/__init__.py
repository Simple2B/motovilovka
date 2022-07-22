from paho.mqtt import client as mqtt

# from paho.mqtt.client import MQTTv311
from config import BaseConfig as conf
from app.logger import log


class MqttClient:
    def __init__(
        self, login=conf.MOSQUITTO_ADMIN_USER, password=conf.MOSQUITTO_ADMIN_PASSWORD
    ):
        from flask import current_app as app

        self.client = mqtt.Client(
            client_id=f"client-{login}",
            # clean_session=None,
            # userdata=None,
            # protocol=MQTTv311,
            # transport="tcp",
            reconnect_on_failure=False,
        )

        # set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_failed
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log

        log(log.INFO, "set username and password")
        self.client.username_pw_set(login, password)
        log(log.INFO, "connect...")
        self.client.connect(app.config["MOSQUITTO_HOST"], app.config["MOSQUITTO_PORT"])

    @staticmethod
    def on_message(client, user_data, message):
        log(log.INFO, "Receive message from: %s", client)
        log(log.INFO, "Topic: %s", message.topic)
        log(log.INFO, "Data: %s", message.payload.decode("utf-8"))

    @staticmethod
    def on_connect(client, user_data, flags, rc):
        log(log.INFO, "Connected: %s", client)
        print(user_data, flags, rc)
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
