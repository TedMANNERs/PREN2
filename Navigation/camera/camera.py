import cv2
from camera.base_camera import BaseCamera # shows error but works?!?

class Camera(BaseCamera):
    def __init__(self, videoCapture: cv2.VideoCapture):
        self.videoCapture = videoCapture

    def getFrame(self):
        _, frame = self.videoCapture.read()
        return frame