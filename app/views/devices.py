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
from app.models import Device, User, Account
from app.forms import DeviceEditForm
from app.logger import log

devices_blueprint = Blueprint("devices", __name__)

ADMIN_ROLES = User.ADMIN_ROLES


@devices_blueprint.route("/devices")
@login_required
def devices_page_main():
    # get first account
    page = request.args.get("page", 1, type=int)
    query = Device.query
    if current_user.role not in ADMIN_ROLES:
        account: Account = Account.query.filter_by(user_id=current_user.id).first()
        query = query.filter_by(account_id=account.id)

    devices = query.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])

    return render_template(
        "devices.html",
        account=account,
        devices=devices,
        mqtt_url=current_app.config["MQTT_WS_URL"],
        device_known_types=current_app.config["DEVICE_TYPE_TEMPLATE_MAP"],
    )


@devices_blueprint.route("/devices/<account_uid>")
@login_required
def devices_page(account_uid: str):
    page = request.args.get("page", 1, type=int)
    account: Account = Account.query.filter_by(uid=account_uid).first()

    if not account:
        log(log.ERROR, "Account not found %s", account.uid)
        return redirect(url_for("accounts.accounts_page"))

    if current_user.role not in ADMIN_ROLES and account.user_id != current_user.id:
        log(log.ERROR, "Access denied for user %s to %s", current_user, account)
        flash(f"Access denied to device {account_uid}.", "danger")
        return redirect(url_for("accounts.accounts_page"))

    query = Device.query.filter_by(account_id=account.id)
    devices = query.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])

    return render_template(
        "devices.html",
        devices=devices,
        account=account,
        mqtt_url=current_app.config["MQTT_WS_URL"],
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
        return redirect(url_for("devices.devices_page_main"))

    if device.account.user.id != current_user.id:
        log(log.ERROR, "Access denied to device [%s]", device_uid)
        return redirect(url_for("devices.devices_page_main"))

    # Get template HTML name from device type
    template_path = current_app.config["DEVICE_TYPE_TEMPLATE_MAP"].get(device.type)
    if not template_path:
        log(log.WARNING, "Unknown device type [%s]", device.type)
        return redirect(url_for("devices.devices_page_main"))

    return render_template(
        template_path,
        device=device,
        mqtt_url=current_app.config["MQTT_WS_URL"],
    )


@devices_blueprint.route("/device_edit/<device_uid>", methods=["POST", "GET"])
@login_required
def device_edit(device_uid: str):
    user: User = current_user
    device: Device = Device.query.filter_by(uid=device_uid).first()
    if not device:
        log(log.ERROR, "Unknown device:[%s]", device_uid)
        flash("Wrong device id.", "danger")
        return redirect(url_for("devices.devices_page"))
    if current_user.role not in ADMIN_ROLES and device.account.user_id != user.id:
        log(log.ERROR, "Access Denied to device:%d by user:%d", device.id, user.id)
        flash("Access Denied.", "danger")
        return redirect(url_for("devices.devices_page"))

    name = device.alias if device.alias else device.name
    form: DeviceEditForm = DeviceEditForm(name=name, uid=device_uid)
    if form.validate_on_submit():
        device.alias = form.name.data
        device.save()
        return redirect(url_for("devices.devices_page"))
    elif form.is_submitted():
        # form validation felt
        log(log.WARNING, "Edit device errors: [%s]", form.errors)
    return render_template("device_edit.html", form=form, uid=device.uid)
