from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import relationship
from app import db
from app.models.utils import ModelMixin


def gen_device_uid() -> str:
    return str(uuid4())


class Device(db.Model, ModelMixin):

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    type = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)
    uid = db.Column(db.String(64), default=gen_device_uid)
    alias = db.Column(db.String(128), nullable=True)
    is_bridge = db.Column(db.Boolean, default=False)

    account = relationship("Account")
    sub_devices = relationship("SubDevice", viewonly=True)

    def __repr__(self):
        return f"<{self.id}:{self.alias if self.alias else self.name} t:{self.type} {'+' if self.is_bridge else '-'}>"
