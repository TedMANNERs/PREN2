import numpy as np
import logging
from common.dataTypes import TargetVector
from common.timer import Timer
from configreader import parser

class Navigator:
    FORWARD_SPEED = int(parser.get("navigation_variables", "FORWARD_SPEED"))
    REVERSE_SPEED = int(parser.get("navigation_variables", "REVERSE_SPEED"))
    SPEED_INCREMENT = int(parser.get("navigation_variables", "SPEED_INCREMENT"))
    MAX_ANGLE_LEFT = int(parser.get("navigation_variables", "MAX_ANGLE_LEFT"))
    MAX_ANGLE_RIGHT = int(parser.get("navigation_variables", "MAX_ANGLE_RIGHT"))
    ANGLE_INCREMENT = int(parser.get("navigation_variables", "ANGLE_INCREMENT"))
    
    def __init__(self):
        self.currentSpeed = 0
        self.currentAngle = 0
        
    def getNextPylon(self, detectedPylons):
        """
        Format of parameter 'detectedPylons':
        [('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)]
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        index = np.argmax([x[2][0] for x in detectedPylons]) #Get index of the detected object with the largest 'bounding_box_x_px'
        rightmost_nearest_pylon = detectedPylons[index]
        logging.debug("Rightmost Nearest Pylon = {0}, Index = {1}".format(rightmost_nearest_pylon, index))
        return rightmost_nearest_pylon

    def getNavigationTargetVector(self, detectedPylons, frame, timer: Timer):
        """
        Format of parameter 'detectedPylons':
        [('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)]
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        if not detectedPylons:
            if timer.getElapsedTime() > 1:
                return self._getTurnLeftVector()
            else:
                return self._getMoveStraightVector()

        nextPylon = self.getNextPylon(detectedPylons)
        frame_width = frame.shape[0]
        xPosition = nextPylon[2][0]
        distance = nextPylon[3]
        fraction_of_frame_width = 3
        if distance < 2000: # 2000mm
            fraction_of_frame_width = 5
        if xPosition < (frame_width / fraction_of_frame_width): # check if the next target pylon is in the left 'fraction' of the frame
            return self._getMoveStraightVector()
        else:
            return self._getTurnRightVector()

    def getSearchTargetVector(self):
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT, minValue=-30)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _getMoveStraightVector(self):
        if self.currentAngle < 0:
            self._updateCurrentAngle(self.currentAngle + self.ANGLE_INCREMENT, maxValue=0)
        else:
            self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT, minValue=0)
        self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        logging.info("MOVE_STRAIGHT: Speed=%s", self.currentSpeed)
        return TargetVector(np.int16(self.currentSpeed), np.int16(self.currentAngle))

    def _getReverseVector(self):
        if self.currentAngle < 0:
            self._updateCurrentAngle(self.currentAngle + self.ANGLE_INCREMENT, maxValue=0)
        else:
            self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT, minValue=0)
        self._updateCurrentSpeed(self.currentSpeed - self.SPEED_INCREMENT, minValue=self.REVERSE_SPEED)
        logging.info("MOVE_STRAIGHT: Speed=%s", self.currentSpeed)
        return TargetVector(np.int16(self.currentSpeed), np.int16(self.currentAngle))

    def _getTurnRightVector(self):
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle + self.ANGLE_INCREMENT)
        logging.info("TURN_RIGHT: Speed=%s, Angle=%s", self.currentSpeed, self.currentAngle)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _getTurnLeftVector(self):
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT)
        logging.info("TURN_LEFT: Speed=%s, Angle=%s", self.currentSpeed, self.currentAngle)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _updateCurrentSpeed(self, value, minValue = 0, maxValue = None):
        if maxValue is None:
            maxValue = self.FORWARD_SPEED

        newSpeed = self._clamp(value, minValue, maxValue)
        self.currentSpeed = newSpeed
        return newSpeed

    def _updateCurrentAngle(self, value, minValue = None, maxValue = None):
        if minValue is None:
            minValue = self.MAX_ANGLE_LEFT
        if maxValue is None:
            maxValue = self.MAX_ANGLE_RIGHT

        newAngle = self._clamp(value, minValue, maxValue)
        self.currentAngle = newAngle
        return newAngle

    def _clamp(self, value, minValue, maxValue):
        return max(min(value, maxValue), minValue)
