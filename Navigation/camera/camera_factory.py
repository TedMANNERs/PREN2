import os
import cv2
from camera.camera import Camera # shows error but works?!?
from camera.camera_fake import CameraFake # shows error but works?!?

class CameraFactory:
    @staticmethod
    def create():
        cap = cv2.VideoCapture(0) # Use default camera (picamera on jetson, webcam on other devices)
        if cap is None or not cap.isOpened():
            print("Warning: Default camera was not found or could not be opened. Continuing with static image...")
            return CameraFake()
        else:
            return Camera(cap)
