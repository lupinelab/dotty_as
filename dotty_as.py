import time
import pyfakewebcam
import numpy as np
import cv2
import subprocess

class Dotty_As():
    def __init__(self):
        self.virtualcam_enabled = 0
        self.brightness = 127
        self.contrast = 127
        self.red = 13
        self.green = 188
        self.blue = 121
        self.shape = 0
        self.filled = 1
        self.virtualcam_device = self.get_virtual_cams()[0]
        self.webcam_capture()
        self.preview()
        self.settings()
        self.dotify()
        

    def webcam_capture(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.capture_width=self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.capture_height=self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)


    def preview(self):
        preview = cv2.namedWindow('dotty_as - Preview', cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow('dotty_as - Preview', int(self.capture_width), int(self.capture_height))
        cv2.setMouseCallback('dotty_as - Preview', self.open_settings)

    def get_virtual_cams(self):
        virtual_cams = subprocess.run(["v4l2-ctl --list-devices | grep -A1 v4l2 | grep /dev/video"], capture_output=True, text=True, shell=True).stdout.strip().replace("\t", "").split("\n")
        return virtual_cams

    def settings(self):  
        settings = cv2.namedWindow('dotty_as - Settings', cv2.WINDOW_GUI_EXPANDED)
        cv2.resizeWindow('dotty_as - Settings', 600, 100)
        cv2.createTrackbar('Virtual Camera On/Off','dotty_as - Settings', self.virtualcam_enabled, 1, self.set_virtualcam_enabled)
        cv2.createTrackbar('Contrast','dotty_as - Settings', self.contrast, 255, self.set_contrast)
        cv2.createTrackbar('Brightness','dotty_as - Settings', self.brightness, 255, self.set_brightness)
        cv2.createTrackbar('R','dotty_as - Settings', self.red, 255, self.set_red)
        cv2.createTrackbar('G','dotty_as - Settings', self.green, 255, self.set_green)
        cv2.createTrackbar('B','dotty_as - Settings', self.blue, 255, self.set_blue)
        cv2.createTrackbar('Dot Type: Rectangle/Circle','dotty_as - Settings', self.shape, 1, self.set_shape)
        cv2.createTrackbar('Outline/Solid','dotty_as - Settings', self.filled, 1, self.set_filled)
        for vcam in self.get_virtual_cams():
            cv2.createButton(f"{vcam}", self.set_virtualcam_device, vcam, cv2.QT_PUSH_BUTTON|cv2.QT_NEW_BUTTONBAR, -1)

    def set_virtualcam_enabled(self, e):
        self.virtualcam_enabled = e

    def set_brightness(self, b):
        self.brightness= b

    def set_contrast(self, c):
        self.contrast = c

    def set_red(self, r):
        self.red = r

    def set_blue(self, b):
        self.blue = b

    def set_green(self, g):
        self.green = g

    def set_shape(self, s):
        self.shape = s

    def set_filled(self, f):
        self.filled = f

    def set_virtualcam_device(self, state, vcam):
        self.virtualcam_device = vcam


    def open_settings(self, event, x, y, flags, param):
        if event:
            self.setting_window()


    def rects(self, y, x, frame, canvas, colour, filled):
        rect_size = (frame[y, x])//32
        rect_start = ((x*10)+2, (y*10)+2)
        rect_end = ((x*10)+(rect_size), (y*10)+(rect_size))
        if filled == 0:
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
        elif filled == 1:
            effect = cv2.rectangle(canvas, rect_start, rect_end, colour, -1)


    def circs(self, y, x, frame, canvas, colour, filled):
        radius = int(((frame[y, x])//32)/2)
        centre = ((x*10)+4, (y*10)+4)
        if filled == 0:
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, 1, cv2.FILLED)
        elif filled == 1:
            if radius == 1:
                rect_start = ((x*10)+4, (y*10)+4)
                rect_end = ((x*10)+4, (y*10)+4)
                cv2.rectangle(canvas, rect_start, rect_end, colour, 1)
            cv2.circle(canvas, centre, radius, colour, -1, cv2.FILLED)


    def dotify(self):
        while True:
            if self.virtualcam_enabled == 1:
                if 'virtualcam' in locals():
                    if current_device == self.virtualcam_device: # JW figure out how to swap device
                       pass
                else:
                    virtualcam = pyfakewebcam.FakeWebcam( # JW find suitable /dev/videoX device
                        self.virtualcam_device, 
                        int(self.capture_width*2), 
                        int(self.capture_height*2)
                        )
                    current_device = self.virtualcam_device
            dottyFrame = np.zeros((int(self.capture_height*2), int(self.capture_width*2), 3), dtype=np.uint8)
            self.capture.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            colour = (self.red, self.green, self.blue)
            ret, frame = self.capture.read() 
            if ret:
                greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dim = ((int(self.capture_width/10)*2), (int(self.capture_height/10)*2))
                downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
                x = 0
                y = 0
                while y < dim[1]:
                    while x < dim[0]:
                        if self.shape == 0:
                            self.rects(y, x, downFrame, dottyFrame, colour, self.filled)
                        elif self.shape == 1:
                            self.circs(y, x, downFrame, dottyFrame, colour, self.filled)
                        x += 1
                    x = 0
                    y += 1
            cv2.imshow('dotty_as - Preview', cv2.cvtColor(dottyFrame, cv2.COLOR_BGR2RGB))
            if self.virtualcam_enabled == 1:
                virtualcam.schedule_frame(dottyFrame)
                time.sleep(1/60.0)
            key = cv2.waitKey(1)
            if key == 27:
                capture.release()
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    dotty_as = Dotty_As()
    