import os
import sys
import cv2
from camera.camera import Camera
from camera.camera_fake import CameraFake
from camera.camera_simulation import CameraSimulation

class CameraFactory:
    @staticmethod
    def create():
        if len(sys.argv) >= 2 and sys.argv[1] == "simulation":
            return CameraSimulation()

        cap = cv2.VideoCapture(0) # Use default camera (picamera on jetson, webcam on other devices)
        if cap is None or not cap.isOpened():
            print("Warning: Default camera was not found or could not be opened. Continuing with static image...")
            return CameraFake()
        else:
            return Camera(cap)
