# dotty_as

dotty_as is a camera filter that converts your webcam to dots. It makes you dotty as...

It includes some different dot types including an ASCII luminance mode.

![Sample Image](./sample%20images/sample_image.png =640x)
![Sample Image - ASCII](./sample%20images/sample_image_ascii.png =640x)

## Platform Feature Support

- Linux has all features. 

- Windows does not have virtual camera output support or camera capability detection.

- Mac is untested currently.

## Installation

### Pip Dependancies

`pip install pyqt5 opencv-python-headless pyvirtualcam`

### Linux(Ubuntu)

Install packages for camera capability detection and virtual camera output

`sudo apt install v4l2-utils v4l2loopback-utils`

Install virtual camera device

`sudo modprobe v4l2loopback devices=1`

## Usage

`python3 ./dotty_as.py`