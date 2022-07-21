from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email

from app.models import User


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset password")

    def validate_email(form, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("Not found registered user with this email.")
