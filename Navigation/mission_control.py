import cv2
import serial
import logging
import numpy as np
from communication.subscriber import Subscriber
from communication.lowLevelController import LowLevelController, CommandType, Command, AudioCommand, LEDCommand
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo
from camera.camera_factory import CameraFactory

class MissionControl(Subscriber):
    def __init__(self, lowLevelController: LowLevelController, navigator: Navigator, pylonDetector: PylonDetector, state_machine):
        self.lowLevelController = lowLevelController
        self.navigator = navigator
        self.pylonDetector = pylonDetector
        self.state_machine = state_machine

        self.nextPylon = None

        # Debug-Info
        self.latestFrame = None
        self.stateDiagram = None

    def initialize(self):
        # Init camera
        self.camera = CameraFactory.create()
        # Init YOLO
        self.pylonDetector.initialize()
        # Start listening for commands from the LLC
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(self)

    def start(self):
        logging.info("Starting Mission Control")
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)

    def search(self):
        frame = self.camera.getFrame()
        detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
        detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
        self.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)

        if __debug__:
            self._showDebugWindows()
        
        if detectedPylons:
            logging.debug(detectedPylons)
            self.nextPylon = self.navigator.getNextPylon(detectedPylons)
            self.state_machine.moveToPylon()

        targetVector = self.navigator.getNextTargetVector(self.nextPylon, self.latestFrame)
        #logging.debug(targetVector)
        self.lowLevelController.sendTargetVector(targetVector)

    def moveToNextPylon(self):
        #TODO: Move to next pylon, but how???
        pass

    def getDebugInfo(self):
        return DebugInfo(self.latestFrame)

    def stop(self):
        logging.info("Stopping Mission Control")
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)

    def abort(self):
        logging.info("Aborting...")
        self.stop()
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.stopListening()

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        logging.debug("MissionControl: Received command = %s", command)
        if command.commandType == CommandType.Start:
            self.state_machine.start()
        elif command.commandType == CommandType.SendSensorData:
            logging.info(command.data)
            #TODO: Implement handling of sensor data
            pass
        elif command.commandType == CommandType.Stop:
            self.state_machine.stop()
        else:
            raise ValueError("A command of type '{0}' should never be received!".format(command.commandType))

    def _showDebugWindows(self):
            cv2.imshow("Horwbot Image Detection", self.latestFrame)
            cv2.waitKey(1)
            graph = self.state_machine.model.get_graph()
            buffer = graph.pipe(format='png')
            nparr = np.fromstring(buffer, np.uint8)
            self.stateDiagram = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.namedWindow("Horwbot State Machine", cv2.WINDOW_NORMAL)
            cv2.imshow("Horwbot State Machine", self.stateDiagram)
            cv2.waitKey(1)