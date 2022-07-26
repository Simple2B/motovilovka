document.addEventListener('DOMContentLoaded', (evt) => {
    const valueInput = document.querySelector('#lamp-value');
    const increaseButton = document.querySelector('#increase');
    const decraseButton = document.querySelector('#decrease');


    device.onDeviceMessage = (msg) => {
        valueInput.value = msg.toString();
    }

    function sendLampValue(value) {
        device.publishMessage(value.toString());
    }

    increaseButton.addEventListener('click', (evt) => {
        let value = parseInt(valueInput.value);
        if (isNaN(value)) {
            value = 0;
        }

        value += 1;
        sendLampValue(value);
    })

    decraseButton.addEventListener('click', (evt) => {
        let value = parseInt(valueInput.value);
        if (isNaN(value)) {
            value = 0;
        }

        value -= 1;
        sendLampValue(value);
    })
});