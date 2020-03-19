import serial
import numpy as np
from enum import Enum

class CommandType(Enum):
    Start = np.int8(0x01)
    SendTargetVector = np.int8(0x02)
    SendSensorData = np.int8(0x03)
    PlayAudio = np.int8(0x04)
    Stop = np.int8(0x05)

class AudioCommand(Enum):
    ShortBeep = np.int8(0x01)

#TODO: Refactor class, remove duplicate code
class LowLevelController:
    BIG_ENDIAN = ">"

    def __init__(self):
        self.serialPort = serial.Serial(baudrate=115200, timeout=1, write_timeout=1, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)
        self.serialPort.port = 'COM3' #TODO: Read COM-Port from config

    def sendTargetVector(self, targetVector):
        print("SendTargetVector: [{0}, {1}]".format(targetVector.x, targetVector.y))
        self.serialPort.open()
        command = CommandType.SendTargetVector.value.tobytes()
        command += targetVector.x.newbyteorder(self.BIG_ENDIAN).tobytes()
        command += targetVector.y.newbyteorder(self.BIG_ENDIAN).tobytes()
        self.serialPort.write(command)
        self.serialPort.close()

    def sendPlayAudio(self, audioCommand):
        print("SendPlayAudio: {0}".format(audioCommand))
        self.serialPort.open()
        command = CommandType.PlayAudio.value.tobytes()
        command += audioCommand.value.tobytes()
        self.serialPort.write(command)
        self.serialPort.close()

    def sendStop(self):
        print("SendStop")
        self.serialPort.open()
        command = CommandType.Stop.value.tobytes()
        self.serialPort.write(command)
        self.serialPort.close()