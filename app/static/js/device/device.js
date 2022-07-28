class Device {
  constructor(username, password, hostname, port) {
    if (hostname.includes("localhost") || hostname.includes("127.0.0.1")) {
      this.mqttUrl = `ws://${hostname}:${port}/mqtt`;
    } else {
      this.mqttUrl = `wss://${hostname}:${port}/mqtt`;
    }
    this.messageQueue = [];
    this.events = {};
    this.deviceTopic = [
      username,
      mqttData.deviceType,
      mqttData.deviceName,
    ].join("/");
    this.mqttClient = mqtt.connect(this.mqttUrl, {
      clean: false,
      connectTimeout: 4000,
      clientId: "browser-client-" + uuidv4(),
      username: username,
      password: password,
    });

    this.messageOpt = {
      qos: 2,
      retain: true,
    }

    this.mqttClient.on("connect", () => {
      console.log("connected.");
      this.mqttClient.subscribe(this.deviceTopic, (err) => {
        if (err) {
          console.log("Error on subscription:", err);
        }
      });

      this.messageQueue.forEach(this.#sendMessage);
      this.sendMessage = this.#sendMessage;

      this.mqttClient.on("message", (topic, msg, packet) => {
        this.onDeviceMessage(msg);
      });
    });
  }

  sendMessage(msg) {
    this.messageQueue.push(msg);
  }

  #sendMessage(msg) {
    this.mqttClient.publish(this.deviceTopic, msg, this.messageOpt);
  }

  onDeviceMessage(msg) {
    console.log("Receive message: ", msg);
  }
}
