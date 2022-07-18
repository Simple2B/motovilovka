import time
import paho.mqtt.client as mqtt

HOST, PORT = "localhost", 1883


def on_connect(client: mqtt.Client, user_data, flags, rc):
    print(f"Connected: {client}")
    print(user_data, flags, rc)
    client.publish("top1", time.time(), 2)


def on_connect_failed(client: mqtt.Client):
    print("Failed to connect")


def on_disconnect(client: mqtt.Client, user_data, rc):
    print("disconnected")
    print(user_data)
    print(rc)


def on_publish(client: mqtt.Client, user_data, mid):
    print(f"message sended: {mid}")


client = mqtt.Client("p1")
# set username and password
client.username_pw_set("username", "password")
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

client.loop_forever()
