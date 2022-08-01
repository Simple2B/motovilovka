from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    HiddenField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    ValidationError,
    Length,
)
from app.models import Device


class DeviceNameForm(FlaskForm):
    name = StringField("Name", [DataRequired(), Length(min=2)])
    uid = HiddenField("UID", [DataRequired()])
    user_id = HiddenField("user_id", [DataRequired()])
    submit = SubmitField("Save")

    def validate_name(self, field):
        if (
            Device.query.filter_by(name=field.data)
            .filter_by(user_id=int(self.user_id))
            .filter(Device.uid != self.uid.data)
            .first()
        ):
            raise ValidationError("This name is taken.")
