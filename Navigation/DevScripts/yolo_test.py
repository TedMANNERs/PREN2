import logging
import os,sys,time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import numpy as np
import cv2
from imageDetection.pylonDetector_screenshot_test import PylonDetector, Label

detector = PylonDetector()
detector.initialize()
path = input("Enter image path: ")
frame = cv2.imread(path)
detections = detector.findObjects(path)
for detection in detections:
    detection = detector.calculateDistance(detection, frame)
    frame = detector.drawBox(detection, frame)

cv2.imshow("yolo test", frame)
cv2.waitKey(1)
cv2.imwrite("yolotest.jpg", frame)
#while True:
#    cv2.waitKey(1)