import scipy
import numpy as np

class Vector:
    def __init__(self, x: np.int16, y: np.int16):
        self.__vector = np.array([x, y], dtype=">i2")

    def getX(self):
        return self.__vector[0]

    def getY(self):
        return self.__vector[1]
    
    def getLength(self):
        return np.sqrt(self.__vector[0] ** 2 + self.__vector[1] ** 2)

    x = property(getX)
    y = property(getY)