import unittest
import serial
import numpy as np
from communication.lowLevelController import LowLevelController, CommandType
from common.dataTypes import Vector

class LowLevelControllerTest(unittest.TestCase):
    def setUp(self):
        self.testee = LowLevelController()

    def test_send(self):
        #arrange
        targetVector = Vector(np.int16(24000), np.int16(10))
        ser =  serial.Serial('COM4', baudrate=115200, timeout=1, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)
        
        #act
        self.testee.sendTargetVector(targetVector)
        
        #assert
        commandType = np.fromstring(ser.read(1), dtype=np.int8)
        x = np.fromstring(ser.read(2), dtype=np.int16)
        y = np.fromstring(ser.read(2), dtype=np.int16)
        self.assertEqual(commandType, CommandType.SendTargetVector.value)
        self.assertEqual(x, 24000)
        self.assertEqual(y, 10)
        ser.close()


if __name__ == '__main__':
    unittest.main()