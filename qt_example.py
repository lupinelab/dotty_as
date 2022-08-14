from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRect, QTimer
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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.redraw)
        self.timer.start(100)

    def redraw(self):
        self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.captureCamera(qp)
        

    def captureCamera(self, qp):
        capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        capture.set(cv2.CAP_PROP_FPS, 30)
        capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        ret, frame = capture.read()
        if ret:
            greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dim = (128, 96)
            downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
            x = 0
            y = 0
            while y < 96:
                while x < 128:
                    self.drawDot(qp, x*10, y*10, (255-downFrame[y, x])//32, (255-downFrame[y, x])//32)
                    x += 1
                x = 0
                y += 1
        qp.end()

    def drawDot(self, qp, x, y, width, height):
        dot = QPainterPath()
        dot.addRoundedRect(x, y, width, height, 2, 2)
        qp.fillPath(dot, QColor(13, 188, 121))


def main():
    app = QApplication(sys.argv)
    dotty_as = Dotty_as()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()