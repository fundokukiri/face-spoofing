import cv2
from typing import List, Tuple
import mediapipe as mp
import numpy as np
from .utils import extract_face

class FaceDetection:
    def __init__(self, max_num_faces: int = 1):
        self.detector = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=max_num_faces, static_image_mode=True
        )
    def __call__(self, frame ,x) -> Tuple[List[np.ndarray], List[List[int]]]:      
        h, w = frame.shape[:2]
        img_h, img_w, img_c = frame.shape
        predictions = self.detector.process(frame[:, :, ::-1])
        boxes = []
        faces = []
        face_3d = []
        face_2d = []
        if predictions.multi_face_landmarks:
            for prediction in predictions.multi_face_landmarks:
                #Face and Bbox detector
                pts = np.array(
                    [(pt.x * w, pt.y * h) for pt in prediction.landmark],
                    dtype=np.float64,
                )
                bbox = np.vstack([pts.min(axis=0), pts.max(axis=0)])
                bbox = np.round(bbox).astype(np.int32)
                face_arr = extract_face(frame, bbox.flatten().tolist())
                boxes.append(bbox)
                faces.append(face_arr)
                if x:
                    #Head Pose Estimation
                    for idx, lm in enumerate(prediction.landmark):
                        if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                            if idx == 1:
                                nose_2d = (lm.x * img_w, lm.y * img_h)
                                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)
                            x, y = int(lm.x * img_w), int(lm.y * img_h)
                            # Get the 2D Coordinates
                            face_2d.append([x, y])
                            # Get the 3D Coordinates
                            face_3d.append([x, y, lm.z])       
                    # Convert it to the NumPy array
                    face_2d = np.array(face_2d, dtype=np.float64)
                    # Convert it to the NumPy array
                    face_3d = np.array(face_3d, dtype=np.float64)
                    # The camera matrix
                    focal_length = 1 * img_w
                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])
                    # The distortion parameters
                    dist_matrix = np.zeros((4, 1), dtype=np.float64)
                    # Solve PnP
                    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                    # Get rotational matrix
                    rmat, jac = cv2.Rodrigues(rot_vec)
                    # Get angles
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                    # Get the y rotation degree
                    x = angles[0] * 360
                    y = angles[1] * 360
                    z = angles[2] * 360          
                    # See where the user's head tilting
                    compare = 12
                    if y < -compare:
                        pose = "LookLeft"
                    elif y > compare:
                        pose = "LookRight"
                    elif x < -compare:
                        pose = "LookDown"
                    elif x > compare:
                        pose = "LookUp"
                    else:
                        pose = "Forward"
        if x:
            try:
                return faces, boxes ,pose
            except:
                return faces, boxes ,"Can't Detected"
        else:
            return faces, boxes




