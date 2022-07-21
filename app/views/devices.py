from flask import (
    current_app,
    render_template,
    Blueprint,
    request,
)
from flask_login import login_required, current_user
from app.models import Device, User, Account

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

    return render_template("devices.html", devices=devices)


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
