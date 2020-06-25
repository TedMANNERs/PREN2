# Modified code taken from 'darknet_video.py' of darknet (https://github.com/AlexeyAB/darknet) by pjreddie and AlexeyAB
import os,sys,inspect
import cv2
import numpy as np
from enum import Enum
from imageDetection import darknet
from configreader import parser

netMain = None # used in module 'darknet.py'
metaMain = None # used in module 'darknet.py'

class Label(Enum):
    Pylon = "pylon".encode()
    LyingPylon = "lyingPylon".encode()
    Obstacle = "obstacle".encode()

class PylonDetector():
    CONFIG_PATH = parser.get("paths", "CONFIG_PATH")
    WEIGHT_PATH = parser.get("paths", "WEIGHT_PATH")
    META_PATH = parser.get("paths", "META_PATH")
    DETECTION_THRESHOLD = float(parser.get("variables", "DETECTION_THRESHOLD"))
    FOCAL_LENGTH_MM = float(parser.get("focal_length", "FOCAL_LENGTH_MM_LINUX"))
    SENSOR_HEIGHT_MM = float(parser.get("variables", "SENSOR_HEIGHT_MM"))
    PYLON_HEIGHT_MM = int(parser.get("variables", "PYLON_HEIGHT_MM"))
    LYING_PYLON_HEIGHT_MM = int(parser.get("variables", "LYING_PYLON_HEIGHT_MM"))
    OBSTACLE_REAL_HEIGHT_MM = int(parser.get("variables", "OBSTACLE_HEIGHT_MM"))

    def __init__(self):
        if os.name == "nt": # Windows
            self.FOCAL_LENGTH_MM = float(parser.get("focal_length", "FOCAL_LENGTH_MM_WINDOWS"))

        if not os.path.exists(self.CONFIG_PATH):
            raise ValueError("Invalid config path `{0}`".format(os.path.abspath(self.CONFIG_PATH)))
        if not os.path.exists(self.WEIGHT_PATH):
            raise ValueError("Invalid weight path `{0}`".format(os.path.abspath(self.WEIGHT_PATH)))
        if not os.path.exists(self.META_PATH):
            raise ValueError("Invalid data file path `{0}`".format(os.path.abspath(self.META_PATH)))

    def initialize(self):
        global metaMain, netMain
        if netMain is None:
            netMain = darknet.load_net_custom(self.CONFIG_PATH.encode("ascii"), self.WEIGHT_PATH.encode("ascii"), 0, 1)  # batch size = 1
        if metaMain is None:
            metaMain = darknet.load_meta(self.META_PATH.encode("ascii"))
        self.darknet_image = darknet.make_image(darknet.network_width(netMain), darknet.network_height(netMain),3)

    def findObjects(self, path):
        """
        Returns a tupple with the following format:
        ('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px))
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame_resized = cv2.resize(frame_rgb,
        #                           (darknet.network_width(netMain),
        #                            darknet.network_height(netMain)),
        #                           interpolation=cv2.INTER_LINEAR)

        #darknet.copy_image_from_bytes(self.darknet_image,frame_resized.tobytes())

        detections = darknet.detect(netMain, metaMain, path.encode("ascii"), thresh=self.DETECTION_THRESHOLD)
        #frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        return detections

    def calculateDistance(self, detection, frame_resized):
        """
        Format of parameter 'detection':
        ('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        object_height = 0
        if detection[0] == Label.Pylon.value:
            object_height = self.PYLON_HEIGHT_MM
        elif detection[0] == Label.LyingPylon.value:
            object_height = self.LYING_PYLON_HEIGHT_MM
        elif detection[0] == Label.Obstacle.value:
            object_height = self.OBSTACLE_REAL_HEIGHT_MM

        distance = (self.FOCAL_LENGTH_MM * object_height * frame_resized.shape[1]) / (detection[2][3] * self.SENSOR_HEIGHT_MM)
        detection += (distance,)
        return detection

    def drawBox(self, detection, frame):
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = self.__convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)

        colorArray = [0, 255, 0]
        colorTuple = (0, 255, 0)
        if detection[0] == Label.LyingPylon.value:
            colorArray = [0, 0, 255]
            colorTuple = (0, 0, 255)
        elif detection[0] == Label.Obstacle.value:
            colorArray = [255, 0, 0]
            colorTuple = (255, 0, 0)

        cv2.rectangle(frame, pt1, pt2, colorTuple, 3)
        cv2.putText(frame,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]", #TODO: Document what the values mean, potentally refactor
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    colorArray, 3)
        cv2.putText(frame,
                    "dist={0}mm".format(int(detection[3])),
                    (pt1[0], pt1[1] - 60), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    colorArray, 3)
        return frame

    def __convertBack(self, x, y, w, h):
        xmin = int(round(x - (w / 2)))
        xmax = int(round(x + (w / 2)))
        ymin = int(round(y - (h / 2)))
        ymax = int(round(y + (h / 2)))
        return xmin, ymin, xmax, ymax
