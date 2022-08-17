import time
import pyvirtualcam
import numpy as np
import cv2
import sys
import subprocess
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QComboBox, QSlider
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    def __init__(self, capture, video_settings, virtualcam_settings):
        super().__init__()
        self._run_flag = True
        self.capture = capture
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.capture_width = video_settings["cap_width"]
        self.capture_height = video_settings["cap_height"]
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_height)
        self.brightness = video_settings["brightness"]
        self.contrast = video_settings["contrast"]
        self.red = video_settings["red"]
        self.green = video_settings["green"]
        self.blue = video_settings["blue"]
        self.shape = video_settings["shape"]
        self.fill = video_settings["fill"]
        self.virtualcam_enabled = virtualcam_settings["virtualcam_enabled"]
        self.virtualcam_device = virtualcam_settings["virtualcam_device"]
        self.virtualcam = None
        self.set_virtualcam_status()
    
    @pyqtSlot(dict)
    def update_image_settings(self, settings):
        self.brightness = settings["brightness"]
        self.contrast = settings["contrast"]
        self.red = settings["red"]
        self.green = settings["green"]
        self.blue = settings["blue"]
        self.shape = settings["shape"]
        self.fill = settings["fill"]
    
    @pyqtSlot(dict)
    def update_virtualcam_settings(self, settings):
        self.virtualcam_enabled = settings["virtualcam_enabled"]
        self.virtualcam_device = settings["virtualcam_device"]
        self.set_virtualcam_status()


    def set_virtualcam_status(self):
        if self.virtualcam_enabled == 1:
            self.virtualcam = pyvirtualcam.Camera(
                        int(self.capture_width), 
                        int(self.capture_height),
                        fps=self.capture.get(cv2.CAP_PROP_FPS),
                        device=self.virtualcam_device
                        )

    def rects(self, y, x, frame, canvas, colour, fill):
        rect_size = (frame[y, x])//32
        rect_start = ((x*10)+2, (y*10)+2)
        rect_end = ((x*10)+(rect_size), (y*10)+(rect_size))
        if fill == "Outline":
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
        elif fill == "Filled":
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, -1)


    def circs(self, y, x, frame, canvas, colour, fill):
        radius = int(((frame[y, x])//32)/2)
        centre = ((x*10)+4, (y*10)+4)
        if fill == "Outline":
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, 1, cv2.LINE_AA)
        elif fill == "Filled":
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, -1, cv2.LINE_AA)

    def run(self):
        while self._run_flag:
            dottyFrame = np.zeros((int(self.capture_height), int(self.capture_width), 3), dtype=np.uint8)
            self.capture.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            colour = (self.red, self.green, self.blue)
            ret, frame = self.capture.read() 
            if ret:
                greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dim = ((int(self.capture_width/10)), (int(self.capture_height/10)))
                downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
                x = 0
                y = 0
                while y < dim[1]:
                    while x < dim[0]:
                        if self.shape == "Square":
                            self.rects(y, x, downFrame, dottyFrame, colour, self.fill)
                        elif self.shape == "Circle":
                            self.circs(y, x, downFrame, dottyFrame, colour, self.fill)
                        x += 1
                    x = 0
                    y += 1
            if self.virtualcam_enabled == 1:
                self.virtualcam.send(dottyFrame)
                self.virtualcam.sleep_until_next_frame()
            self.change_pixmap_signal.emit(dottyFrame)
        self.capture.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class Dotty_As(QMainWindow):
    update_settings_signal = pyqtSignal(dict)
    update_virtualcam_signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dotty_as")
        self.capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.settings = {
            "cap_width": 1280,
            "cap_height": 720,
            "brightness": 127,
            "contrast": 127,
            "red": 13,
            "green": 188,
            "blue": 121,
            "shape": "Square",
            "fill": "Outline",
            }
        self.virtualcam_settings = {
            "virtualcam_enabled": 0, 
            "virtualcam_device": str(self.get_virtual_cams()[0])
            }
        self.thread = VideoThread(capture=self.capture, video_settings=self.settings, virtualcam_settings=self.virtualcam_settings)
        self.update_settings_signal.connect(self.thread.update_image_settings)
        self.update_virtualcam_signal.connect(self.thread.update_virtualcam_settings)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()
        self.resize(
            int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
        self.preview = QLabel(self)
        self.preview.mousePressEvent = self.show_settings
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.preview)
        self.settings_window = Dotty_As_Settings()
        self.settings_window.show()


    def closeEvent(self, event):
        self.settings_window.close()
        self.thread.stop()
        event.accept()


    def show_settings(self, event):
        self.settings_window.resize(400, 600)
        self.settings_window.show()

    def update_settings(self):
        self.update_settings_signal.emit(self.settings)

    def update_virtualcam_settings(self):
        self.update_virtualcam_signal.emit(self.virtualcam_settings)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_frame):
        """Updates the image_label with a new opencv image"""
        qt_frame = self.convert_cv_qt(cv_frame)
        self.preview.resize(self.width(), self.height())
        self.preview.setPixmap(qt_frame)
    
    def convert_cv_qt(self, cv_frame):
        """Convert from an opencv image to QPixmap"""
        h, w, ch = cv_frame.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(cv_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
        

    def get_virtual_cams(self):
        virtual_cams = subprocess.run(["v4l2-ctl --list-devices | grep -A1 v4l2 | grep /dev/video"], capture_output=True, text=True, shell=True).stdout.strip().replace("\t", "").split("\n")
        return virtual_cams

class Dotty_As_Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dotty_as - Settings")
        self.resize(400, 0)
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        self.virtualcamtoggle()
        self.virtualcamselect()
        self.brightness()
        self.contrast()
        self.colour()
        self.dottype()

    def virtualcamtoggle(self):
        self.virtualcamtoggle_groupbox = QGroupBox("Virtual Camera")
        self.mainlayout.addWidget(self.virtualcamtoggle_groupbox)
        self.virtualcamtoggle_layout = QHBoxLayout()
        self.virtualcamtoggle_groupbox.setLayout(self.virtualcamtoggle_layout)
        self.virtualcamtoggle_on = QRadioButton("On")
        self.virtualcamtoggle_off = QRadioButton("Off")
        self.virtualcamtoggle_off.setChecked(True)
        self.virtualcamtoggle_layout.addWidget(self.virtualcamtoggle_on)
        self.virtualcamtoggle_layout.addWidget(self.virtualcamtoggle_off)
        self.virtualcamtoggle_off.toggled.connect(lambda:self.set_virtualcamtoggle(self.virtualcamtoggle_off))
        self.virtualcamtoggle_on.toggled.connect(lambda:self.set_virtualcamtoggle(self.virtualcamtoggle_on))
    
    def virtualcamselect(self):
        self.virtualcamselect_groupbox = QGroupBox("Select Virtual Camera")
        self.mainlayout.addWidget(self.virtualcamselect_groupbox)
        self.virtualcamselect_layout = QHBoxLayout()
        self.virtualcamselect_groupbox.setLayout(self.virtualcamselect_layout)      
        self.virtualcamselect_combobox = QComboBox()
        self.virtualcamselect_combobox.addItems(self.get_virtual_cams())
        self.virtualcamselect_layout.addWidget(self.virtualcamselect_combobox)
        self.virtualcamselect_combobox.activated[str].connect(self.set_virtualcamselect)

    def brightness(self):
        self.brightnessslider_groupbox = QGroupBox("Brightness")
        self.mainlayout.addWidget(self.brightnessslider_groupbox)
        self.brightnessslider_layout = QHBoxLayout()
        self.brightnessslider_groupbox.setLayout(self.brightnessslider_layout)
        self.brightnessvalue = QLabel(str(127))
        self.brightnessslider = QSlider(Qt.Horizontal)
        self.brightnessslider.setMinimum(0)
        self.brightnessslider.setMaximum(255)
        self.brightnessslider_layout.addWidget(self.brightnessvalue)
        self.brightnessslider_layout.addWidget(self.brightnessslider)
        self.brightnessslider.setValue(127)
        self.brightnessslider.sliderMoved.connect(self.set_brightness)

    def contrast(self):
        self.contrastslider_groupbox = QGroupBox("Contrast")
        self.mainlayout.addWidget(self.contrastslider_groupbox)
        self.contrastslider_layout = QHBoxLayout()
        self.contrastslider_groupbox.setLayout(self.contrastslider_layout)
        self.contrastvalue = QLabel(str(127))
        self.contrastslider = QSlider(Qt.Horizontal)
        self.contrastslider.setMinimum(0)
        self.contrastslider.setMaximum(255)
        self.contrastslider_layout.addWidget(self.contrastvalue)
        self.contrastslider_layout.addWidget(self.contrastslider)
        self.contrastslider.setValue(127)
        self.contrastslider.sliderMoved.connect(self.set_contrast)

    def colour(self):
        self.colourslider_groupbox = QGroupBox("Colour")
        self.mainlayout.addWidget(self.colourslider_groupbox)
        self.colourslider_layout = QVBoxLayout()
        self.colourslider_groupbox.setLayout(self.colourslider_layout)
        # Red
        self.redslider_groupbox = QGroupBox("Red")
        self.colourslider_layout.addWidget(self.redslider_groupbox)
        self.redslider_layout = QHBoxLayout()
        self.redslider_groupbox.setLayout(self.redslider_layout)
        self.redvalue = QLabel(str(13))
        self.redslider = QSlider(Qt.Horizontal)
        self.redslider.setMinimum(0)
        self.redslider.setMaximum(255)
        self.redslider_layout.addWidget(self.redvalue)
        self.redslider_layout.addWidget(self.redslider)
        self.redslider.setValue(13)
        self.redslider.sliderMoved.connect(self.set_red)
        # Green
        self.greenslider_groupbox = QGroupBox("Green")
        self.colourslider_layout.addWidget(self.greenslider_groupbox)
        self.greenslider_layout = QHBoxLayout()
        self.greenslider_groupbox.setLayout(self.greenslider_layout)
        self.greenvalue = QLabel(str(188))
        self.greenslider = QSlider(Qt.Horizontal)
        self.greenslider.setMinimum(0)
        self.greenslider.setMaximum(255)
        self.greenslider_layout.addWidget(self.greenvalue)
        self.greenslider_layout.addWidget(self.greenslider)
        self.greenslider.setValue(188)
        self.greenslider.sliderMoved.connect(self.set_green)
        # Blue
        self.blueslider_groupbox = QGroupBox("Blue")
        self.colourslider_layout.addWidget(self.blueslider_groupbox)
        self.blueslider_layout = QHBoxLayout()
        self.blueslider_groupbox.setLayout(self.blueslider_layout)
        self.bluevalue = QLabel(str(121))
        self.blueslider = QSlider(Qt.Horizontal)
        self.blueslider.setMinimum(0)
        self.blueslider.setMaximum(255)
        self.blueslider_layout.addWidget(self.bluevalue)
        self.blueslider_layout.addWidget(self.blueslider)
        self.blueslider.setValue(121)
        self.blueslider.sliderMoved.connect(self.set_blue)

    def dottype(self):
        self.dottype_groupbox = QGroupBox("Dot Type")
        self.mainlayout.addWidget(self.dottype_groupbox)
        self.dottype_layout = QVBoxLayout()
        self.dottype_groupbox.setLayout(self.dottype_layout)
        # Shape
        self.dotshape_groupbox = QGroupBox("Shape")
        self.dottype_layout.addWidget(self.dotshape_groupbox)
        self.dotshape_layout = QHBoxLayout()
        self.dotshape_groupbox.setLayout(self.dotshape_layout)
        self.dotshape_square = QRadioButton("Square")
        self.dotshape_circle = QRadioButton("Circle")
        self.dotshape_square.setChecked(True)
        self.dotshape_layout.addWidget(self.dotshape_square)
        self.dotshape_layout.addWidget(self.dotshape_circle)
        self.dotshape_square.toggled.connect(lambda:self.set_dotshape(self.dotshape_square))
        self.dotshape_circle.toggled.connect(lambda:self.set_dotshape(self.dotshape_circle))
        # Fill/Outline
        self.dotfill_groupbox = QGroupBox("Fill")
        self.dottype_layout.addWidget(self.dotfill_groupbox)
        self.dotfill_layout = QHBoxLayout()
        self.dotfill_groupbox.setLayout(self.dotfill_layout)
        self.dotfill_filled = QRadioButton("Filled")
        self.dotfill_outline = QRadioButton("Outline")
        self.dotfill_outline.setChecked(True)
        self.dotfill_layout.addWidget(self.dotfill_filled)
        self.dotfill_layout.addWidget(self.dotfill_outline)
        self.dotfill_filled.toggled.connect(lambda:self.set_dotfill(self.dotfill_filled))
        self.dotfill_outline.toggled.connect(lambda:self.set_dotfill(self.dotfill_outline))

    def set_virtualcamtoggle(self, button):
        if button.text() == "On":
            dotty_as.virtualcam_settings["virtualcam_enabled"] = 1
        if button.text() == "Off":
            dotty_as.virtualcam_settings["virtualcam_enabled"] = 0
        dotty_as.update_virtualcam_settings()

    def set_virtualcamselect(self):
        dotty_as.virtualcam_settings["virtualcam_device"] = self.virtualcamselect_combobox.currentText()
        dotty_as.update_virtualcam_settings()

    def set_brightness(self):
        self.brightnessvalue.setText(str(self.brightnessslider.value()))
        dotty_as.settings["brightness"] = self.brightnessslider.value()
        dotty_as.update_settings()

    def set_contrast(self):
        self.contrastvalue.setText(str(self.contrastslider.value()))
        dotty_as.settings["contrast"] = self.contrastslider.value()
        dotty_as.update_settings()

    def set_red(self):
        self.redvalue.setText(str(self.redslider.value()))
        dotty_as.settings["red"] = self.redslider.value()
        dotty_as.update_settings()
    
    def set_green(self):
        self.greenvalue.setText(str(self.greenslider.value()))
        dotty_as.settings["green"] = self.greenslider.value()
        dotty_as.update_settings()

    def set_blue(self):
        self.bluevalue.setText(str(self.blueslider.value()))
        dotty_as.settings["blue"] = self.blueslider.value()
        dotty_as.update_settings()

    def set_dotshape(self, button):
        dotty_as.settings["shape"] = button.text()
        dotty_as.update_settings()
    
    def set_dotfill(self, button):
        dotty_as.settings["fill"] = button.text()
        dotty_as.update_settings()

    def get_virtual_cams(self):
        virtual_cams = subprocess.run(["v4l2-ctl --list-devices | grep -A1 v4l2 | grep /dev/video"], capture_output=True, text=True, shell=True).stdout.strip().replace("\t", "").split("\n")
        return virtual_cams


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dotty_as = Dotty_As()
    dotty_as.show()
    sys.exit(app.exec_())
    
    
    