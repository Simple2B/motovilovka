from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    EqualTo,
    ValidationError,
    Email,
)
from app.models import User


ROLES = [
    (User.Role.admin.value, User.Role.admin.name),
    (User.Role.client.value, User.Role.client.name),
]

FORBIDDEN_SYMBOLS = [
    "!",
    "@",
    "#",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    ":",
    ";",
    "<",
    ">",
    "?",
    ",",
    "/",
    "|",
    "\\",
    "*",
    "+",
    "'",
    '"',
    " ",
]


class UserCreateForm(FlaskForm):
    username = StringField("Username", [DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    password_confirm = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password do not match."),
        ],
    )
    role = SelectField("Role", coerce=int, validators=[InputRequired()], choices=ROLES)
    submit = SubmitField("Add User")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError("This username is taken.")

        for symbol in FORBIDDEN_SYMBOLS:
            if symbol in self.username.data:
                raise ValidationError("Forbidden symbols in username")
