class SocketDevice extends Device {
  constructor() {
    super();
    this.dataTopic = `${this.topic}/${subDeviceName}`;
  }

  onDeviceMessage(topic, msg, packet) {
    if (topic === this.dataTopic) {
      // console.log(msg);
      const decoder = new TextDecoder();
      const text = decoder.decode(msg);
      this.#onChange(JSON.parse(text));
    }
    // const name = topic.split("/").slice(3).join("/");
    // console.log(`${name}: `, msg.toString());
    // this.#onChange(name, msg.toString());
  }

  #onChange(data) {
    Object.keys(data).forEach((key) => {
      this.setInputHTML(key, data[key]);
    });
    // for (let key in Object.keys(data)) {
    //   this.setInputHTML(key, data[key]);
    // }
  }

  setInputHTML(name, value) {
    const nameElement = `elem_${name}`;
    let element = this[nameElement];
    if (!element) {
      element = document.getElementById(name);
      this[nameElement] = element;
    }
    if (element) {
      element.innerHTML = value;
    }
  }

  setSwitch(name, value) {
    const nameElement = `elem_${name}`;
    let element = this[nameElement];
    if (!element) {
      element = document.getElementById(name);
      this[nameElement] = element;
    }
    if (element) {
      element.checked = !!value;
    }
  }
}

document.addEventListener("DOMContentLoaded", (evt) => {
  document.device = new SocketDevice();
  document.device.elem_relayState = document.getElementById("relayState");
  document.device.elem_relayState &&
    document.device.elem_relayState.addEventListener("change", (e) => {
      // gpio/5
      const device = document.device;
      document.device.publish("gpio/5", e.target.checked ? "1" : "0");
    });
});
