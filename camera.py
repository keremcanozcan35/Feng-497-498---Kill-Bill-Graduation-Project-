from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (1280,1280)
sleep(2)
camera.awb_mode = "fluorescent"
#camera.start_preview()
sleep(8)
camera.capture("/tmp/picture3.jpg",format="jpeg",quality=100)
#camera.stop_preview()