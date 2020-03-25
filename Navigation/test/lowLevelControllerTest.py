import unittest
import serial
import numpy as np
from communication.subscriber import Subscriber
from communication.lowLevelController import LowLevelController, CommandType, Command
from common.dataTypes import Vector

class DummySubscriber(Subscriber):
    def __init__(self):
        self.result = None

    def onCommandReceived(self, command):
        print(command)
        self.result = command

class LowLevelControllerTest(unittest.TestCase):
    def setUp(self):
        self.testee = LowLevelController()

    def test_send(self):
        #arrange
        targetVector = Vector(np.int16(24000), np.int16(10))
        ser = serial.Serial('COM4', baudrate=115200, timeout=1, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)
        
        #act
        self.testee.sendTargetVector(targetVector)
        
        #assert
        commandType = np.fromstring(ser.read(1), dtype=np.int8)
        x = np.fromstring(ser.read(2), dtype=">i2")
        y = np.fromstring(ser.read(2), dtype=">i2")
        self.assertEqual(commandType, CommandType.SendTargetVector.value)
        self.assertEqual(x, 24000)
        self.assertEqual(y, 10)
        ser.close()
        
    def test_receive(self):
        #arrange
        self.testee.startListening()
        expectedCommand = Command(CommandType.SendSensorData, np.array([10,160,2560,11,176,12,192], dtype=">i2"))
        dummy = DummySubscriber()
        self.testee.subscribe(dummy)
        ser = serial.Serial('COM4', baudrate=115200, timeout=1, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)
        
        #act
        ser.write(bytearray.fromhex("03000A00A00A00000B00B0000C00C0"))
        
        #assert
        while dummy.result is None:
            pass
        self.assertEqual(dummy.result.commandType, expectedCommand.commandType)
        np.testing.assert_array_equal(dummy.result.data, expectedCommand.data)
        self.testee.stopListening()
        ser.close()

#TODO: Add more tests


if __name__ == '__main__':
    unittest.main()