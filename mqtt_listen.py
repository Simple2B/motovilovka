import paho.mqtt.client as mqtt

HOST, PORT = "localhost", 1883


def on_message(client, userdata, message):
    print(f"message receive: {message.payload.decode('utf-8')}, topic: {message.topic}")


def on_connect(client, userdata, flags, rc):
    print(f"Connected: {client}")
    print(userdata, flags, rc)
    client.subscribe("top1")
    client.on_message = on_message


def on_connect_failed(client):
    print("Failed to connect")


client = mqtt.Client("p2")
# set username and password
client.username_pw_set("username", "password")
client.on_connect = on_connect
client.on_connect_fail = on_connect_failed
client.connect(HOST, PORT)
client.loop_forever()
