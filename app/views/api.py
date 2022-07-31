from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required, current_user
from app.models import Account


api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/accounts", methods=["GET"])
@login_required
def get_accounts():
    page = request.args.get("page", 1, type=int)
    accounts_query = Account.query.filter_by(user_id=current_user.id)
    accounts = accounts_query.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])
    accounts_dict = {
        account.mqtt_login: account.mqtt_password
        for account in accounts.items
    }

    return jsonify({"accounts": accounts_dict, "total": accounts.total})


@api_blueprint.route("/broker/info", methods=["GET"])
@login_required
def get_broker_info():
    info = {
        "port": current_app.config["MOSQUITTO_EXTERNAL_WS_PORT"],
    }
    return jsonify({"info": info})
