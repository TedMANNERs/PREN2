import cv2
import serial
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
from communication.subscriber import Subscriber
from communication.lowLevelController import LowLevelController, CommandType, Command
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo
from camera.camera_factory import CameraFactory

class MissionControl(Subscriber):
    def __init__(self, lowLevelController: LowLevelController, navigator: Navigator, pylonDetector: PylonDetector):
        self.lowLevelController = lowLevelController
        self.navigator = navigator
        self.pylonDetector = pylonDetector

        # Init camera
        self.camera = CameraFactory.create()

        # Start listening for commands from the LLC
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(self)

        #TODO: Replace booleans with state machine
        self.isMissionSuccessful = False #TODO: change to false when code is ready
        self.isMissionCancelled = False
        self.isMissionRunning = False

        # Debug-Info
        self.latestFrame = None

    def start(self):
        if self.isMissionRunning:
            logging.info("Mission is already running")
            return
            
        logging.info("Starting Mission Control")
        #selfTest.run()
        self.isMissionCancelled = False
        self.isMissionRunning = True
        self.__runMission()

    def __runMission(self):
        logging.info("Mission is running")
        while not self.isMissionSuccessful:
            if self.isMissionCancelled:
                logging.info("Mission was cancelled!")
                self.isMissionRunning = False
                return
            
            frame = self.camera.getFrame()
            detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
            if detectedPylons:
                detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
                logging.info(detectedPylons)
            
            self.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)
            
            targetVector = self.navigator.getNextTargetVector(detectedPylons, frame_resized)
            #logging.info(targetVector)
            try:
                self.lowLevelController.sendTargetVector(targetVector)
            except serial.SerialTimeoutException as serialError:
                print(serialError)
                self.stop()

            #self.isMissionSuccessful = True # Remove to loop

        logging.info("Mission was successful!")

    def getDebugInfo(self):
        return DebugInfo(self.latestFrame)

    def stop(self):
        logging.info("Stopping Mission Control")
        self.isMissionCancelled = True

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        #print("MissionControl: Received command = {0}".format(command))
        logging.info("MissionControl: Received command = %s", command)
        if command.commandType == CommandType.Start:
            self.start()
        elif command.commandType == CommandType.SendSensorData:
            logging.info(command.data)
            #TODO: Implement handling of sensor data
            pass
        elif command.commandType == CommandType.Stop:
            self.stop()
        else:
            raise ValueError("A command of type '{0}' should never be received!".format(command.commandType))