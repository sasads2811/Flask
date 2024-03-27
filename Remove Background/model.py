import os

from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from app import db


class BaseMixin(object):

    @declared_attr
    def id(self):
        return db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    @declared_attr
    def date_of_creation(self):
        return db.deferred(db.Column(db.DateTime, nullable=False, server_default=func.now()))

    @declared_attr
    def date_of_update(self):
        return db.deferred(
            db.Column(db.DateTime, nullable=False, onupdate=func.now(), server_default=func.now()))

    @declared_attr
    def deleted(self):
        return db.deferred(db.Column(db.Boolean, server_default=db.false(), default=False))

    @classmethod
    def get_by_id(cls, _id):
        if _id is None:
            return None
        if hasattr(cls, "query"):
            return cls.query.get(_id)

SEED = os.environ.get("SEED", "239mvkefw9043;l;m4@$@#fw,340m23fvke")

class User(BaseMixin,db.Model,UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.LargeBinary)

    # def __init__(self, username, email, password, profile_image):
    #     self.username = username
    #     self.email = email
    #     self.password = password
    #     self.profile_image = profile_image

    def __repr__(self):
        return f'<User {self.username}>'

    def is_active(self):
        # All users are considered active
        return True
    def get_id(cls):
        return cls.id

    @classmethod
    def get_by_email(cls,email):
        return cls.query.filter(cls.email == email).first()

    # @classmethod
    # def login(cls, email, password):
    #     # print(hashlib.sha512("{};{}".format(SEED, password).encode("UTF-8")).hexdigest())
    #     user = cls.query.filter(db.or_(cls.email == email, cls.password == password), ~cls.deleted).first()
    #     if not user:
    #         return
    #     if user.password_hash == hashlib.sha512("{};{}".format(SEED, password).encode("UTF-8")).hexdigest():
    #         return user


