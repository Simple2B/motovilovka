import paho.mqtt.client as mqtt
import time
HOST, PORT = "localhost", 1883


def on_connect(client, userdata, flags, rc):
    print(f"Connected: {client}")
    print(userdata, flags, rc)
    client.publish("top1", time.time(), 2)


def on_connect_failed(client):
    print("Failed to connect")


def on_disconnect(client, userdata, rc):
    print("disconnected")
    print(userdata)
    print(rc)


def on_publish(client, userdata, mid):
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
