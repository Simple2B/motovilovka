from datetime import datetime
from sqlalchemy.orm import relationship
from app import db
from app.models.utils import ModelMixin


class Device(db.Model, ModelMixin):

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    type = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)

    account = relationship("Account")

    def __repr__(self):
        return f"<{self.id}:{self.name} t:{self.type}>"
