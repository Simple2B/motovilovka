from .mqtt import mqtt_service


class UserService:
    def create_user(self, username: str, password):
        mqtt_service.set_user(username, password)

    def remove_user(self, username):
        mqtt_service.remove_user(username)


user_service = UserService()
