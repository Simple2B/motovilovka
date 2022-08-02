from flask import (
    current_app,
    redirect,
    render_template,
    Blueprint,
    request,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from app.models import Device, User, Account, SubDevice
from app.forms import SubDeviceEditForm
from app.logger import log

sub_devices_blueprint = Blueprint("sub_devices", __name__)

ADMIN_ROLES = User.ADMIN_ROLES


@sub_devices_blueprint.route("/sub_devices/<device_uid>")
@login_required
def sub_devices_page(device_uid: str):
    page = request.args.get("page", 1, type=int)
    device: Device = Device.query.filter_by(uid=device_uid).first()

    if not device:
        log(log.ERROR, "Device not found %s", device_uid)
        return redirect(url_for("devices.devices_page_default"))

    if (
        current_user.role not in ADMIN_ROLES
        and device.account.user_id != current_user.id
    ):
        log(log.ERROR, "Access denied for user %s to %s", current_user, device.account)
        flash(f"Access denied to device {device_uid}.", "danger")
        return redirect(url_for("devices.devices_page_default"))

    sub_devices = SubDevice.query.filter_by(device_id=device.id).paginate(
        page=page,
        per_page=current_app.config["PAGE_SIZE"],
    )

    return render_template(
        "sub_devices.html",
        device=device,
        sub_devices=sub_devices,
        mqtt_url=current_app.config["MQTT_WS_URL"],
        device_known_types=current_app.config["DEVICE_TYPE_TEMPLATE_MAP"],
    )


@sub_devices_blueprint.route("/sub_device_search/<query>")
@login_required
def device_search(query):
    # TODO: need implement
    flash("Search is not implemented yet.", "info")
    return redirect(url_for("devices.devices_page_default"))


@sub_devices_blueprint.route("/sub_device/<sub_uid>")
@login_required
def sub_device_page(sub_uid: str):
    device: SubDevice = SubDevice.query.filter_by(uid=sub_uid).first()
    if not device:
        log(log.ERROR, "Device [%s] not found", sub_uid)
        return redirect(url_for("devices.devices_page_default"))

    if (
        current_user.role not in ADMIN_ROLES
        and device.device.account.user.id != current_user.id
    ):
        log(log.ERROR, "Access denied to device [%s]", sub_uid)
        return redirect(url_for("devices.devices_page_default"))

    return render_template(
        "device/sub_device.html",
        device=device.device,
        sub_device=device,
        mqtt_url=current_app.config["MQTT_WS_URL"],
    )


@sub_devices_blueprint.route("/sub_device_edit/<sub_uid>", methods=["POST", "GET"])
@login_required
def sub_device_edit(sub_uid: str):
    user: User = current_user
    device: SubDevice = SubDevice.query.filter_by(uid=sub_uid).first()
    if not device:
        log(log.ERROR, "Unknown device:[%s]", sub_uid)
        flash("Wrong device id.", "danger")
        return redirect(url_for("devices.devices_page_default"))
    if (
        current_user.role not in ADMIN_ROLES
        and device.device.account.user_id != user.id
    ):
        log(log.ERROR, "Access Denied to sub device:[%s] by user:%d", sub_uid, user.id)
        flash("Access Denied.", "danger")
        return redirect(url_for("devices.devices_page_default"))

    name = device.alias if device.alias else device.name
    form: SubDeviceEditForm = SubDeviceEditForm(
        name=name,
        uid=sub_uid,
        device_uid=device.device.uid,
    )
    if form.validate_on_submit():
        device.alias = form.name.data
        device.save()
        return redirect(url_for("sub_devices.sub_device_page", sub_uid=sub_uid))
    elif form.is_submitted():
        # form validation felt
        log(log.WARNING, "Edit device errors: [%s]", form.errors)
    return render_template("sub_device_edit.html", form=form, uid=device.uid)
