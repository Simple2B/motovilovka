import os
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

HOST, PORT = "localhost", int(os.environ.get("DEV_MOSQUITTO_PORT"))

login, password = "mqtt-login", "mqtt-password"

run = True


def on_connect(client: mqtt.Client, user_data, flags, rc):
    print(f"Connected: {client}")
    print(user_data, flags, rc)
    client.publish(f"{login}/temperature/d0/tx", time.time(), 2)


def on_connect_failed(client: mqtt.Client):
    print("Failed to connect")


def on_disconnect(client: mqtt.Client, user_data, rc):
    print("disconnected")
    print(user_data)
    print(rc)


def on_publish(client: mqtt.Client, user_data, mid):
    global run
    print(f"message sended: {mid}")
    run = False


client = mqtt.Client("user_1")
# set username and password
client.username_pw_set(login, password)
client.on_connect = on_connect
client.on_connect_fail = on_connect_failed
client.on_disconnect = on_disconnect
client.on_publish = on_publish

while True:
    try:
        client.connect(HOST, PORT)
        break
    except ConnectionRefusedError:
        print("MQTT server down: retry in 5 seconds")
        time.sleep(5)

client.loop_start()
while run:
    pass
