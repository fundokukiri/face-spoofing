import os
import cv2
import numpy as np
import torch
import pyshine as ps
from PIL import Image
from torch.nn.functional import interpolate
from torchvision import transforms as T


def imresample(img, sz):
    im_data = interpolate(img, size=sz, mode="area")
    return im_data


def get_size(img):
    if isinstance(img, (np.ndarray, torch.Tensor)):
        return img.shape[1::-1]
    else:
        return img.size


def crop_resize(img, box, image_size):
    if isinstance(img, np.ndarray):
        img = img[box[1] : box[3], box[0] : box[2]]
        out = cv2.resize(
            img, (image_size, image_size), interpolation=cv2.INTER_AREA
        ).copy()
    elif isinstance(img, torch.Tensor):
        img = img[box[1] : box[3], box[0] : box[2]]
        out = (
            imresample(
                img.permute(2, 0, 1).unsqueeze(0).float(), (image_size, image_size)
            )
            .byte()
            .squeeze(0)
            .permute(1, 2, 0)
        )
    else:
        out = img.crop(box).copy().resize((image_size, image_size), Image.BILINEAR)
    return out


def save_img(img, path):
    if isinstance(img, np.ndarray):
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    else:
        img.save(path)


def extract_face(img, box, image_size=160, margin= 80, save_path=None):
    margin = [
        margin * (box[2] - box[0]) / (image_size - margin),
        margin * (box[3] - box[1]) / (image_size - margin),
    ]
    raw_image_size = get_size(img)
    box = [
        int(max(box[0] - margin[0] / 2, 0)),
        int(max(box[1] - margin[1] / 2, 0)),
        int(min(box[2] + margin[0] / 2, raw_image_size[0])),
        int(min(box[3] + margin[1] / 2, raw_image_size[1])),
    ]

    face = crop_resize(img, box, image_size)

    if save_path is not None:
        os.makedirs(os.path.dirname(save_path) + "/", exist_ok=True)
        save_img(face, save_path)

    return face
def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)

def visualize_results_register(
    frame: np.ndarray, box: np.ndarray,
    BORDER_COLOR = (224, 224, 224),
    BGR_COLOR =  (201, 201, 44),
    txt_offset = 1,
    txt_width = 1,
    res_text = ""
):
    cv2.putText(frame, res_text, (box[0][0], box[0][1]-txt_offset), 
                cv2.FONT_HERSHEY_COMPLEX, 1, BGR_COLOR, txt_width)
    return frame
def visualize_results_recognize(
    frame: np.ndarray, box: np.ndarray, checkSpoof:str  ,userName:str ,
    BORDER_COLOR = (224, 224, 224),
    BGR_COLOR =  (201, 201, 44),
):
    draw_border(frame, 
    (box[0][0], box[0][1]),
    (box[1][0], box[1][1]),
    BORDER_COLOR, 1,10,20)

    cv2.rectangle(frame,
        (box[0][0], box[0][1] -5),
        (box[1][0], box[0][1] - 35),
        BORDER_COLOR,-1,)
    cv2.putText(
        frame,
        checkSpoof,
        (box[0][0], box[0][1] - 10),                                                                                                                                                                                                                                                                                                                                                                                                                                               
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    cv2.rectangle(
        frame,
        (box[0][0] - 40, box[1][1] +5),
        (box[1][0] + 40, box[1][1] + 35),
        BGR_COLOR,
        -1,
    )
    cv2.putText(
        frame,
        userName,
        (box[0][0]- 35, box[1][1] + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    return frame

def visualize_results(
    frame: np.ndarray, box: np.ndarray,
    BORDER_COLOR = (224, 224, 224),
    BGR_COLOR =  (201, 201, 44),
):
    draw_border(frame, 
    (box[0][0], box[0][1]),
    (box[1][0], box[1][1]),
    BORDER_COLOR, 2,10,20)

    return frame
