from flask import Blueprint , render_template ,request, flash ,redirect ,url_for, session
from .model import Users, PurchaseHistory, FaceData, SignInHistory, Avatar
from . import db
from werkzeug.security import check_password_hash, generate_password_hash
import time
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
import socket

users = Blueprint("user",__name__)
@users.route('/sign_in', methods =['GET','POST'])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Đăng nhập thành công!", category="error")
                new_sgin_in_history = SignInHistory(ip_address=socket.gethostbyname(socket.gethostname()),user_id = user.id)
                db.session.add(new_sgin_in_history)
                db.session.commit()
                return redirect(url_for("views.home"))
            else:
                flash("Tài khoản hoặc mật khẩu chưa đúng!", category="error")
        else:
            flash("Tài khoản hoặc mật khẩu chưa đúng!", category="error")


    return render_template("sign_in.html",user = current_user)

@users.route('/sign_up', methods =['GET','POST'])
def sign_up():

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        id_card = request.form.get("id-card")
        birthday = request.form.get("birthday")
        gender = request.form.get("gender")
        password = request.form.get("password")
        comfirm_password = request.form.get("comfirm-password")

        user = Users.query.filter_by(email = email).first()

        if user:
            flash("Tài khoản đã tồn tại!", category="error")
        elif password!=comfirm_password:
            flash("Mật khẩu không khớp!", category="error")
        else:
            password = generate_password_hash(password, method="sha256")
            new_user = Users(name, birthday, gender, id_card, address, phone, email, password)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_session = Users.query.filter_by(email=email).first()
                if login_session:
                    login_user(login_session, remember=True)
                    flash("Đăng ký thành công!", category="error")
                    new_sgin_in_history = SignInHistory(ip_address=socket.gethostbyname(socket.gethostname()),user_id = login_session.id)
                    db.session.add(new_sgin_in_history)
                    db.session.commit()
                    return redirect(url_for("views.home"))
            except:
                pass
    return render_template("sign_up.html",user = current_user)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

