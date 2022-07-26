class Device {
	constructor () {
		this.messageQueue = [];
	}
	
	onDeviceMessage(message) {
		console.log('msg:', msg)
	} 

	publishMessage (msg) {
		this.messageQueue.push(msg)
	}

}

const device = new Device();

document.addEventListener('DOMContentLoaded', (evt) => {
	const options = {
  	// Clean session
  	clean: true,
    connectTimeout: 4000,
    // Auth
		// TODO client test UUID4
    clientId: "browser_test",
    username: mqttData.login,
    password: mqttData.password,
  };

	const mqttUrl = "ws://" + window.location.hostname + ":" + mqttData.port + "/mqtt";
	const client = mqtt.connect(mqttUrl, options);
	const device_topic = [mqttData.login, mqttData.deviceType, mqttData.deviceName].join('/');

	client.on('connect', () => {
		console.log('Connected to mqtt-broker');
		client.subscribe('#', (err) => {
			if (err) {
				console.log("Cannot subscribe: " + err);
				return;
			}
		})

		client.on('message', (topic, msg, packet) => {
			device.onDeviceMessage(msg);
		});

		device.publishMessage = (msg) => {
			client.publish(device_topic, msg);
		}

		device.messageQueue.forEach((msg) => {
			device.publishMessage(msg);
		});
	});
});