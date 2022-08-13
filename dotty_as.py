import cv2
import numpy as np
  
capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
  
# while(True):
capture.set(cv2.CAP_PROP_FPS, 30)
capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)

ret, frame = capture.read()
if ret:
    greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x = 0
    y = 0
    print(type(greyFrame))
    # while x < 640:
    #     area_average = np.average(greyFrame[x:x+9, y:y+9])
    #     print(area_average)
    #     x += 10


cv2.imshow('video gray', greyFrame)
        
    # if cv2.waitKey(1) == 27:
    #         break
  
capture.release()
cv2.destroyAllWindows()