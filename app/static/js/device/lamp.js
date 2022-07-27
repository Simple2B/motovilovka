class LampDevice extends Device {
    constructor(...args) {
        super(...args);
        this.listeners = [];
    }

    onDeviceMessage(msg) {
        this.inputValue.value = msg.toString();
    }

    setInputHTML(selector) {
        this.inputValue = document.querySelector(selector);
        this.inputValue.addEventListener('input', (evt) => {
            this.changeLampValue();
        })
    }

    changeLampValue(change=0) {
        let value = parseInt(this.inputValue.value);
        if (isNaN(value)) {
            value = 0;
        }

        value += change;

        this.sendMessage(value.toString());
        console.log(value, 'sended')
    }
}


document.addEventListener('DOMContentLoaded', (evt) => {
    const increaseButton = document.querySelector('#increase');
    const decraseButton = document.querySelector('#decrease');

    const lampDevice = new LampDevice(
        mqttData.login,
        mqttData.password,
        location.hostname,
        mqttData.port
    );

    lampDevice.setInputHTML('#lamp-value');

    increaseButton.addEventListener('click', (evt) => {
        lampDevice.changeLampValue(1);
    });

    decraseButton.addEventListener('click', (evt) => {
        lampDevice.changeLampValue(-1);
    });
});