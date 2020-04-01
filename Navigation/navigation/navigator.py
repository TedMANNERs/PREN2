import numpy as np
from common.dataTypes import Vector

class Navigator:

    def __init__(self):
        pass
        
    def getNextTargetVector(self, detectedPylons):
        """
        Format of parameter 'detectedPylons':
        [('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px), distance)]
        The X and Y coordinates are from the center of the bounding box. Subtract half the width or height to get the lower corner.
        """
        
            #print(distance)
        return Vector(np.int16(10),np.int16(10))