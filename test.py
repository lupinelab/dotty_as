from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QPainterPath
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from time import sleep


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FPS, 1)
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
        self.update()



    @pyqtSlot(np.ndarray)
    def update_image(self, capture):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(capture)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, capture):
        """Convert from an opencv image to QPixmap"""
        image = QPixmap(1280,960)
        painter = QPainter(image)
        path = QPainterPath()
        dot_colour = QColor(13, 188, 121)
        x = 0
        y = 0
        while y < 96:
            while x < 128:
                if capture[y, x] < 51:
                    path.addRoundedRect(x*10, y*10, 8, 8, 2, 2)
                    painter.fillPath(path, dot_colour)
                # elif 51 <= capture[y, x] < 102:
                #     path.addRoundedRect(x*5, y*5, 6, 6, 2, 2)
                #     painter.fillPath(path, dot_colour)
                # elif capture[y, x] >= 102 and capture[y, x] < 153:
                #     path.addRoundedRect(x*5, y*5, 5, 5, 2, 2)
                #     painter.fillPath(path, dot_colour)
                # elif capture[y, x] > 153 and capture[y, x] < 204:
                #     path.addRoundedRect(x*5, y*5, 3, 3, 2, 2)
                #     painter.fillPath(path, dot_colour)
                # elif capture[y, x] >= 153:
                #     path.addRoundedRect(x*5, y*5, 1, 1, 2, 2)
                #     painter.fillPath(path, dot_colour) 
                x += 1
            x = 0
            y += 1
        painter.end()
        # rgb_image = cv2.cvtColor(capture, cv2.COLOR_BGR2RGB)
        # h, w, ch = rgb_image.shape
        # bytes_per_line = ch * w
        # convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap(image)

if __name__=="__main__":
    app = QApplication(sys.argv)
    dotty_as = App()
    dotty_as.show()
    sys.exit(app.exec_())