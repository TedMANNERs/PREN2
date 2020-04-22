import threading
import serial
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
import numpy as np
from enum import Enum
from time import sleep

class CommandType(Enum):
    Start = np.int8(0x01)
    SendTargetVector = np.int8(0x02)
    SendSensorData = np.int8(0x03)
    PlayAudio = np.int8(0x04)
    Stop = np.int8(0x05)
    Led = np.int8(0xF0)

class AudioCommand(Enum):
    ShortBeep = np.int8(0x01)
    LongBeep = np.int8(0x02)

class LEDCommand(Enum):
    Off = np.int8(0x00)
    On = np.int8(0x01)

class Command:
    def __init__(self, commandType: CommandType, data=None):
        self.commandType = commandType
        self.data = data

    def __str__(self):
        return "{0} - {1}".format(self.commandType, self.data)

#TODO: Refactor class, remove duplicate code
class LowLevelController:
    BIG_ENDIAN = ">"
    COMMAND_TYPE_SIZE = 1
    INT_16_SIZE = 2
    INT_16_DTYPE = "{0}i{1}".format(BIG_ENDIAN, INT_16_SIZE)

    def __init__(self):
        self.serialPort = serial.Serial(baudrate=115200, timeout=1, write_timeout=1, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE)
        self.serialPort.port = 'COM3' #TODO: Read COM-Port from config
        self._subscribers = set()
        self._listenerThread = threading.Thread(target=self._listen)
        self._isListening = False

    def startListening(self):
        self._isListening = True
        self._listenerThread.start()
        logging.info("Listener thread started")

    def stopListening(self):
        self._isListening = False

    def sendTargetVector(self, targetVector):
        logging.info("SendTargetVector: [%s, %s]", targetVector.x, targetVector.y)
        #self.serialPort.open()
        command = CommandType.SendTargetVector.value.tobytes()
        command += targetVector.speed.newbyteorder(self.BIG_ENDIAN).tobytes()
        command += targetVector.angle.newbyteorder(self.BIG_ENDIAN).tobytes()
        self.serialPort.write(command)
        #self.serialPort.close()

    def sendPlayAudio(self, audioCommand: AudioCommand):
        #print("SendPlayAudio: {0}".format(audioCommand))
        logging.info("SendPlayAudio: %s", audioCommand)
        #self.serialPort.open()
        command = CommandType.PlayAudio.value.tobytes()
        command += audioCommand.value.tobytes()
        self.serialPort.write(command)
        #self.serialPort.close()

    def sendStop(self):
        logging.info("SendStop")
        #self.serialPort.open()
        command = CommandType.Stop.value.tobytes()
        self.serialPort.write(command)
        #self.serialPort.close()

    def sendLED(self, ledCommand: LEDCommand):
        logging.info("SendLED")
        #self.serialPort.open()
        command = CommandType.Led.value.tobytes()
        command += ledCommand.value.tobytes()
        self.serialPort.write(command)
        #self.serialPort.close()

    def subscribe(self, subscriber):
        subscriber._publisher = self
        self._subscribers.add(subscriber)

    def unsubscribe(self, subscriber):
        subscriber._publisher = None
        self._subscribers.discard(subscriber)

    def _listen(self):
        self.serialPort.open()
        while self._isListening:
            commandTypeData = self.serialPort.read(self.COMMAND_TYPE_SIZE)
            if len(commandTypeData) <= 0:
                sleep(0.1)
                continue
            try:
                commandType = CommandType(np.fromstring(commandTypeData, dtype=">i1"))
            except ValueError:
                #print("'{0}' is not a valid CommandType".format(commandTypeData))
                logging.warning("%s is not a valid CommandType", commandTypeData)
                continue
            if commandType == CommandType.Start:
                logging.info("Start received")
                self._notify(Command(commandType))
            elif commandType == CommandType.Stop:
                logging.info("Stop received")
                self._notify(Command(commandType))
            elif commandType == CommandType.SendSensorData:
                logging.info("SendSensorData received")
                sensorData = self._readSensorData()
                self._notify(Command(commandType, sensorData))
        self.serialPort.close()
        logging.info("Listener thread stopped")
    
    def _readSensorData(self):
        #read IMU
        xData = self.serialPort.read(self.INT_16_SIZE)
        yData = self.serialPort.read(self.INT_16_SIZE)
        zData = self.serialPort.read(self.INT_16_SIZE)
        x = np.fromstring(xData, dtype=self.INT_16_DTYPE)
        y = np.fromstring(yData, dtype=self.INT_16_DTYPE)
        z = np.fromstring(zData, dtype=self.INT_16_DTYPE)

        #read encoder
        leftEncoderData = self.serialPort.read(self.INT_16_SIZE)
        rightEncoderData = self.serialPort.read(self.INT_16_SIZE)
        leftEncoder = np.fromstring(leftEncoderData, dtype=self.INT_16_DTYPE)
        rightEncoder = np.fromstring(rightEncoderData, dtype=self.INT_16_DTYPE)

        #read range finder
        straightDistanceData = self.serialPort.read(self.INT_16_SIZE)
        angledDistanceData = self.serialPort.read(self.INT_16_SIZE)
        straightDistance = np.fromstring(straightDistanceData, dtype=self.INT_16_DTYPE)
        angledDistance = np.fromstring(angledDistanceData, dtype=self.INT_16_DTYPE)
        return np.concatenate((x, y, z, leftEncoder, rightEncoder, straightDistance, angledDistance))

    def _notify(self, command):
        for subscriber in self._subscribers:
            subscriber.onCommandReceived(command)