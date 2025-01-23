const alerts = document.querySelector("#alerts")

function alert_info(text) {
    let newInfo = new_alert(text, "info", "<i class=\"fa-solid fa-circle-info\"></i>");
    newInfo.classList.add("info");
}

function alert_success(text) {
    new_alert(text, "success", "<i class=\"fa-solid fa-circle-check\"></i>");
}

function alert_warning(text) {
    new_alert(text, "warning", "<i class=\"fa-solid fa-circle-exclamation\">");
}

function alert_error(text) {
    new_alert(text, "error", "<i class=\"fa-solid fa-triangle-exclamation\"></i>");
}

function new_alert(text, style, icon) {
    let newAlert = document.createElement("div");
    newAlert.classList.add("alert");
    newAlert.classList.add(style);

    let iconDiv = newAlert.appendChild(document.createElement("div"));
    iconDiv.innerHTML = icon;

    let textDiv = newAlert.appendChild(document.createElement("div"));
    textDiv.innerHTML = text;

    let exitDiv = newAlert.appendChild(document.createElement("div"));
    exitDiv.innerHTML = '<i class="fa-solid fa-xmark"></i>';

    exitDiv.addEventListener("click", () => {
        newAlert.remove();
    });

    setTimeout(function () {
        newAlert.remove();
    }, 3500);

    alerts.appendChild(newAlert);
    return newAlert;
}

function test_alerts () {
    alert_info("JS TEST info");
    alert_success("JS TEST success");
    alert_warning("JS TEST warning");
    alert_error("JS TEST error");
}
