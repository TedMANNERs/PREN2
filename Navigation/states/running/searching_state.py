import logging
import threading
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider

class SearchingState(NestedState):
    def __init__(self, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        super().__init__(name='searching', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self):
        self._do() #TODO: Refactor so that '_do' is called after the state has actually transitioned (otherwise 'after_state_change' won't be called)

    def _do(self):
        while(True):
            frame = CameraProvider.getCamera()
            detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
            detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
            DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)

            if __debug__:
                DebugInfo.showDebugWindows()
            
            if detectedPylons:
                logging.debug(detectedPylons)
                self.nextPylon = self.navigator.getNextPylon(detectedPylons)
                #self.state_machine.moveToPylon() #TODO: Figure out how to call the transition trigger

            targetVector = self.navigator.getNextTargetVector(self.nextPylon, frame_resized)
            #logging.debug(targetVector)
            self.lowLevelController.sendTargetVector(targetVector)

    def onExit(self):
        pass