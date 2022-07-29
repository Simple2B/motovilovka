class Device {
  constructor() {
    this.mqttUrl = mqttData.webSocketURL;

    this.messageQueue = [];
    this.events = {};
    this.topic = [
      mqttData.login,
      mqttData.deviceType,
      mqttData.deviceName,
    ].join("/");
    this.mqttClient = mqtt.connect(this.mqttUrl, {
      clean: false,
      connectTimeout: 4000,
      clientId: `browser-client-${mqttData.login}-${+new Date()}`,
      username: mqttData.login,
      password: mqttData.password,
    });

    this.messageOpt = {
      qos: 2,
      retain: true,
    };

    this.mqttClient.on("connect", () => {
      console.log("connected.");
      this.mqttClient.subscribe(`${this.topic}/#`, (err) => {
        if (err) {
          console.log("Error on subscription:", err);
        }
      });

      this.messageQueue.forEach(this.#sendMessage);
      this.sendMessage = this.#sendMessage;

      this.mqttClient.on("message", (topic, msg, packet) => {
        this.onDeviceMessage(topic, msg, packet);
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

  publish(topic, msg) {
    this.mqttClient.publish(`${this.topic}/${topic}`, msg);
  }
}
