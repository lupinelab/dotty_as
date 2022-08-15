import time
import pyfakewebcam
import numpy as np
import cv2
import sys


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
        self.webcam_capture()
        self.preview()
        self.setting_window()
        self.dotify()
        print(cv2.getTrackbarPos('Contrast','dotty_as - Settings'))
        

    def webcam_capture(self):
        self.capture = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.capture.set(cv2.CAP_PROP_FPS, 60)
        self.capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)


    def preview(self):
        preview_window = cv2.namedWindow('dotty_as - Preview')
        cv2.setMouseCallback('dotty_as - Preview', self.open_settings)


    def setting_window(self):  
        setting_window = cv2.namedWindow('dotty_as - Settings', cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('dotty_as - Settings', 800, 200)
        cv2.createTrackbar('Virtual Camera','dotty_as - Settings', self.virtualcam_enabled, 1, self.set_virtualcam_enabled)
        cv2.createTrackbar('Contrast','dotty_as - Settings', self.contrast, 255, self.set_contrast)
        cv2.createTrackbar('Brightness','dotty_as - Settings', self.brightness, 255, self.set_brightness)
        cv2.createTrackbar('R','dotty_as - Settings', self.red, 255, self.set_red)
        cv2.createTrackbar('G','dotty_as - Settings', self.green, 255, self.set_green)
        cv2.createTrackbar('B','dotty_as - Settings', self.blue, 255, self.set_blue)
        cv2.createTrackbar('Dot Type: Rectangle/Circle','dotty_as - Settings', self.shape, 1, self.set_shape)
        cv2.createTrackbar('Outline/Solid','dotty_as - Settings', self.filled, 1, self.set_filled)

    def set_virtualcam_enabled(self, x):
        self.virtualcam_enabled = x

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


    def open_settings(self, event, x, y, flags, param):
        if event:
            cv2.destroyWindow('dotty_as - Settings')
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
                    pass
                else:
                    virtualcam = pyfakewebcam.FakeWebcam('/dev/video2', 1280, 960)
            dottyFrame = np.zeros((960, 1280, 3), dtype=np.uint8)
            self.capture.set(cv2.CAP_PROP_CONTRAST, self.contrast)
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
            colour = (self.red, self.green, self.blue)
            ret, frame = self.capture.read() 
            if ret:
                greyFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dim = (128, 96)
                downFrame = cv2.resize(greyFrame, dim, interpolation=cv2.INTER_AREA)
                x = 0
                y = 0
                while y < 96:
                    while x < 128:
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