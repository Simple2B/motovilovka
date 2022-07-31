from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user
from app import models as m

main_blueprint = Blueprint("main", __name__)

ADMIN_ROLES = (m.User.Role.admin,)


@main_blueprint.route("/")
@login_required
def index():
    if current_user.role in ADMIN_ROLES:
        return redirect(url_for("users.users_page"))
    else:
        return redirect(url_for("devices.devices_page"))
