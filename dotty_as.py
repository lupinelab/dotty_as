import time
import pyvirtualcam
import numpy as np
import cv2
import sys
import random
import subprocess
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QGroupBox, QComboBox, QSlider, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QObject, QThreadPool, QRunnable

class WorkerSignals(QObject):
    change_pixmap_signal = pyqtSignal(np.ndarray)

class VideoThread(QRunnable):
    def __init__(self, run_flag, virtualcam, resolution, video_settings, virtualcam_settings):
        super(VideoThread, self).__init__()
        self.signals = WorkerSignals()
        self.run_flag = run_flag
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.resolution = resolution
        self.video_settings = video_settings
        self.video_settings["brightness"] = int(self.capture.get(cv2.CAP_PROP_BRIGHTNESS))
        self.video_settings["contrast"] = int(self.capture.get(cv2.CAP_PROP_CONTRAST))
        self.virtualcam_settings = virtualcam_settings
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution["width"])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution["height"])
        self.virtualcam = virtualcam
        self.ascii_symbols = (".", ",", "-", "~", ":", ";", "=", "!", "*", "#", "$", "@")

    @pyqtSlot()
    def run(self):
        while self.run_flag:
            dottyFrame = np.zeros((int(self.resolution["height"]), int(self.resolution["width"]), 3), dtype=np.uint8)
            self.capture.set(cv2.CAP_PROP_CONTRAST, self.video_settings["contrast"])
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.video_settings["brightness"])
            colour = (self.video_settings["red"], self.video_settings["green"], self.video_settings["blue"])
            if self.video_settings["discochaos"] == "Disco":
                colour = (random.randint(0, 255), random.randint(0, 255) ,random.randint(0, 255))
            ret, frame = self.capture.read() 
            if ret:
                greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dim = ((int(self.resolution["width"]/10)), (int(self.resolution["height"]/10)))
                downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
                x = 0
                y = 0
                while y < dim[1]:
                    while x < dim[0]:
                        if self.video_settings["discochaos"] == "Chaos":
                             colour = (random.randint(0, 255), random.randint(0, 255) ,random.randint(0, 255))
                        if self.video_settings["dottype"] == "Square":
                            self.square(y, x, downFrame, dottyFrame, colour, self.video_settings["fill"])
                        elif self.video_settings["dottype"] == "Circle":
                            self.circle(y, x, downFrame, dottyFrame, colour, self.video_settings["fill"])
                        elif self.video_settings["dottype"] == "ASCII":
                            self.ascii(y, x, downFrame, dottyFrame, colour)
                        x += 1
                    x = 0
                    y += 1
            if self.virtualcam_settings["virtualcam_enabled"] == 1:
                self.set_virtualcam()
                self.virtualcam.send(dottyFrame)
                self.virtualcam.sleep_until_next_frame()
            self.signals.change_pixmap_signal.emit(dottyFrame)
        self.capture.release()


    def set_virtualcam(self):
        if self.virtualcam == None:    
                self.virtualcam = pyvirtualcam.Camera(
                        int(self.resolution["width"]), 
                        int(self.resolution["height"]),
                        fps=self.capture.get(cv2.CAP_PROP_FPS),
                        device=self.virtualcam_settings["virtualcam_device"]
                        )
        elif self.virtualcam.device != self.virtualcam_settings["virtualcam_device"]:
                self.virtualcam = pyvirtualcam.Camera(
                        int(self.resolution["width"]), 
                        int(self.resolution["height"]),
                        fps=self.capture.get(cv2.CAP_PROP_FPS),
                        device=self.virtualcam_settings["virtualcam_device"]
                        )
        elif self.virtualcam_settings["virtualcam_enabled"]== 0:
                self.virtualcam = None


    def square(self, y, x, frame, canvas, colour, fill):
        rect_size = (frame[y, x])//32
        rect_start = ((x*10)+2, (y*10)+2)
        rect_end = ((x*10)+(rect_size), (y*10)+(rect_size))
        if self.video_settings["fill"] == "Outline":
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
        elif self.video_settings["fill"] == "Filled":
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, -1)


    def circle(self, y, x, frame, canvas, colour, fill):
        radius = int(((frame[y, x])//32)/2)
        centre = ((x*10)+4, (y*10)+4)
        if self.video_settings["fill"] == "Outline":
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, 1, cv2.LINE_AA)
        elif self.video_settings["fill"] == "Filled":
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, -1, cv2.LINE_AA)


    def ascii(self, y, x, frame, canvas, colour):
        symbol = self.ascii_symbols[(frame[y, x])//22]
        bottom_left = ((x*10)+2, (y*10)+8)
        effect = cv2.putText(canvas, symbol, bottom_left, cv2.FONT_HERSHEY_PLAIN, .6, colour, 1, cv2.LINE_AA)


    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False

class Dotty_As(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.setWindowTitle("dotty_as")
        self.dotify_run_flag = True
        self.virtualcam = None
        self.resolution = {
            "width": 1280,
            "height": 720,
            }
        self.settings = {
            "brightness": 127,
            "contrast": 127,
            "red": 13,
            "green": 188,
            "blue": 121,
            "discochaos": None,
            "dottype": "Square",
            "fill": "Outline",
            }
        self.virtualcam_settings = {
            "virtualcam_enabled": 0, 
            "virtualcam_device": str(self.get_virtual_cams()[0])
            }
        self.threadpool = QThreadPool()
        self.threadpool.setExpiryTimeout(100)
        self.start_worker()
        self.resize_window()
        self.preview = QLabel(self)
        self.preview.mousePressEvent = self.show_settings
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.preview)
        self.show()
        self.settings_window = Dotty_As_Settings()
        self.init_settings_values()
        self.settings_window.show()


    def update_resolution(self, new_res):
        self.dotify.stop()
        self.threadpool.waitForDone()
        self.resolution = new_res
        self.start_worker()
        self.resize_window()

    def start_worker(self):
        self.dotify = VideoThread(run_flag=self.dotify_run_flag, virtualcam=self.virtualcam, resolution=self.resolution, video_settings=self.settings, virtualcam_settings=self.virtualcam_settings)
        self.dotify.setAutoDelete(True)
        self.dotify.signals.change_pixmap_signal.connect(self.update_image)
        self.threadpool.start(self.dotify)

    def closeEvent(self, event):
        self.dotify.stop()
        self.threadpool.waitForDone()
        self.settings_window.close()
        event.accept()

    def resize_window(self):
        self.resize(
            self.resolution["width"],
            self.resolution["height"]
            )

    def init_settings_values(self):
        self.settings_window.width_input.setText(str(self.resolution["width"]))
        self.settings_window.height_input.setText(str(self.resolution["height"]))
        self.settings_window.brightnessslider.setValue(self.settings["brightness"])
        self.settings_window.brightnessvalue.setText(str(self.settings["brightness"]))
        self.settings_window.contrastslider.setValue(self.settings["contrast"])
        self.settings_window.contrastvalue.setText(str(self.settings["contrast"]))

    def show_settings(self, event):
        self.settings_window.resize(400, 600)
        self.settings_window.show()
        self.settings_window.activateWindow()



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
        self.resolution()
        self.virtualcam()
        self.brightness()
        self.contrast()
        self.colour()
        self.discochaos()
        self.dottype()

    def resolution(self):
        self.resolution_groupbox = QGroupBox("Resolution")
        self.mainlayout.addWidget(self.resolution_groupbox)
        self.resolution_layout = QHBoxLayout()
        self.resolution_groupbox.setLayout(self.resolution_layout)
        self.width_label = QLabel("W")
        self.width_input = QLineEdit()
        self.width_input.setMaxLength(4)
        self.multiplier_label = QLabel("x")
        self.height_label = QLabel("H")
        self.height_input = QLineEdit()
        self.height_input.setMaxLength(4)
        self.set_resolution_button = QPushButton("Set")
        self.resolution_layout.addWidget(self.width_label)
        self.resolution_layout.addWidget(self.width_input)
        self.resolution_layout.addWidget(self.multiplier_label)
        self.resolution_layout.addWidget(self.height_label)
        self.resolution_layout.addWidget(self.height_input)
        self.resolution_layout.addWidget(self.set_resolution_button)
        self.width_input.setText("1280")
        self.height_input.setText("720")
        self.set_resolution_button.clicked.connect(self.set_resolution)

    def virtualcam(self):
        self.virtualcam_groupbox = QGroupBox("Virtual Camera")
        self.mainlayout.addWidget(self.virtualcam_groupbox)
        self.virtualcam_layout = QVBoxLayout()
        self.virtualcam_groupbox.setLayout(self.virtualcam_layout)
        # Device
        self.virtualcamselect_combobox = QComboBox()
        self.virtualcamselect_combobox.addItems(self.get_virtual_cams())
        self.virtualcam_layout.addWidget(self.virtualcamselect_combobox)
        self.virtualcamselect_combobox.activated[str].connect(self.set_virtualcamselect)     
        # On/Off
        self.virtualcamtoggle_layout = QHBoxLayout()
        self.virtualcam_layout.addLayout(self.virtualcamtoggle_layout)
        self.virtualcamtoggle_on = QRadioButton("On")
        self.virtualcamtoggle_off = QRadioButton("Off")
        self.virtualcamtoggle_off.setChecked(True)
        self.virtualcamtoggle_layout.addWidget(self.virtualcamtoggle_on)
        self.virtualcamtoggle_layout.addWidget(self.virtualcamtoggle_off)
        self.virtualcamtoggle_off.clicked.connect(lambda:self.set_virtualcamtoggle(self.virtualcamtoggle_off))
        self.virtualcamtoggle_on.clicked.connect(lambda:self.set_virtualcamtoggle(self.virtualcamtoggle_on))

    def brightness(self):
        self.brightnessslider_groupbox = QGroupBox("Brightness")
        self.mainlayout.addWidget(self.brightnessslider_groupbox)
        self.brightnessslider_layout = QHBoxLayout()
        self.brightnessslider_groupbox.setLayout(self.brightnessslider_layout)
        self.brightnessvalue = QLabel()
        self.brightnessslider = QSlider(Qt.Horizontal)
        self.brightnessslider.setMinimum(0)
        self.brightnessslider.setMaximum(255)
        self.brightnessslider_layout.addWidget(self.brightnessvalue)
        self.brightnessslider_layout.addWidget(self.brightnessslider)
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
        self.colourslider_groupbox.setCheckable(True)
        self.colourslider_groupbox.setChecked(True)
        self.mainlayout.addWidget(self.colourslider_groupbox)
        self.colourslider_layout = QVBoxLayout()
        self.colourslider_groupbox.setLayout(self.colourslider_layout)
        self.colourslider_groupbox.toggled.connect(lambda:self.set_discochaos_checkbox(self.colourslider_groupbox))
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

    def discochaos(self):      
        self.discochaos_groupbox = QGroupBox("Disco/Chaos")
        self.discochaos_groupbox.setCheckable(True)
        self.discochaos_groupbox.setChecked(False)
        self.mainlayout.addWidget(self.discochaos_groupbox)
        self.discochaos_layout = QHBoxLayout()
        self.discochaos_groupbox.setLayout(self.discochaos_layout)
        self.discochaos_disco = QRadioButton("Disco")
        self.discochaos_chaos = QRadioButton("Chaos")
        self.discochaos_disco.setChecked(True)
        self.discochaos_layout.addWidget(self.discochaos_disco)
        self.discochaos_layout.addWidget(self.discochaos_chaos)
        self.discochaos_groupbox.toggled.connect(lambda:self.set_colour_checkbox(self.discochaos_groupbox))
        self.discochaos_disco.clicked.connect(lambda:self.set_discochaos(self.discochaos_disco))
        self.discochaos_chaos.clicked.connect(lambda:self.set_discochaos(self.discochaos_chaos))

    def dottype(self):
        self.dottype_groupbox = QGroupBox("Dot Type")
        self.mainlayout.addWidget(self.dottype_groupbox)
        self.dottype_layout = QVBoxLayout()
        self.dottype_groupbox.setLayout(self.dottype_layout)
        # Shape
        self.dotshape_groupbox = QGroupBox("Type")
        self.dottype_layout.addWidget(self.dotshape_groupbox)
        self.dotshape_layout = QHBoxLayout()
        self.dotshape_groupbox.setLayout(self.dotshape_layout)
        self.dotshape_square = QRadioButton("Square")
        self.dotshape_circle = QRadioButton("Circle")
        self.dotshape_ascii = QRadioButton("ASCII")
        self.dotshape_square.setChecked(True)
        self.dotshape_layout.addWidget(self.dotshape_square)
        self.dotshape_layout.addWidget(self.dotshape_circle)
        self.dotshape_layout.addWidget(self.dotshape_ascii)
        self.dotshape_square.clicked.connect(lambda:self.set_dotshape(self.dotshape_square))
        self.dotshape_circle.clicked.connect(lambda:self.set_dotshape(self.dotshape_circle))
        self.dotshape_ascii.clicked.connect(lambda:self.set_dotshape(self.dotshape_ascii))
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
        self.dotfill_filled.clicked.connect(lambda:self.set_dotfill(self.dotfill_filled))
        self.dotfill_outline.clicked.connect(lambda:self.set_dotfill(self.dotfill_outline))


    def set_resolution(self):
        new_res = {
            "width": int(self.width_input.text()),
            "height": int(self.height_input.text()),
            }
        dotty_as.update_resolution(new_res)

    
    def set_virtualcamtoggle(self, button):
        if button.text() == "On":
            self.resolution_groupbox.setEnabled(False)
            dotty_as.virtualcam_settings["virtualcam_enabled"] = 1
        if button.text() == "Off":
            self.resolution_groupbox.setEnabled(True)
            dotty_as.virtualcam_settings["virtualcam_enabled"] = 0

    def set_virtualcamselect(self):
        dotty_as.virtualcam_settings["virtualcam_device"] = self.virtualcamselect_combobox.currentText()

    def set_brightness(self):
        self.brightnessvalue.setText(str(self.brightnessslider.value()))
        dotty_as.settings["brightness"] = self.brightnessslider.value()

    def set_contrast(self):
        self.contrastvalue.setText(str(self.contrastslider.value()))
        dotty_as.settings["contrast"] = self.contrastslider.value()

    def set_red(self):
        self.redvalue.setText(str(self.redslider.value()))
        dotty_as.settings["red"] = self.redslider.value()
    
    def set_green(self):
        self.greenvalue.setText(str(self.greenslider.value()))
        dotty_as.settings["green"] = self.greenslider.value()

    def set_blue(self):
        self.bluevalue.setText(str(self.blueslider.value()))
        dotty_as.settings["blue"] = self.blueslider.value()

    def set_discochaos_checkbox(self, checkbox):
        if checkbox.isChecked():
            self.discochaos_groupbox.setChecked(False)
            dotty_as.settings["discochaos"] = None
        if checkbox.isChecked() == False:
            self.discochaos_groupbox.setChecked(True)
            if self.discochaos_chaos.isChecked():
                dotty_as.settings["discochaos"] = self.discochaos_chaos.text()
            if self.discochaos_disco.isChecked():
                dotty_as.settings["discochaos"] = self.discochaos_disco.text()

    def set_colour_checkbox(self, checkbox):
        if checkbox.isChecked():
            self.colourslider_groupbox.setChecked(False)
            if self.discochaos_chaos.isChecked():
                dotty_as.settings["discochaos"] = self.discochaos_chaos.text()
            if self.discochaos_disco.isChecked():
                dotty_as.settings["discochaos"] = self.discochaos_disco.text()
        if checkbox.isChecked() == False:
            dotty_as.settings["discochaos"] = None
            self.colourslider_groupbox.setChecked(True)

    def set_discochaos(self, button):
        dotty_as.settings["discochaos"] = button.text()

    def set_dotshape(self, button):
        dotty_as.settings["dottype"] = button.text()
        if button.text() == "ASCII":
            self.dotfill_groupbox.setEnabled(False)
        if button.text() != "ASCII":
            self.dotfill_groupbox.setEnabled(True)
    
    def set_dotfill(self, button):
        dotty_as.settings["fill"] = button.text()

    def get_virtual_cams(self):
        virtual_cams = subprocess.run(["v4l2-ctl --list-devices | grep -A1 v4l2 | grep /dev/video"], capture_output=True, text=True, shell=True).stdout.strip().replace("\t", "").split("\n")
        return virtual_cams


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dotty_as = Dotty_As()
    sys.exit(app.exec_())