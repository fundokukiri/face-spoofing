import os
import cv2
import pickle
import numpy as np
import tensorflow as tf
from arcface import ArcFace
from facenet.src import facenet
from imutils.video import VideoStream
from .facetools.face_detection import FaceDetection
from .facetools.utils import visualize_results
from .facetools.utils import visualize_results_register
from .facetools.utils import visualize_results_recognize
from .facetools.face_antispoofing import AntiSpoof

COLOR_REAL = (0, 255, 0)
COLOR_FAKE = (0, 0, 255)
COLOR_UNKNOWN = (127, 127, 127)

path_DataVector = 'FacePay/Models/FaceNet_Model.pkl'
path_ModelFaceNet = 'FacePay/Models/FaceNet_Model.pb'

path_DataSet_FaceNet = "FacePay/static/Data/FaceNet/"
path_DataSet_ArcFace = "FacePay/static/Data/ArcFace/"

with open(path_DataVector, 'rb') as file:
    model, class_names = pickle.load(file)

gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.6)
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options,
                                                            log_device_placement=False))
facenet.load_model(path_ModelFaceNet)
images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")


arcFacedetector = ArcFace.ArcFace()
face_AntiSpoofDetector = AntiSpoof("FacePay/Models/AntiSpoofing_bin_1.5_128.onnx")
face_Detector = FaceDetection(max_num_faces= 1)

def FaceDetector(frame, Flag):
    if Flag:
        faces, boxes, poses = face_Detector(frame,Flag)
        return faces, boxes, poses
    else:
        faces, boxes = face_Detector(frame,Flag)
        return faces, boxes

def LoadAntiSpoofing(face_arr, threshold):

    img = cv2.cvtColor(face_arr, cv2.COLOR_BGR2RGB)
    pred = face_AntiSpoofDetector([img])[0]
    score = pred[0][0]
    label = np.argmax(pred)

    if label == 0:
        if score > threshold:
            res_text = "REAL      {:.2f}".format(score)
        else:
            res_text = "unknown" 
    else:
        res_text = "FAKE      {:.2f}".format(score)

    return res_text

def LoadFaceRecognize(face_arr):
    
    scaled = facenet.prewhiten(face_arr)
    scaled_reshape = scaled.reshape(-1, 160,160,3)
    feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
    emb_array = sess.run(embeddings, feed_dict=feed_dict)
    predictions = model.predict_proba(emb_array)
    best_class_indices = np.argmax(predictions, axis=1)
    best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
    bestName = class_names[best_class_indices[0]]
    recognizeScore = float(best_class_probabilities) 

    if best_class_probabilities > 0.6 :
        emb1 = arcFacedetector.calc_emb(face_arr)
        emb2 = arcFacedetector.calc_emb(path_DataSet_ArcFace + str(bestName) + "/temp.jpg")
            
        if arcFacedetector.get_distance_embeddings(emb1,emb2) < 0.8:
            res_text = "{}      {:.2f}".format(bestName, recognizeScore)
        return res_text           


def FaceAntiSpoofing(canvas, face_arr, box, threshold):

    img = cv2.cvtColor(face_arr, cv2.COLOR_BGR2RGB)
    pred = face_AntiSpoofDetector([img])[0]
    score = pred[0][0]
    label = np.argmax(pred)

    if label == 0:
        if score > threshold:
            color = COLOR_REAL
        else: 
            color = COLOR_UNKNOWN
    else:
        color = COLOR_FAKE
    canvas = visualize_results(canvas, box, color)
    return score, label, canvas 


def FaceRecognize(face_arr,score ,ThresholdLiveness , probabilitiesFaceNet, probabilitiesArcFace ,ArcFaceActivate):
    
    scaled = facenet.prewhiten(face_arr)
    scaled_reshape = scaled.reshape(-1, 160,160,3)
    feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
    emb_array = sess.run(embeddings, feed_dict=feed_dict)
    predictions = model.predict_proba(emb_array)
    best_class_indices = np.argmax(predictions, axis=1)
    best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
    bestName = class_names[best_class_indices[0]]
    recognizeScore = float(best_class_probabilities) 

    if best_class_probabilities > probabilitiesFaceNet  and score > ThresholdLiveness:
        if ArcFaceActivate:
            emb1 = arcFacedetector.calc_emb(face_arr)
            emb2 = arcFacedetector.calc_emb(path_DataSet_ArcFace + str(bestName) + "/temp.jpg")    
            if arcFacedetector.get_distance_embeddings(emb1,emb2) < probabilitiesArcFace:               
                return bestName, recognizeScore
            else:
                return "0", recognizeScore
        else:
            return bestName, recognizeScore
    return "0", recognizeScore

def SuggestPoseCounter(face_arr, dataCounter, pose, sizeCount, userID):
    
    suggest = ""

    if dataCounter[0]<sizeCount and pose !="LookUp":
        suggest ="Up"
    if dataCounter[1]<sizeCount and dataCounter[0]>=sizeCount and pose !="LookDown":
        suggest ="Down"
    if dataCounter[2]<sizeCount and dataCounter[1]>=sizeCount and pose !="LookLeft":
        suggest ="Left"
    if dataCounter[3]<sizeCount and dataCounter[2]>=sizeCount and pose !="LookRight":
        suggest ="Right"
    if dataCounter[4]<sizeCount and dataCounter[3]>=sizeCount and pose !="Forward":
        suggest ="Forward"


    if pose == "LookUp" and dataCounter[0]<sizeCount:
        dataCounter[0]+=1
        cv2.imwrite(path_DataSet_FaceNet + userID + "/" + userID+"_"+pose + "_"+str(dataCounter[0]) + ".jpg",face_arr) 
    elif pose == "LookDown" and dataCounter[1]<sizeCount and dataCounter[0] >=sizeCount:
        cv2.imwrite(path_DataSet_FaceNet + userID + "/" + userID+"_"+pose + "_"+str(dataCounter[1]) + ".jpg",face_arr) 
        dataCounter[1]+=1
    elif pose == "LookLeft" and dataCounter[2]<sizeCount and dataCounter[1] >=sizeCount:
        cv2.imwrite(path_DataSet_FaceNet + userID + "/" + userID+"_"+pose + "_"+str(dataCounter[2]) + ".jpg",face_arr) 
        dataCounter[2]+=1
    elif pose == "LookRight" and dataCounter[3]<sizeCount and dataCounter[2] >=sizeCount:
        cv2.imwrite(path_DataSet_FaceNet + userID + "/" + userID+"_"+pose + "_"+str(dataCounter[3]) + ".jpg",face_arr) 
        dataCounter[3]+=1
    elif pose == "Forward" and dataCounter[4]<sizeCount and dataCounter[3] >=sizeCount:
        cv2.imwrite(path_DataSet_FaceNet + userID + "/" + userID+"_"+pose + "_"+str(dataCounter[4]) + ".jpg",face_arr)  
        dataCounter[4]+=1

    return suggest, dataCounter



    



    
    
