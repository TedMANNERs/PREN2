import cv2
from camera.base_camera import BaseCamera

class CameraFake(BaseCamera):
    def getFrame(self):
        return cv2.imread("./imageDetection/pylon (527).jpg")