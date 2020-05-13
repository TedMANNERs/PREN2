import numpy as np
import logging
from common.dataTypes import TargetVector

class Navigator:
    VECTOR_STRAIGHT = TargetVector(np.int16(500),np.int16(0))
    VECTOR_TURN_LEFT_SLOW = TargetVector(np.int16(250),np.int16(-30))
    VECTOR_TURN_RIGHT_SLOW = TargetVector(np.int16(250),np.int16(30))
    MAX_SPEED = 500
    SPEED_INCREMENT = 1
    MAX_ANGLE = 60
    ANGLE_INCREMENT = 1
    
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

    def getNavigationTargetVector(self, detectedPylons, frame):
        """
        Format of parameter 'detectedPylons':
        [('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)]
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        nextPylon = self.getNextPylon(detectedPylons)
        if nextPylon:
            frame_width = frame.shape[0]
            xPosition = nextPylon[2][0]
            if xPosition < (frame_width / 4): # check if the next target pylon is in the left quarter of the frame
                return self._getMoveStraightVector()
            else:
                return self._getTurnRightVector()
        else:
            return self._getTurnLeftVector()

    def getSearchTargetVector(self):
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT, minValue=-30)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _getMoveStraightVector(self):
        logging.info("MOVE_STRAIGHT")
        if self.currentAngle < 0:
            self._updateCurrentAngle(self.currentAngle + self.ANGLE_INCREMENT, maxValue=0)
        else:
            self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT, minValue=0)
        self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        return TargetVector(np.int16(self.currentSpeed), np.int16(self.currentAngle))

    def _getTurnRightVector(self):
        logging.info("TURN_RIGHT")
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle + self.ANGLE_INCREMENT)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _getTurnLeftVector(self):
        logging.info("TURN_LEFT")
        newSpeed = self._updateCurrentSpeed(self.currentSpeed + self.SPEED_INCREMENT)
        newAngle = self._updateCurrentAngle(self.currentAngle - self.ANGLE_INCREMENT)
        return TargetVector(np.int16(newSpeed), np.int16(newAngle))

    def _updateCurrentSpeed(self, value, minValue = 0, maxValue = Navigator.MAX_SPEED):
        newSpeed = self._clamp(value, minValue, maxValue)
        self.currentSpeed = newSpeed
        return newSpeed

    def _updateCurrentAngle(self, value, minValue = 0 - Navigator.MAX_ANGLE, maxValue = Navigator.MAX_ANGLE):
        newAngle = self._clamp(value, minValue, maxValue)
        self.currentAngle = newAngle
        return newAngle

    def _clamp(self, value, minValue, maxValue):
        return max(min(value, maxValue), minValue)
