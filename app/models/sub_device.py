from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import relationship
from app import db
from app.models.utils import ModelMixin


def gen_device_uid() -> str:
    return str(uuid4())


class SubDevice(db.Model, ModelMixin):

    __tablename__ = "sub_devices"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"))
    name = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)
    uid = db.Column(db.String(64), default=gen_device_uid)
    alias = db.Column(db.String(128), nullable=True)

    device = relationship("Device")

    def __repr__(self):
        return f"<{self.id}:{self.name}:{self.alias}>"
