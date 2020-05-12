import logging
import threading
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider

class SearchingState(NestedState):
    def __init__(self, parent, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        self.parent = parent
        super().__init__(name='searching', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self):
        self.parent.substate = self

    def loop(self):
        frame = CameraProvider.getCamera().getFrame()
        detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
        detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
        DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)

        if __debug__:
            DebugInfo.showLatestFrame()
        
        if detectedPylons:
            logging.debug(detectedPylons)
            self.nextPylon = self.navigator.getNextPylon(detectedPylons)
            self.parent.state_machine.moveToPylon()

        targetVector = self.navigator.getNextTargetVector(self.nextPylon, frame_resized)
        #logging.debug(targetVector)
        self.lowLevelController.sendTargetVector(targetVector)

    def onExit(self):
        pass