# dotty_as

dotty_as is a camera filter that converts your webcam to dots. It makes you dotty as...

It will output to a virtual camera device for video conferencing software to use as a webcam.

It also includes RGB colour control, colour randomization modes and different dot types including an ASCII luminance mode.

<img src="./sample%20images/sample_image.png" alt="sample_image" width="640"/>
<img src="./sample%20images/sample_image_ascii.png" alt="sample_image_ascii" width="640"/>

## Platform Feature Support

- Linux - all features. 

- Windows - does not have virtual camera output or camera capability detection.

- Mac - currently untested.

## Installation

### Pip Dependencies (All platforms)

`pip install pyqt5 opencv-python-headless pyvirtualcam`

### Linux(Ubuntu)

Install packages for camera capability detection and virtual camera output

`sudo apt install v4l2-utils v4l2loopback-utils`

Install virtual camera device

`sudo modprobe v4l2loopback devices=1`

## Usage

`python3 ./dotty_as.py`

## Notes on virtualcam and video conferencing software

Tested - Teams, Zoom, Skype

Be sure to turn the virtual camera output on before selecting it as a device from one of the above.

Teams seems to be picky about the resolution of virtual camera devices and works most reliably at 720p.