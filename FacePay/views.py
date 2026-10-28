from flask import Blueprint,app , render_template, flash, request, jsonify,redirect , Response ,url_for
from FacePay.func import FaceDetector, FaceRecognize, SuggestPoseCounter, FaceAntiSpoofing
from flask_login import login_required, current_user
from .facetools.utils import visualize_results_register
from werkzeug.exceptions import RequestURITooLarge
from sqlalchemy.sql.functions import user
from .model import PurchaseHistory, Users
from datetime import timedelta
from . import db
import json
import cv2
import os

views = Blueprint("views",__name__)
data_cart = []
money = 0
recognize_id = 0
threshold = 0.5
current_id = 0

def gen_frames_checkout():

    global recognize_id 
    frame_count = 0

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:

        status, frame = camera.read()
        frame = cv2.flip(frame,1)
        frame_count += 1
        canvas = frame.copy()
        faces, boxes = FaceDetector(frame,False)
        if not faces:
            recognize_id = 0
        try:
            for face_arr , box in zip(faces,boxes):              
                score, label, canvas =  FaceAntiSpoofing(canvas, face_arr, box, threshold)
                cv2.imwrite("FacePay/static/user_img_temp/temp.jpg",frame)
                # if frame_count%15==0 or frame_count==1:
                recognize_id2, scoreRecognize = FaceRecognize(face_arr,
                                                                score,
                                                                threshold,
                                                                probabilitiesFaceNet=0.6,
                                                                probabilitiesArcFace=0.8,
                                                                ArcFaceActivate=False)
                recognize_id = int(recognize_id2)
        except:
            pass
        if not status:
            break
        else:
            status, buffer=cv2.imencode('.jpg',canvas)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
 

@views.route('/video_feed')
def video_feed():
    return Response(gen_frames_checkout(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames_register():

    dataCounter = [0,0,0,0,0]
    path_DataSet_FaceNet = "FacePay/static/Data/FaceNet/"
    path_DataSet_ArcFace = "FacePay/static/Data/ArcFace/"
    if not os.path.exists(path_DataSet_FaceNet + str(current_id) + "/"):
        os.mkdir(path_DataSet_FaceNet + str(current_id) + "/")
    if not os.path.exists(path_DataSet_ArcFace + str(current_id) + "/"):
        os.mkdir(path_DataSet_ArcFace + str(current_id) + "/")

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))
    frame_size = (frame_width, frame_height)
    
    rec_width = max(1, int(frame_width/240))
    txt_offset = int(frame_height/50)
    txt_width = max(1, int(frame_width/480))

    while True:

        status, frame = camera.read()
        frame = cv2.flip(frame,1)
        canvas = frame.copy()
        faces, boxes, poses = FaceDetector(frame,True)
        try:
            for face_arr , box in zip(faces,boxes):
                score, label, canvas =  FaceAntiSpoofing(canvas, face_arr, box, threshold)
                if score > 0.5 and dataCounter[0]+dataCounter[1]+dataCounter[2]+dataCounter[3]+dataCounter[4]<5*50:
                    suggest_pose, dataCounter =  SuggestPoseCounter(face_arr, dataCounter, poses, 50, str(current_id))
                    
                    if dataCounter[0]+dataCounter[1]+dataCounter[2]+dataCounter[3]+dataCounter[4] == 50*5:
                        cv2.imwrite(path_DataSet_ArcFace + str(current_id) + "/" + "temp.jpg", face_arr)
                        suggest_pose = "Complete !!!"
                        break
                
                res_text = "ID: {} Pose: {}".format(current_id ,suggest_pose)
                canvas = visualize_results_register(canvas,box,txt_offset=txt_offset,txt_width=txt_width,res_text=res_text)
        except:
            pass
        if not status:
            break
        else:
            status, buffer=cv2.imencode('.jpg',canvas)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
 
@views.route('/video_feed_register')
def video_feed_register():
    return Response(gen_frames_register(), mimetype='multipart/x-mixed-replace; boundary=frame')


@views.route("/", methods=["GET", "POST"])
# @login_required
def home():
    global money, data_cart , recognize_id
    if request.method == "POST":
        money = request.form.get("total-price")
        data_cart = request.form.get("data-purchase")
        return redirect(url_for("views.checkout"))
    if recognize_id!=0 and money!=0:
        user = Users.query.filter_by(id=int(recognize_id)).first()
        if user:
            current_currency = int(user.currency)
            if 0 < int(money) < current_currency:
                user.currency = current_currency - int(money)
                checkout = PurchaseHistory( data = data_cart, 
                                            price = money, 
                                            user_id = int(recognize_id))
                db.session.add(checkout)
                db.session.commit()
                print(recognize_id)
                recognize_id = 0
                money = 0
                data_cart = []
                flash("Thanh toán thành công!", category="error")
            else:
                recognize_id = 0
                money = 0
                data_cart = []
                flash("Thanh toán thất bại! Số dư không đủ!", category="error")
        else:
            recognize_id = 0
            money = 0
            data_cart = []
            flash("Thanh toán thất bại!", category="error")
    if recognize_id==0 and money!=0:
        recognize_id = 0
        money = 0
        data_cart = []
        flash("Thanh toán thất bại!", category="error")

    return render_template("home.html", user=current_user )

@views.route("/account", methods=["GET", "POST"])
@login_required
def account():
    global current_id
    if request.method == "POST":
        return redirect(url_for("views.face_register"))
    current_id = current_user.id
    name = current_user.name
    birthday = current_user.birthday
    gender = current_user.gender
    id_card = current_user.id_card
    address = current_user.address
    phone = current_user.phone
    email = current_user.email
    currency = current_user.currency
    return render_template("account.html", user=current_user
                                         , name=name
                                         , gender=gender
                                         , birthday = birthday
                                         , id_card=id_card
                                         , address=address
                                         , phone=phone
                                         , email=email
                                         , currency=currency
                                         ,avatar = "../static/Data/ArcFace/"+str(current_user.id)+"/temp.jpg")


@views.route("/checkout")
def checkout(): 
    if money ==0:
        return redirect(url_for("views.home"))
    else:
        return render_template("checkout.html",user=current_user)

@views.route("/last_checkout")
def last_checkout(): 
    if money ==0:
        return redirect(url_for("views.home"))
    else:
        return render_template("last_checkout.html",user=current_user)

@views.route("/face_register")
@login_required
def face_register(): 
    return render_template("face_register.html",user=current_user)