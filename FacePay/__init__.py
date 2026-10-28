from flask import Flask, Response, render_template, request, redirect, session, url_for, flash
from FacePay.func import LoadFaceRecognize, LoadAntiSpoofing
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
from dotenv import load_dotenv
import cv2
import os


img = cv2.imread("FacePay/static/images/temp.jpg")
res_text1=LoadAntiSpoofing(img, 0.5)
res_text2=LoadFaceRecognize(img)

print("___________________________FOR_LOAD_MODEL_______________________________")
print("________________________________________________________________________")
print(res_text1)
print(res_text1)
print(res_text1)
print(res_text2)
print(res_text2)
print(res_text2)
print("________________________________________________________________________")
print("________________________________________________________________________")



db = SQLAlchemy()

load_dotenv()

SECRET_KEY = os.environ.get("KEY")
DB_NAME = os.environ.get("DB_NAME")

def create_database(app):
    if not os.path.exists("zFacePayApp/"+DB_NAME):
        db.create_all(app=app)
        print("Created Database")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .model import PurchaseHistory, Users, FaceData, Avatar, SignInHistory
    create_database(app)
    
    from .users import users
    from .views import views

    app.register_blueprint(users)
    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.login_view = "user.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))
    return app