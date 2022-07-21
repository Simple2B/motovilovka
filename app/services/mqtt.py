import os
import requests


API_HOST = os.environ.get("MOSQUITTO_API_HOST", "localhost")
API_PORT = os.environ.get("MOSQUITTO_API_PORT", "8080")
BASE_URL = f"http://{API_HOST}:{API_PORT}"


class MqttService():
    def set_user(self, username: str, password: str):
        return requests.post(f"{BASE_URL}/user", json={"login": username, "password": password}).json()

    def remove_user(self, username: str):
        return requests.delete(f"{BASE_URL}/user/{username}").json()


mqtt_service = MqttService()
