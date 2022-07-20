from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    request,
)
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import func

from app import mail, models as m
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, PasswordResetForm
from app.logger import log
from config import BaseConfig as CONF

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user: m.User = m.User.authenticate(form.username.data, form.password.data)
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


@login_blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = m.User(
            username=form.username.data,
            email=form.email.data,
        )
        user.save()
        # send mail to the user
        msg = Message(
            subject="New password",
            sender=CONF.MAIL_DEFAULT_SENDER,
            recipients=[user.email],
        )
        msg.html = render_template(
            "email/register.html",
            user=user,
            url=url_for(
                "login.password_reset",
                reset_password_uid=user.reset_password_uid,
                _external=True,
            ),
            config=CONF,
        )
        mail.send(msg)

        flash(
            "Registration successful. For reset password please check your e-mail.",
            "success",
        )
        return redirect(url_for("main.index"))
    elif form.is_submitted():
        flash("The given data was invalid.", "danger")
    return render_template("auth/register.html", form=form)


@login_blueprint.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user: m.User = m.User.query.filter(
            func.lower(m.User.email) == func.lower(form.email.data)
        ).first()
        if user:
            user.reset_password()
            # send mail to the user
            msg = Message(
                subject="Reset password",
                sender=CONF.MAIL_DEFAULT_SENDER,
                recipients=[user.email],
            )
            msg.html = render_template(
                "email/reset_password.html",
                user=user,
                url=url_for(
                    "login.password_reset",
                    reset_password_uid=user.reset_password_uid,
                    _external=True,
                ),
                config=CONF,
            )
            mail.send(msg)
            flash(
                "Password reset successful. For set new password please check your e-mail.",
                "success",
            )
            return redirect(url_for("main.index"))
        flash("No registered user with this e-mail", "danger")
    elif form.is_submitted():
        log(log.WARNING, "form error: [%s]", form.errors)
        flash("The given data was invalid.", "danger")
    return render_template("auth/forgot_password.html", form=form)


@login_blueprint.route("/password/<reset_password_uid>", methods=["GET", "POST"])
def password_reset(reset_password_uid: str):
    user: m.User = m.User.query.filter(
        m.User.reset_password_uid == reset_password_uid
    ).first()
    if not user:
        log(log.ERROR, "wrong reset_password_uid. [%s]", reset_password_uid)
        flash("Incorrect reset password link", "danger")
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.password = form.password.data
        user.reset_password_uid = ""
        user.save()
        login_user(user)
        flash("Login successful.", "success")
        return redirect(url_for("main.index"))
    elif form.is_submitted():
        log(log.WARNING, "form error: [%s]", form.errors)
        flash("Wrong user password.", "danger")
    return render_template(
        "auth/password_reset.html", form=form, reset_password_uid=reset_password_uid
    )
