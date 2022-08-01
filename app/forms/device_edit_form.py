from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    ValidationError,
    Length,
)
from app.models import Device


class DeviceEditForm(FlaskForm):
    name = StringField("Name", [DataRequired(), Length(min=2)])
    uid = HiddenField("device_uid")
    submit = SubmitField("Save")

    def validate_name(self, field):

        for account in current_user.accounts:
            for device in account.devices:
                device: Device = device
                if device.alias == field.data and device.uid != self.uid.data:
                    raise ValidationError("This name is taken.")
