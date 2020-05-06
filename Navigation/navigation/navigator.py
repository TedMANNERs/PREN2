import numpy as np
import logging
from common.dataTypes import TargetVector

class Navigator:
    VECTOR_STRAIGHT = TargetVector(np.int16(500),np.int16(0))
    VECTOR_TURN_LEFT_SLOW = TargetVector(np.int16(250),np.int16(-30))
    VECTOR_TURN_RIGHT_SLOW = TargetVector(np.int16(250),np.int16(30))

    def __init__(self):
        self._targetVector = self.VECTOR_STRAIGHT
        pass
        
    def getNextTargetVector(self, detectedPylons, frame):
        """
        Format of parameter 'detectedPylons':
        [('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)]
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        standingPylons = list(filter(lambda x: x[0].decode("utf-8") == "pylon", detectedPylons))
        if standingPylons:
            index = np.argmax([x[2][0] for x in standingPylons])
            rightmost_nearest_pylon = standingPylons[index]
            print("Rightmost Nearest Pylon = {0}, Index = {1}".format(rightmost_nearest_pylon, index))
            frame_width = frame.shape[0]
            if rightmost_nearest_pylon[2][0] < (frame_width / 4): # check if the rightmost nearest pylon is in the left quarter of the frame
                self._targetVector = self.VECTOR_STRAIGHT
                logging.info("STRAIGHT")
            else:
                self._targetVector = self.VECTOR_TURN_RIGHT_SLOW
                logging.info("TURN_RIGHT_SLOW")
        else:
            self._targetVector = self.VECTOR_TURN_LEFT_SLOW
            logging.info("TURN_LEFT_SLOW")

        return self._targetVector
