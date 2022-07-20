from datetime import datetime
import enum
from sqlalchemy import Enum
from uuid import uuid4


from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.utils import ModelMixin


def gen_password_reset_id() -> str:
    return str(uuid4())


class User(db.Model, UserMixin, ModelMixin):

    __tablename__ = "users"

    class Role(enum.Enum):
        """Utility class to support
        admin - creates users, including admins
        client - application client
        """

        admin = 1
        client = 2

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    activated = db.Column(db.Boolean, default=False)
    reset_password_uid = db.Column(db.String(64), default=gen_password_reset_id)
    role = db.Column(Enum(Role), default=Role.client)
    created_at = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)

    accounts = relationship("Account", viewonly=True)

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @classmethod
    def authenticate(cls, user_id, password):
        user = cls.query.filter(
            db.or_(
                func.lower(cls.username) == func.lower(user_id),
                func.lower(cls.email) == func.lower(user_id),
            )
        ).first()
        if user is not None and check_password_hash(user.password, password):
            return user

    def __repr__(self):
        return f"<{self.id}: {self.username} ({self.role})>"


class AnonymousUser(AnonymousUserMixin):
    pass
