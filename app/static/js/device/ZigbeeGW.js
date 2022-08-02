class SocketDevice extends Device {
  constructor() {
    super();
  }

  onDeviceMessage(topic, msg, packet) {
    const name = topic.split("/").slice(3).join("/");
    console.log(`${name}: `, msg.toString());
    this.#onChange(name, msg.toString());
  }

  #onChange(name, value) {
    // console.log(`${name}: `, value);
    switch (true) {
      case /LWT/i.test(name):
        this.setInputHTML("onlineStatus", value);
        break;
      case /bridge\/state/i.test(name):
        this.setInputHTML("bridge-state", value);
        break;
      // case /status/i.test(name):
      //   this.setInputHTML("status", value.trim());
      //   break;
      default:
        console.log(`unknown key: ${name}=[${value}]`);
        break;
    }
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
