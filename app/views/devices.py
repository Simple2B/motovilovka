from flask import current_app, redirect, render_template, Blueprint, request, url_for
from flask_login import login_required, current_user
from app.models import Device, User, Account
from app.logger import log

devices_blueprint = Blueprint("devices", __name__)

ADMIN_ROLES = (User.Role.admin,)


@devices_blueprint.route("/devices")
@login_required
def devices_page():
    page = request.args.get("page", 1, type=int)
    query = Device.query
    if current_user.role not in ADMIN_ROLES:
        account: Account = Account.query.filter_by(user_id=current_user.id).first()
        query = query.filter_by(account_id=account.id)

    devices = query.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])

    return render_template(
        "devices.html",
        devices=devices,
        device_known_types=current_app.config["DEVICE_TYPE_TEMPLATE_MAP"],
    )


@devices_blueprint.route("/device_search/<query>")
@login_required
def device_search(query):
    page = request.args.get("page", 1, type=int)
    splitted_queries = query.split(",")
    search_result = Device.query.filter_by(id=0)

    for raw_single_query in splitted_queries:
        single_query = raw_single_query.strip()
        devices = Device.query.filter(Device.name.like(f"%{single_query}%"))
        if current_user.role not in ADMIN_ROLES:
            account: Account = Account.query.filter_by(user_id=current_user.id).first()
            devices = devices.filter_by(account_id=account.id)
        search_result = search_result.union(devices)

    devices = search_result.paginate(
        page=page, per_page=current_app.config["PAGE_SIZE"]
    )
    return render_template("devices.html", devices=devices, query=query)


@devices_blueprint.route("/device/<device_uid>")
@login_required
def device_page(device_uid: str):
    device: Device = Device.query.filter_by(uid=device_uid).first()
    if not device:
        log(log.ERROR, "Device [%s] not found", device_uid)
        return redirect(url_for("devices.devices_page"))

    if device.account.user.id != current_user.id:
        log(log.ERROR, "Access denied to device [%s]", device_uid)
        return redirect(url_for("devices.devices_page"))

    # Get template HTML name from device type
    template_path = current_app.config["DEVICE_TYPE_TEMPLATE_MAP"].get(device.type)
    if not template_path:
        log(log.WARNING, "Unknown device type [%s]", device.type)
        return redirect(url_for("devices.devices_page"))

    return render_template(
        template_path,
        device=device,
        mqtt_port=current_app.config["MOSQUITTO_EXTERNAL_WS_PORT"],
    )
