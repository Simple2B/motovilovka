import email
from flask import (
    current_app,
    render_template,
    Blueprint,
    redirect,
    request,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from sqlalchemy import desc
from app.models import User
from app.forms import UserCreateForm, UserUpdateForm

users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/users")
@login_required
def users_page():
    # TODO: temporary solution
    # if current_user.role != User.Role.admin:
    #     return redirect(url_for("users.users_page"))
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(desc(User.id)).paginate(
        page=page, per_page=current_app.config["PAGE_SIZE"]
    )

    return render_template("users.html", users=users)


@users_blueprint.route("/user_delete/<int:user_id>", methods=["GET"])
@login_required
def user_delete(user_id: int):
    user: User = User.query.get(user_id)
    user.deleted = True
    user.save()

    return redirect(url_for("users.users_page"))


@users_blueprint.route("/user_add", methods=["GET", "POST"])
@login_required
def user_add():
    form = UserCreateForm()

    if form.validate_on_submit():
        User(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            role=User.Role(form.role.data),
        ).save()

        return redirect(url_for("users.users_page"))
    return render_template("user/add.html", form=form)


@users_blueprint.route("/user_update/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_update(user_id: int):
    if user_id != current_user.id and current_user.role != User.Role.admin:
        flash("Access denied", "danger")
        return redirect(url_for("users.user_update", user_id=current_user.id))
    form = UserUpdateForm()
    user: User = User.query.get(user_id)

    if form.validate_on_submit():
        user.username = form.username.data
        user.password = form.password.data
        user.role = User.Role(form.role.data)
        user.save()

        return redirect(url_for("users.users_page"))

    elif request.method == "GET":
        form.username.data = user.username
        form.role.data = user.role.name

    return render_template("user/update.html", form=form, user=user)


@users_blueprint.route("/user_search/<query>")
@login_required
def user_search(query):
    page = request.args.get("page", 1, type=int)
    splitted_queries = query.split(",")
    search_result = User.query.filter_by(id=0)
    for raw_single_query in splitted_queries:
        single_query = raw_single_query.strip()
        users = User.query.filter(User.username.like(f"%{single_query}%"))
        search_result = search_result.union(users)
    users = search_result.paginate(page=page, per_page=current_app.config["PAGE_SIZE"])
    return render_template("users.html", users=users, query=query)
