package main

import (
	"image"
	"image/color"
	"strconv"
	"time"

	"gocv.io/x/gocv"
)

func main() {
	webcam, _ := gocv.OpenVideoCapture(0)
	webcam.Set(gocv.VideoCaptureFrameWidth, 640)
	webcam.Set(gocv.VideoCaptureFrameHeight, 480)
	height := int(webcam.Get(gocv.VideoCaptureFrameHeight))
	width := int(webcam.Get(gocv.VideoCaptureFrameWidth))
	previewwindow := gocv.NewWindow("Hello")
	frame := gocv.NewMat()
	for {
		dotify(webcam, frame, previewwindow, height, width)
		if previewwindow.WaitKey(27) == 27 {
			break
		}
	}
}

func dotify(capture *gocv.VideoCapture, frame gocv.Mat, window *gocv.Window, height int, width int) {
	prev_frame_time := time.Now()
	capture.Read(&frame)
	canvas := gocv.Zeros(int(capture.Get(gocv.VideoCaptureFrameHeight)), int(capture.Get(gocv.VideoCaptureFrameWidth)), gocv.MatTypeCV8UC4)
	greyFrame := gocv.NewMat()
	gocv.CvtColor(frame, &greyFrame, gocv.ColorBGRToGray)
	downFrame := gocv.NewMat()
	size := image.Point{X: width / 10, Y: height / 10}
	gocv.Resize(greyFrame, &downFrame, size, 0, 0, gocv.InterpolationArea)
	colour := color.RGBA{13, 188, 121, 255}
	for y := 0; y < downFrame.Rows(); y++ {
		for x := 0; x < downFrame.Cols(); x++ {
			rectsize := int(downFrame.GetUCharAt(y, x) / 32)
			rectDims := image.Rect((x*10)+1, (y*10)+1, (x*10)+rectsize, (y*10)+rectsize)
			gocv.Rectangle(&canvas, rectDims, colour, 1)
		}
	}
	font := gocv.FontHersheyComplex
	new_frame_time := time.Now()
	fps := int(1 / (time.Since(prev_frame_time).Seconds()))
	prev_frame_time = new_frame_time
	text := strconv.Itoa(fps)
	position := image.Point{X: 40, Y: 80}
	white := color.RGBA{255, 255, 255, 255}
	gocv.PutText(&canvas, text, position, font, 2, white, 3)
	window.IMShow(canvas)
	window.ResizeWindow(width, height)
}
