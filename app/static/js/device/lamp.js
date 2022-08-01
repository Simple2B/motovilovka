class LampDevice extends Device {
  onDeviceMessage(topic, msg, packet) {
    this.inputValue.value = msg.toString();
  }

  setInputHTML(selector) {
    this.inputValue = document.querySelector(selector);
    this.inputValue.addEventListener("input", (evt) => {
      this.changeLampValue();
    });
  }

  changeLampValue(change = 0) {
    let value = parseInt(this.inputValue.value);
    if (isNaN(value)) {
      value = 0;
    }

    value += change;

    this.sendMessage(value.toString());
    console.log(value, "sent");
  }
}

document.addEventListener("DOMContentLoaded", (evt) => {
  const increaseButton = document.querySelector("#increase");
  const decreaseButton = document.querySelector("#decrease");

  const lampDevice = new LampDevice(
    mqttData.login,
    mqttData.password,
    location.hostname,
    mqttData.port
  );

  lampDevice.setInputHTML("#lamp-value");

  increaseButton.addEventListener("click", (evt) => {
    lampDevice.changeLampValue(1);
  });

  decreaseButton.addEventListener("click", (evt) => {
    lampDevice.changeLampValue(-1);
  });
});
