document.addEventListener("DOMContentLoaded", (evt) => {
  const deviceDashboard = document.querySelector(".device-dashboard");

  for (let deviceRow of deviceDashboard.children) {
    const deviceId = deviceRow.getAttribute("id");
    const deviceTypeBtn = deviceRow.querySelector(".btn-device-type");
    if (deviceTypeBtn != null) {
      deviceTypeBtn.addEventListener("click", (evt) => {
        window.open("device?id=" + deviceId, "_blank").focus();
        window.go;
      });
    }
  }
});
