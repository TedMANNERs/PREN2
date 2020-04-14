import scipy
import numpy as np

class TargetVector:
    def __init__(self, speed: np.int16, angle: np.int16):
        self.__vector = np.array([speed, angle], dtype=">i2") #TODO: replace array with variables

    def getSpeed(self):
        return self.__vector[0]

    def getAngle(self):
        return self.__vector[1]

    def __str__(self):
        return "TargetVector(Speed={0}, Angle={1})".format(self.__vector[0], self.__vector[1])

    speed = property(getSpeed)
    angle = property(getAngle)
