package main

import (
	"image"
	"image/color"
	"strconv"
	"time"

	"gocv.io/x/gocv"
)

const r = ".,-~:;=!*#$@"
var ascii_symbols []rune

func main() {
	webcam, err := gocv.OpenVideoCaptureWithAPI(0, 200)
	if err != nil {
		print(err)
	}
	webcam.Set(gocv.VideoCaptureFrameWidth, 1280)
	webcam.Set(gocv.VideoCaptureFrameHeight, 720)
	height := int(webcam.Get(gocv.VideoCaptureFrameHeight))
	width := int(webcam.Get(gocv.VideoCaptureFrameWidth))
	ascii_symbols = []rune(r)
	previewwindow := gocv.NewWindow("Hello")
	frame := gocv.NewMat()
	
	for {
		webcam.Read(&frame)
		dotify(webcam, &frame, previewwindow, height, width, ascii_symbols)
		if previewwindow.WaitKey(27) == 27 {
			break
		}
		previewwindow.ResizeWindow(width, height)
	}
}

func dotify(capture *gocv.VideoCapture, frame *gocv.Mat, window *gocv.Window, height int, width int, symbols []rune) {
	prev_frame_time := time.Now()
	canvas := gocv.Zeros(int(capture.Get(gocv.VideoCaptureFrameHeight)), int(capture.Get(gocv.VideoCaptureFrameWidth)), gocv.MatTypeCV8UC4)
	greyFrame := gocv.NewMat()
	gocv.CvtColor(*frame, &greyFrame, gocv.ColorBGRToGray)
	downFrame := gocv.NewMat()
	size := image.Point{X: width / 10, Y: height / 10}
	gocv.Resize(greyFrame, &downFrame, size, 0, 0, gocv.InterpolationArea)
	colour := color.RGBA{13, 188, 121, 255}
	for y := 0; y < downFrame.Rows(); y++ {
		for x := 0; x < downFrame.Cols(); x++ {
			sym := symbols[int(downFrame.GetUCharAt(y, x)/22)]
			bottom_left := image.Point{(x*10)+1, (y*10)+9}
			gocv.PutText(&canvas, string(sym), bottom_left, gocv.FontHersheyComplexSmall, .5, colour, 1)
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
}
