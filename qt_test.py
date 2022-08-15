from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QPainterPath, QPicture
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        while True:
            ret, cv_img = cap.read()
            if ret:
                greyFrame = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                dim = (128, 96)
                downsampled = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
                self.change_pixmap_signal.emit(downsampled)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dotty_as")
        self.disply_width = 1280
        self.display_height = 960
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        # create a vertical box layout and the label
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()
        self.show()


    @pyqtSlot(np.ndarray)
    def update_image(self, capture):
        """Updates the image_label with a new opencv image"""
        self.image_label.clear()
        qt_img = self.convert_cv_qt(capture)
        self.image_label.setPixmap(qt_img)

    
    def convert_cv_qt(self, capture):
        """Convert from an opencv image to QPixmap"""
        dotty_frame = np.zeros((960, 1280, 3), dtype=np.uint8)
        image = QPixmap(1280, 960)
        x = 0
        y = 0
        while y < 96:
            while x < 128:
                rect_size = (255-capture[y, x])//32
                rect_start = ((x*10)+(5-int((rect_size)/2)), int(y*10)+(5-int((rect_size)/2)))
                rect_end = ((x*10)+(rect_size), (y*10)+(rect_size))
                colour = (13, 188, 121)
                cv2.rectangle(dotty_frame, rect_start, rect_end, colour, -1)
                x += 1
            x = 0
            y += 1
        height, width, channel = dotty_frame.shape
        qtImg = QImage(dotty_frame.data, width, height, QImage.Format_RGB888)
        qpixmap = QPixmap.fromImage(qtImg)
        return qpixmap


if __name__=="__main__":
    app = QApplication(sys.argv)
    dotty_as = App()
    sys.exit(app.exec_())