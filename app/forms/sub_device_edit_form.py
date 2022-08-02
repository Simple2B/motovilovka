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


class SubDeviceEditForm(FlaskForm):
    name = StringField("Name", [DataRequired(), Length(min=2)])
    device_uid = HiddenField("device_uid")
    uid = HiddenField("uid")
    submit = SubmitField("Save")

    def validate_name(self, field):

        for account in current_user.accounts:
            for device in account.devices:
                device: Device = device
                for sub_device in device.sub_devices:
                    if (
                        sub_device.alias == field.data
                        and sub_device.uid != self.uid.data
                    ):
                        raise ValidationError("This name is taken.")
