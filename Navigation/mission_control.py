import serial
import logging
from communication.subscriber import Subscriber
from communication.usb import Usb
from communication.lowLevelController import LowLevelController, CommandType, Command, AudioCommand, LEDCommand
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo
from camera.camera_factory import CameraFactory
from debugGui.webserver import Webserver
from horwbot_state_machine import HorwbotStateMachine

class MissionControl(Subscriber):
    def __init__(self, lowLevelController: LowLevelController, navigator: Navigator, pylonDetector: PylonDetector, state_machine: HorwbotStateMachine):
        self.lowLevelController = lowLevelController
        self.navigator = navigator
        self.pylonDetector = pylonDetector
        self.state_machine = state_machine

        self.nextPylon = None

    def initialize(self):
        # Init camera
        self.camera = CameraFactory.create()
        # Init YOLO
        self.pylonDetector.initialize()
        # Start listening for commands from the LLC
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(self)
        if Usb.hasWifiDongle():
            self.webserver = Webserver(self)
            self.webserver.start()
        self.state_machine.initialized()

    def start(self):
        logging.info("Starting Mission Control")
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)

    def search(self):
        frame = self.camera.getFrame()
        detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
        detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
        DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)

        if __debug__:
            DebugInfo.showDebugWindows()
        
        if detectedPylons:
            logging.debug(detectedPylons)
            self.nextPylon = self.navigator.getNextPylon(detectedPylons)
            self.state_machine.moveToPylon()

        targetVector = self.navigator.getNextTargetVector(self.nextPylon, frame_resized)
        #logging.debug(targetVector)
        self.lowLevelController.sendTargetVector(targetVector)

    def moveToNextPylon(self):
        #TODO: Move to next pylon, but how???
        pass

    def stop(self):
        logging.info("Stopping Mission Control")
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)
        self.state_machine.stop()

    def abort(self):
        logging.info("Aborting...")
        self.stop()
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.stopListening()
        self.state_machine.abort()

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        logging.debug("MissionControl: Received command = %s", command)
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
