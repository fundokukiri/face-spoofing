from datetime import datetime
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class SignInHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(10000))
    date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
class PurchaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000000))
    price = db.Column(db.String(10000))
    date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class FaceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date_update = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Avatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    date_update = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    birthday = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    id_card = db.Column(db.String(12))
    address = db.Column(db.String(10000))
    phone = db.Column(db.String(10))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    currency = db.Column(db.Integer)
    date_create = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    date_update_password = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    histories = db.relationship("SignInHistory")
    avatars = db.relationship("Avatar")
    facedatas = db.relationship("FaceData")
    purchase_histories = db.relationship("PurchaseHistory")

    def __init__(self, name, birthday, gender, id_card, address, phone, email, password):

        self.name = name
        self.birthday = birthday
        self.gender = gender
        self.id_card = id_card
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.currency = 1000000000


