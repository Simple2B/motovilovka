from app.controllers.mqtt_client import MqttClient, MQTTMessage
from app.models import Account


class MqttTestClient(MqttClient):
    def __init__(self, account: Account = None, client_id: str = "testClient"):
        # super().__init__(account, client_id)
        self.account = account
        self.client_id = client_id
        self.data = {}

    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        self.data[topic] = payload
        message = MQTTMessage(topic=topic.encode())
        message.payload = payload
        return self.on_message(None, None, message=message)
