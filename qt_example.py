from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRect
import sys
import cv2
import numpy as np

class Dotty_as(QWidget):

    def __init__(self):
        super().__init__()

        self.init()

    def init(self):
        self.setGeometry(480, 480, 1280, 960)
        self.setWindowTitle('dotty_as')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.captureCamera(qp)
        

    def captureCamera(self, qp):
        capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        # while True:
        capture.set(cv2.CAP_PROP_FPS, 30)
        capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        ret, frame = capture.read()
        if ret:
            greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dim = (128, 96)
            downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
            ret, invert = cv2.threshold(greyFrame,100,255,cv2.THRESH_BINARY_INV)
            x = 0
            y = 0
            while y < 96:
                while x < 128:
                    if downFrame[y, x] < 51:
                        self.drawDot(qp, x*10, y*10, 8, 8)    
                    elif downFrame[y, x] >= 51 and downFrame[y, x] < 102:
                        self.drawDot(qp, x*10, y*10, 6, 6)
                    elif downFrame[y, x] >= 102 and downFrame[y, x] < 153:
                        self.drawDot(qp, x*10, y*10, 5, 5)
                    # elif area_average > 153 and area_average < 204:
                    #     self.drawDot(qp, x, y, 3, 3)
                    elif downFrame[y, x] >= 153:
                        self.drawDot(qp, x*10, y*10, 1, 1) 
                    x += 1
                x = 0
                y += 1
        qp.end()

    
    def drawDot(self, qp, x, y, width, height):
        #size = self.size()
        dot = QPainterPath()
        dot.addRoundedRect(x, y, width, height, 2, 2)
        qp.fillPath(dot, QColor(13, 188, 121))
        
            # while y < 480:
            #     while x < 480:
            #         area_average = np.average(greyFrame[x:x+9, y:y+9])
            #         print(area_average)
            #         if area_average > 85:
            #             dot.addRoundedRect(x, y, 2, 2, 1, 1)
            #             qp.fillPath(dot, QColor(13, 188, 121))
            #         elif area_average > 85 and area_average < 170:
            #             dot.addRoundedRect(x, y, 5, 5, 2, 2)
            #             qp.fillPath(dot, QColor(13, 188, 121))
            #         elif area_average > 170:
            #             dot.addRoundedRect(x, y, 8, 8, 2, 2)
            #             qp.fillPath(dot, QColor(13, 188, 121))
            #         x += 10
            #     x = 0
            #     y += 10
        # dot.addRoundedRect(0, 0, 10, 10, 5, 5)
        # qp.fillPath(dot, QColor(13, 188, 121))
        # qp.drawRoundedRect(100, 20, 100, 100, 10, 10)



def main():
    app = QApplication(sys.argv)
    dotty_as = Dotty_as()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()