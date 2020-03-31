# Modified code taken from 'darknet_video.py' of darknet (https://github.com/AlexeyAB/darknet) by pjreddie and AlexeyAB
import os
import cv2
import numpy as np
from imageDetection import darknet

netMain = None # used in module 'darknet.py'
metaMain = None # used in module 'darknet.py'

class PylonDetector():
    
    CONFIG_PATH = "./imageDetection/yolov3-tiny-pylon.cfg"
    WEIGHT_PATH = "./imageDetection/yolov3-tiny-pylon_13000.weights" # Download from OneDrive
    META_PATH = "./imageDetection/pylon.data"
    DETECTION_THRESHOLD = 0.25 # TODO: read from config file

    def __init__(self):
        global metaMain, netMain
        if not os.path.exists(self.CONFIG_PATH):
            raise ValueError("Invalid config path `{0}`".format(os.path.abspath(self.CONFIG_PATH)))
        if not os.path.exists(self.WEIGHT_PATH):
            raise ValueError("Invalid weight path `{0}`".format(os.path.abspath(self.WEIGHT_PATH)))
        if not os.path.exists(self.META_PATH):
            raise ValueError("Invalid data file path `{0}`".format(os.path.abspath(self.META_PATH)))

        if netMain is None:
            netMain = darknet.load_net_custom(self.CONFIG_PATH.encode("ascii"), self.WEIGHT_PATH.encode("ascii"), 0, 1)  # batch size = 1
        if metaMain is None:
            metaMain = darknet.load_meta(self.META_PATH.encode("ascii"))
        self.darknet_image = darknet.make_image(darknet.network_width(netMain), darknet.network_height(netMain),3)

    def findPylons(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(self.darknet_image,frame_resized.tobytes())

        detections = darknet.detect_image(netMain, metaMain, self.darknet_image, thresh=self.DETECTION_THRESHOLD)
        return detections, frame_resized

    def drawBoxes(self, detections, frame):
        for detection in detections:
            x, y, w, h = detection[2][0],\
                detection[2][1],\
                detection[2][2],\
                detection[2][3]
            xmin, ymin, xmax, ymax = self.__convertBack(
                float(x), float(y), float(w), float(h))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 1)
            cv2.putText(frame,
                        detection[0].decode() +
                        " [" + str(round(detection[1] * 100, 2)) + "]", #TODO: Document what the values mean, potentally refactor
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def __convertBack(self, x, y, w, h):
        xmin = int(round(x - (w / 2)))
        xmax = int(round(x + (w / 2)))
        ymin = int(round(y - (h / 2)))
        ymax = int(round(y + (h / 2)))
        return xmin, ymin, xmax, ymax
