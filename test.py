import cv2
from imutils.video import VideoStream ,WebcamVideoStream

vs = cv2.VideoCapture(0 , cv2.CAP_DSHOW)

while True:
    stauts,frame = vs.read()

    cv2.imshow("Test App", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

vs.release()
cv2.destroyAllWindows