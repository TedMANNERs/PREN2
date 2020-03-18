import scipy
import numpy as np

class Vector:
    def __init__(self, x: np.int16, y: np.int16):
        self.x = x
        self.y = y
    
    def getLength(self):
        return np.sqrt(self.x ** 2 + self.y ** 2)