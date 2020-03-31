import cv2
from communication.subscriber import Subscriber
from communication.lowLevelController import LowLevelController, CommandType, Command
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo

class MissionControl(Subscriber):
    def __init__(self, lowLevelController: LowLevelController, navigator: Navigator, pylonDetector: PylonDetector):
        self.lowLevelController = lowLevelController
        self.navigator = navigator
        self.pylonDetector = pylonDetector

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
            print("Mission is already running")
            return
            
        print("Starting Mission Control")
        #selfTest.run()
        self.isMissionRunning = True
        self.__runMission()

    def __runMission(self):
        print("Mission is running")
        while not self.isMissionSuccessful:
            if self.isMissionCancelled:
                print("Mission was cancelled!")
                self.isMissionRunning = False
                return
            
            frame = cv2.imread("./imageDetection/pylon (527).jpg") #TODO: Replace static image with actual camera image
            detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
            print(detectedPylons)
            self.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)

            #targetVector = self.navigator.getNextTargetVector()
            #print(targetVector)
            #self.lowLevelController.sendTargetVector(targetVector)
            self.isMissionSuccessful = True

        print("Mission was successful!")

    def getDebugInfo(self):
        return DebugInfo(self.latestFrame)

    def stop(self):
        print("Stopping Mission Control")
        self.isMissionCancelled = True
        self.lowLevelController.stopListening()

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        print("MissionControl: Received command = {0}".format(command))
        if command.commandType == CommandType.Start:
            self.start()
        elif command.commandType == CommandType.SendSensorData:
            #TODO: Implement handling of sensor data
            pass
        elif command.commandType == CommandType.Stop:
            self.stop()
        else:
            raise ValueError("A command of type '{0}' should never be received!".format(command.commandType))