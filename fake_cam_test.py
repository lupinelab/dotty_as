# see red_blue.py in the examples dir
import time
import pyfakewebcam
import numpy as np
import cv2

camera = pyfakewebcam.FakeWebcam('/dev/video2', 1280, 960)
capture = cv2.VideoCapture(0, cv2.CAP_V4L2)

while True:
    capture.set(cv2.CAP_PROP_FPS, 30)
    capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    ret, frame = capture.read()
    dotty_frame = np.zeros((960, 1280, 3), dtype=np.uint8)
    if ret:
        greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dim = (128, 96)
        downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
        x = 0
        y = 0
        while y < 96:
            while x < 128:
                coords = ((x*10)+5, (y*10)+5)
                colour = (13, 188, 121)
                cv2.circle(dotty_frame, coords, (255-downFrame[y, x])//32, colour, -1)
                x += 1
            x = 0
            y += 1

    camera.schedule_frame(dotty_frame)
    time.sleep(1/30.0)