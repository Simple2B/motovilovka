import subprocess


class MqttService():
    def __init__(self, service_name: str):
        self.CONTAINER_BASE_CMD = ['docker-compose', 'exec', service_name]

    def container_exec(self, cmd: list):
        subprocess.call(self.CONTAINER_BASE_CMD + cmd)

    def set_user(self, username: str, password: str):
        self.container_exec(["mqtt-set-user", username, password])

    def remove_user(self, username: str):
        self.container_exec(["mqtt-remove-user", username])

    def set_admin(self):
        self.container_exec(["mqtt-set-admin"])


mqtt_service = MqttService("mqtt")
