document.addEventListener('DOMContentLoaded', (evt) => {
    const deviceDashboard = document.querySelector('.device-dashboard');
    
    for (let deviceRow of deviceDashboard.children) {
        const deviceId = deviceRow.getAttribute('id');
        deviceRow.addEventListener('click', (evt) => {
            window.open('device?id=' + deviceId, '_blank').focus();
        });
    }
});