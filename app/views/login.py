from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    request,
)
from flask_login import login_user, logout_user, login_required

from app.models import User
from app.forms import LoginForm
from app.logger import log

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user: User = User.authenticate(form.username.data, form.password.data)
        flash("You are successfully logged in!", "info")
        if user:
            login_user(user)
            return redirect(url_for("main.index"))
        flash("Wrong username or password.", "danger")
        log(log.ERROR, "Wrong username or password")
    return render_template("auth/login.html", form=form)


@login_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
