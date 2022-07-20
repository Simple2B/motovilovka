from flask import (
    current_app,
    render_template,
    Blueprint,
    request,
)
from flask_login import login_required, current_user
from app.models import Account, User

accounts_blueprint = Blueprint("accounts", __name__)

ADMIN_ROLES = (User.Role.admin,)


@accounts_blueprint.route("/accounts")
@login_required
def accounts_page():
    page = request.args.get("page", 1, type=int)
    query = Account.query
    if current_user.role not in ADMIN_ROLES:
        query = query.filter_by(user_id=current_user.id)

    accounts = query.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])

    return render_template("accounts.html", accounts=accounts)


@accounts_blueprint.route("/account_search/<query>")
@login_required
def accounts_search(query):
    page = request.args.get("page", 1, type=int)
    splitted_queries = query.split(",")
    search_result = Account.query.filter_by(id=0)

    for raw_single_query in splitted_queries:
        single_query = raw_single_query.strip()
        accounts = Account.query.filter(Account.mqtt_login.like(f"%{single_query}%"))
        if current_user.role not in ADMIN_ROLES:
            accounts = accounts.filter_by(user_id=current_user.id)
        search_result = search_result.union(accounts)

    accounts = search_result.paginate(
        page=page, per_page=current_app.config["PAGE_SIZE"]
    )
    return render_template("users.html", accounts=accounts, query=query)
