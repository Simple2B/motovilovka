class GlobalDeviceListener {
  constructor(mqttData) {
    this.listeners = {};
    this.mqttUrl = mqttData.mqttUrl;
    this.mqttUsername = mqttData.username;
    this.clientId = "browser-client-" + mqttData.username + '-' + (new Date()).getTime();

    // connection options
    this.mqttClient = mqtt.connect(this.mqttUrl, {
      clientId: this.clientId,
      username: mqttData.username,
      password: mqttData.password,
      clean: false,
      connectTimeout: 4000,
    });

    // connect and subscribe
    this.mqttClient.on('connect', () => {
      console.log('connected', mqttData.username);

      this.mqttClient.on('message', (topic, message) => {
        const [deviceAccount, deviceType, ...topicPath] = topic.split('/');
        const topicPostfix = topicPath.join('/');
        if (this.listeners.hasOwnProperty(topicPostfix)) {
          this.listeners[topicPostfix](message);
        }
      });

      const topic = mqttData.username + '/#';
      this.mqttClient.subscribe(topic, (err) => {
        if (err) {
          console.log('Error subscribe:', topic, err);
        } else {
          console.log('Subscribed:', topic)
        }
      });
    });
  }

  addTopicListener(topic, callback) {
    this.listeners[topic] = callback
  }
}


document.addEventListener("DOMContentLoaded", (evt) => {
  const globalDeviceListener = new GlobalDeviceListener(mqttData);
  const devicesHTML = document.querySelector('.device-dashboard').children;

  for (let deviceColumn of devicesHTML) {
    const deviceName = deviceColumn.querySelector('.device-name').getAttribute('name');
    const indicatorIcon = deviceColumn.querySelector('.emoji-icon');


    globalDeviceListener.addTopicListener([deviceName, 'LWT'].join('/'), (msg) => {
      const messageText = msg.toString().toLowerCase();
      if (messageText == 'offline') {
        indicatorIcon.classList.remove('device-connected');
        indicatorIcon.classList.add('device-disconnected');
      } else if (messageText == 'online') {
        indicatorIcon.classList.remove('device-disconnected');
        indicatorIcon.classList.add('device-connected');
      }
    });
  }
});
