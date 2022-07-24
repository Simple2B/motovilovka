import paho.mqtt.client as mqtt

HOST, PORT = "localhost", 7883


def on_message(client, user_data, message):
    print(f"message receive: {message.payload.decode('utf-8')}, topic: {message.topic}")


def on_connect(client, user_data, flags, rc):
    print(f"Connected: {client}")
    print(user_data, flags, rc)
    client.subscribe("top1")
    client.on_message = on_message


def on_connect_failed(client):
    print("Failed to connect")


client = mqtt.Client("p2")
# set username and password
client.username_pw_set("admin", "passwd")
client.on_connect = on_connect
client.on_connect_fail = on_connect_failed
client.connect(HOST, PORT)
client.loop_forever()
