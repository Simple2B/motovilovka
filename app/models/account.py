from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import relationship
from app import db
from app.models.utils import ModelMixin


def generate_uid() -> str:
    return str(uuid4())


class Account(db.Model, ModelMixin):

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mqtt_login = db.Column(db.String(16), unique=True, nullable=False)
    mqtt_password = db.Column(db.String(16), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)
    uid = db.Column(db.String(64), default=generate_uid)

    user = relationship("User")
    devices = relationship("Device", viewonly=True)

    def __repr__(self):
        return f"<{self.id}:{self.mqtt_login} u:{self.user.username}, created:{self.created_at}"
