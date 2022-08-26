# dotty_as

dotty_as is a camera filter that converts your webcam to dots. It makes you dotty as...

## Feature Support

All features work on Linux. 

Windows does not have virtualcam output support or camera capability detection.

Mac is untested currently.

## Installation

### Pip Dependancies

`pip install pyqt5 opencv-python-headless pyvirtualcam`

### Linux(Ubuntu)

`sudo apt install v4l2-utils v4l2loopback-utils`

`sudo modprobe v4l2loopback devices=1`

## Usage

`python3 ./dotty_as.py`