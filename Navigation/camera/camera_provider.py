import os
import sys
import cv2
import logging
from camera.camera import Camera
from camera.camera_fake import CameraFake
from camera.camera_simulation import CameraSimulation

class CameraProvider:
    _camera = None

    @staticmethod
    def initialize(isSimulation: bool):
        if isSimulation:
            CameraProvider._camera = CameraSimulation()
        else:
            cap = cv2.VideoCapture(0) # Use default camera (picamera on jetson, webcam on other devices)
            if cap is None or not cap.isOpened():
                logging.warning("Warning: Default camera was not found or could not be opened. Continuing with static image...")
                CameraProvider._camera = CameraFake()
            else:
                CameraProvider._camera = Camera(cap)
    
    @staticmethod
    def getCamera():
        return CameraProvider._camera