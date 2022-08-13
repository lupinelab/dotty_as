import cv2
import numpy as np
  
capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
  
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
capture.set(cv2.CAP_PROP_FPS, 30)
capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)

ret, frame = capture.read()
if ret:
    greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x = 0
    y = 0
    print(greyFrame)
    while y < 480:
        while x < 480:
            area_average = np.average(greyFrame[x:x+9, y:y+9])
            
            x += 10
        x = 0
        y += 10


capture.release()
cv2.destroyAllWindows()